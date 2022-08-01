import pickle
from datetime import datetime
from typing import List, Union, Iterable

import pydash
import pytest
from _pytest.outcomes import Skipped
from pytest import ExitCode, Config, Session, Mark, Item, TestReport, CallInfo

from .config import TrConfig
from .constants import TR_MARKER_NAME, TR_PASSED_TESTS_FLUSH_SIZE, TestrailStatus, \
    PytestStatus, TESTRAIL_STATUS_PRIORITY, PYTEST_TO_TESTRAIL_STATUS, TestrailMsgStyle
from .dto import ReportDTO
from .service import TrService

WORKER_RESULTS_KEY = 'tr_results'


def tr_case(case_id: Union[str, int]):
    return pytest.mark.case(case_id)


def is_master(config: Config) -> bool:
    """
    True if the code running the given pytest.config object is
    running in a xdist master node or not running xdist at all.
    """
    return not hasattr(config, 'workerinput')


class TrClient:
    def __init__(self, config):
        self._service: TrService = config.tr_service
        self._config = config
        self._tr_config: TrConfig = config.tr_config
        self._results: List[ReportDTO] = []
        self._passed_tests_count = 0

    def add_results(self, results: Iterable[ReportDTO]) -> None:
        self._results.extend(results)

    def pytest_collection_modifyitems(self, session: Session, config: Config, items: List[Item]):
        """Select tests containing in testrail test run only."""
        cond = (self._service.is_test_run_available(), self._tr_config.deselect_tests)
        if not all(cond):
            return

        tr_run_cases = self._service.get_cases()
        deselected, selected = [], []

        for item in items:
            marker = item.get_closest_marker(TR_MARKER_NAME)
            if not marker:
                deselected.append(item)
                continue

            case_id = self._get_marker_case_id(marker)
            if case_id not in tr_run_cases:
                deselected.append(item)
            else:
                selected.append(item)
        items[:] = selected

        config.hook.pytest_deselected(items=deselected)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item: Item, call: CallInfo):
        result: TestReport = (yield).get_result()
        marker = item.get_closest_marker(TR_MARKER_NAME)
        cond = (call.when == 'call', result.outcome == 'skipped')
        if not marker or not any(cond):
            return

        case_id = self._get_marker_case_id(marker)

        report = ReportDTO(
            item.name,
            item.nodeid,
            self.__get_pytestrail_status(call),
            result.duration,
            result.longrepr,
            case_id,
            self.__is_parametrized_test(item.own_markers)
        )

        self._results.append(report)

        if report.status == PytestStatus.PASSED:
            self._passed_tests_count += 1

        # Try to flush passed results per node
        self._try_flush_reports()

    @staticmethod
    def _get_marker_case_id(marker):
        case = marker.args[0]
        if isinstance(case, str):
            case = case.lower().replace('c', '')
        case_id = int(case)
        return case_id

    def _try_flush_reports(self):
        if self._service.is_test_run_available() and \
                self._passed_tests_count > TR_PASSED_TESTS_FLUSH_SIZE:
            self._send_passed_reports(self._results)
            self._passed_tests_count = 0

    @staticmethod
    def __get_pytestrail_status(call: CallInfo) -> PytestStatus:
        """Gets PytestStatus depending on CallInfo data. Separate Broken tests from Failed by Exception class."""
        if call.excinfo is None:
            return PytestStatus.PASSED
        exc_info_type = call.excinfo.type

        if exc_info_type == Skipped:
            return PytestStatus.SKIPPED
        if exc_info_type == AssertionError:
            return PytestStatus.FAILED

        # Test is marked as BROKEN if Exception is not of type AssertionError.
        return PytestStatus.BROKEN

    @pytest.hookimpl(hookwrapper=True, trylast=True)
    def pytest_sessionfinish(self, session: Session, exitstatus: Union[int, ExitCode]):
        yield
        config = session.config
        if is_master(config):
            if not self._service.is_test_run_available():
                # Todo: Probably it would be better to create new test run after all tests are collected.
                self._create_new_tr_run(config)
            self._service.upload_results(self._prepare_report(self._results, self._service.get_cases()))

        else:
            # Serialize results on worker node and place in workeroutput to pass results to master node
            workeroutput = getattr(config, "workeroutput")
            workeroutput[WORKER_RESULTS_KEY] = pickle.dumps(self._results)

    def _create_new_tr_run(self, config):
        """
        Creates new test run with required test cases as well as title with description.
        Args:
            config: Session.Config instance

        Returns: None

        """
        run_name = config.hook.pytest_tr_generate_run_name(config=config)
        run_description = config.hook.pytest_tr_generate_run_description(config=config)
        actual_cases = {x.case_id for x in self._results}
        self._service.create_test_run(run_name, run_description, actual_cases)

    @pytest.hookimpl(trylast=True)
    def pytest_tr_generate_run_name(self, config):
        """Default tr run name generation."""
        current_date = datetime.now().utcnow().strftime("%d-%h-%y %H:%MUTC")
        return 'Automated test run ' + current_date

    @pytest.hookimpl(trylast=True)
    def pytest_tr_generate_run_description(self, config):
        """Default tr description is empty."""
        return ""

    def _prepare_report(self, results: List[ReportDTO], testrun_cases: List[int]):
        # Remove redundant result reports
        filtered = filter(lambda x: x.case_id in testrun_cases, results)
        out = []
        for report_item in filtered:
            out.append(self.__prepare_item_report(report_item))

        # Sort results by testrail status to get failed results on top.
        return sorted(out, key=lambda x: TESTRAIL_STATUS_PRIORITY[TestrailStatus(x['status_id'])])

    def __prepare_item_report(self, report: ReportDTO) -> dict:
        """Prepares API report item."""

        return {
            "case_id": report.case_id,
            "status_id": PYTEST_TO_TESTRAIL_STATUS[report.status].value,
            "comment": self.__prepare_comment(report),
            "elapsed": f"{round(report.duration, 2) or 0.01}s"  # No need to pass more precise elapse time than 0.01s
        }

    def __prepare_comment(self, report: ReportDTO):
        msg = report.name
        if report.is_parametrized:
            # crop by [ and ] to select parametrize ID
            msg = f"Test ID: {msg[msg.find('[') + 1: msg.find(']')]}"

        if report.status in [PytestStatus.FAILED, PytestStatus.BROKEN]:
            tb = f'{msg}\n{pydash.get(report, "longrepr.reprcrash.message", "")}'
            if self._tr_config.tb_style == TestrailMsgStyle.LONG:
                return tb
            elif self._tr_config.tb_style == TestrailMsgStyle.SHORT:
                return self._shorten_error(tb)
        if report.status == PytestStatus.SKIPPED:
            return msg + f'\n{pydash.get(report, "longrepr[2]", "")}'
        return msg

    @staticmethod
    def _shorten_error(err: str) -> str:
        """Cuts long traceback message."""
        if not err:
            return err

        cut_until = err.find('\n + ')  # May be changed to more accurate substr
        return err[:cut_until]

    @staticmethod
    def __is_parametrized_test(markers: List[Mark]):
        """
        Checks if the list contains parametrized marker.

        Args:
            markers: List of test's markers.

        Returns:
            boolean

        """

        return any([x.name == 'parametrize' for x in markers])

    def _send_passed_reports(self, results: List[ReportDTO]) -> None:
        """Prepare and send all passed tests only then delete them from the reports list.

        Args:
            results: All results within node.

        Returns:
            None

        """
        passed_results = list(filter(lambda x: x.status == PytestStatus.PASSED, results))
        results[:] = list(filter(lambda x: x.status != PytestStatus.PASSED, results))

        self._service.upload_results(self._prepare_report(passed_results, self._service.get_cases()))
