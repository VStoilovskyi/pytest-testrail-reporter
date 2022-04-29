import os

from pytest import Config

from pytest_testrail_integrator.constants import TestrailMsgStyle


class TrConfig:
    """Object storing entire configs set for Testrail-Integrator plugin."""

    def __init__(self, config: Config):
        self._config = config
        self.start_client = config.getoption('--tr-reporting')
        self.deselect_tests = config.getoption('--tr-deselect-tests', False)
        self.run_id = os.getenv('TR_RUN_ID') or config.getini('tr_run_id')
        self.api_url = os.getenv('TR_API_URL') or config.getini('tr_api_url')
        self.user_email = os.getenv('TR_USER_EMAIL') or config.getini('tr_user_email')
        self.user_password = os.getenv('TR_USER_PASSWORD') or config.getini('tr_user_password')
        self.project_id = os.getenv('TR_PROJECT_ID') or config.getini('tr_project_id')
        self.suite_id = os.getenv('TR_SUITE_ID') or config.getini('tr_suite_id')
        self.tb_style = TestrailMsgStyle(config.getoption('--tr-tb') or config.getini('tr_tb') or 'short')

        required_keys = (self.api_url, self.user_email, self.user_password)
        assert all(required_keys)
