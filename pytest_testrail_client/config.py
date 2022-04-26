import os

from _pytest.config import Config


class TrConfig:
    def __init__(self, config: Config):
        self._config = config
        self.start_client = config.getoption('--tr-reporting')
        self.deselect_tests = config.getoption('--tr_deselect_tests', False)
        self.run_id = os.getenv('TR_RUN_ID') or config.getini('tr_run_id')
        self.api_url = os.getenv('TR_API_URL') or config.getini('tr_api_url')
        self.user_email = os.getenv('TR_USER_EMAIL') or config.getini('tr_user_email')
        self.user_password = os.getenv('TR_USER_PASSWORD') or config.getini('tr_user_password')
        self.project_id = os.getenv('TR_PROJECT_ID') or config.getini('tr_project_id')
