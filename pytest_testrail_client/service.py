from typing import List, Iterable

from testrail_api import TestRailAPI

from pytest_testrail_client.config import TrConfig


class TrService:
    _tests: list

    def __init__(self, config):
        self._config: TrConfig = config.tr_config
        self._api = TestRailAPI(self._config.api_url, self._config.user_email, self._config.user_password)

    def is_test_run_available(self) -> bool:
        return bool(self._config.run_id)

    @property
    def tests(self):
        """
        Gets Tests from run if RunId is defined.
        :raises ValueError: When runId in configs is not defined.
        :return: List of test dicts.
        """
        if not hasattr(self, '_tests'):
            if not self._config.run_id:
                raise ValueError('RunId is not available.')
            self._tests = self._api.tests.get_tests(int(self._config.run_id))
        return self._tests

    def get_cases(self) -> List[int]:
        """
        Gets list of case ids within entire test run if defined.
        :return: List of integers.
        """
        return [x['case_id'] for x in self.tests]

    def upload_results(self, results):
        if results:
            return self._api.results.add_results_for_cases(int(self._config.run_id), results)

    def create_test_run(self, case_ids: Iterable[int]) -> int:
        """
        Creates new test with test cases matching with passed case_ids param.
        :param case_ids: List of int, testrail case ids.
        :return:
        """
        r = self._api.runs.add_run(
            self._config.project_id,
            name='Automated Test run',
            include_all=False,
            case_ids=list(case_ids)
        )
        self._config.run_id = r['id']  # guessing the key
        return 0
