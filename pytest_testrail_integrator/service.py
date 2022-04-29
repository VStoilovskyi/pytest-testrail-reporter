from typing import List, Iterable

from testrail_api import TestRailAPI

from pytest_testrail_integrator.config import TrConfig


class TrService:
    _tests: list

    def __init__(self, config, tr_api: TestRailAPI):
        self._config: TrConfig = config.tr_config
        self._api = tr_api

    def is_test_run_available(self) -> bool:
        return bool(self._config.run_id)

    @property
    def tests(self):
        """Gets Tests from run if RunId is defined.

        Returns:
            List of test dicts.
        Raises:
            ValueError: When runId in configs is not defined.

        """
        if not hasattr(self, '_tests'):
            if not self._config.run_id:
                raise ValueError('RunId is not available.')
            # Todo: Add support of receiving more than 250 tests
            self._tests = self._api.tests.get_tests(int(self._config.run_id))
        return self._tests

    def get_cases(self) -> List[int]:
        """Gets list of case ids within entire test run if defined.

        Returns:
            List of integers.

        """
        return [x['case_id'] for x in self.tests]

    def upload_results(self, results):
        if results:
            return self._api.results.add_results_for_cases(int(self._config.run_id), results)

    def create_test_run(self, run_name: str,  case_ids: Iterable[int]) -> None:
        """Creates new test with test cases matching with passed case_ids param.

        Args:
            run_name: New test run name str.
            case_ids: List of int, testrail case ids.

        Returns:
            None

        """
        assert self._config.suite_id and self._config.suite_id.isdigit()

        tr_cases = self.__filter_pytest_cases(case_ids)

        r = self._api.runs.add_run(
            self._config.project_id,
            name=run_name,
            include_all=False,
            case_ids=tr_cases,
            suite_id=self._config.suite_id
        )
        self._config.run_id = r['id']

    def __filter_pytest_cases(self, cases: Iterable[int]) -> List[int]:
        """
        Filter cases and return the only cases which are present in testrail suite.

        Args:
            cases: List of integers. Testcase ids.

        Returns:
            List[int] containing the only ids present in testrail.

        """
        # Todo: Add support of getting more than 250 cases.
        suite_cases = self._api.cases.get_cases(self._config.project_id, suite_id=self._config.suite_id)
        suite_cases_ids = [x['id'] for x in suite_cases]

        return list(filter(lambda x: x in suite_cases_ids, cases))
