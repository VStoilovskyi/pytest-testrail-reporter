import math
import pickle
from typing import List, Union

import pytest
from _pytest.config import ExitCode, Config
from _pytest.main import Session
from _pytest.mark import Mark
from _pytest.nodes import Item
from _pytest.reports import TestReport
from _pytest.runner import CallInfo

from .config import TrConfig
from .constants import TR_MARKER_NAME, TR_PASSED_TESTS_FLUSH_SIZE, TestrailStatus, \
    PytestStatus, TESTRAIL_STATUS_PRIORITY, PYTEST_TO_TESTRAIL_STATUS
from .dto import ReportDTO
from .service import TrService


def tr_case(case_id: Union[str, int]):
    return pytest.mark.case(case_id)


def is_master(config) -> bool:
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

    def pytest_collection_modifyitems(self, session: Session, config: Config, items: List[Item]):
        if self._service.is_test_run_available() and self._tr_config.deselect_tests:
            tr_run_cases = self._service.get_cases()
            deselected = []
            selected = []
            for item in items:
                marker = item.get_closest_marker(TR_MARKER_NAME)
                if not marker or int(marker.args[0]) not in tr_run_cases:
                    deselected.append(item)
                else:
                    selected.append(item)
            items[:] = selected

            config.hook.pytest_deselected(items=deselected)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item: Item, call: CallInfo):
        result: TestReport = (yield).get_result()
        if call.when == 'call' or result.outcome == 'skipped':
            if marker := item.get_closest_marker(TR_MARKER_NAME):
                case_id = int(marker.args[0])

                report = ReportDTO(
                    item.name,
                    item.nodeid,
                    item.own_markers,
                    PytestStatus(result.outcome),
                    result.duration,
                    result.longrepr,
                    case_id
                )

                self._results.append(report)

                if report.status == PytestStatus.PASSED:
                    self._passed_tests_count += 1

                # Try to flush passed results per node
                if self._service.is_test_run_available() and \
                        self._passed_tests_count > TR_PASSED_TESTS_FLUSH_SIZE:
                    self._try_send_passed_reports(self._results)
                    self._passed_tests_count = 0

    @pytest.hookimpl(hookwrapper=True, trylast=True)
    def pytest_sessionfinish(self, session: Session, exitstatus: Union[int, ExitCode]):
        yield
        if not is_master(session.config):
            # Serialize results and place in workeroutput to pass data to master node
            session.config.workeroutput['tr_results'] = pickle.dumps(self._results)
        else:
            if not self._service.is_test_run_available():
                # Todo: Probably it would be better to create new test run after all tests are collected.
                self._service.create_test_run(self._service.get_cases())

            self._service.upload_results(self._prepare_report(self._results, self._service.get_cases()))

    def pytest_testnodedown(self, node, error):
        """
        Extend master node results with worker's node results.
        """
        node_reports = pickle.loads(node.workeroutput['tr_results'])
        self._results.extend(node_reports)

    def _prepare_report(self, results: List[ReportDTO], testrun_cases: List[int]):
        # Remove redundant result reports
        filtered = filter(lambda x: x.case_id in testrun_cases, results)
        out = []
        for report_item in filtered:
            out.append(self.__prepare_item_report(report_item))

        # Sort results by testrail status.
        return sorted(out, key=lambda x: TESTRAIL_STATUS_PRIORITY[TestrailStatus(x['status_id'])])

    def __prepare_item_report(self, report: ReportDTO) -> dict:
        """Prepares API report item."""

        return {
            "case_id": report.case_id,
            "status_id": PYTEST_TO_TESTRAIL_STATUS[report.status].value,
            "comment": self.__prepare_comment(report),
            "elapsed": f"{math.ceil(report.duration)}s"
        }

    def __prepare_comment(self, report: ReportDTO):
        msg = report.name
        if self.__is_parametrized_test(report.markers):
            # crop by [ and ] to select parametrize ID
            msg = f"Test IDENTIFIER: {msg[msg.find('[') + 1: msg.find(']')]}"

        if report.status == PytestStatus.FAILED:
            return f'{msg}\n{report.longrepr.reprcrash.message}'
        if report.status == PytestStatus.SKIPPED:
            return msg + f'\n{report.longrepr[2]}'
        return msg

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

    def _try_send_passed_reports(self, results: List[ReportDTO]) -> None:
        """
        Prepare and send all passed tests only then delete them from the reports list.

        Args:
            results: All results within node.

        Returns:
            None

        """
        passed_results = list(filter(lambda x: x.status == PytestStatus.PASSED, results))
        results[:] = list(filter(lambda x: x.status != PytestStatus.PASSED, results))

        self._service.upload_results(self._prepare_report(passed_results, self._service.get_cases()))
