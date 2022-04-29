import pytest

from pytest_testrail_integrator.config import TrConfig
from pytest_testrail_integrator.constants import TestrailMsgStyle

INI = {
    'tr_run_id': '2',
    'tr_api_url': 'example.com',
    'tr_user_email': 'user@example.com',
    'tr_user_password': 'asdf',
    'tr_project_id': '54',
    'tr_suite_id': '11',
    'tr_tb': 'long'
}


def test_config_env_var_has_grater_priority(pytester: pytest.Pytester, setup_env):
    config = pytester.parseconfig()
    options = {
        "--tr-reporting": True,
        "--tr-deselect-tests": False,
        "--tr-tb": "long"
    }

    config.getoption = lambda x, y=None: options[x] or y
    config.getini = lambda x, y=None: INI[x] or y
    tr_config = TrConfig(config)
    assert tr_config.run_id == '1'
    assert tr_config.api_url == 'test.com'
    assert tr_config.user_email == 'test@test.com'
    assert tr_config.user_password == 'qwerty'
    assert tr_config.project_id == '321'
    assert tr_config.suite_id == '1122'
    assert tr_config.tb_style == TestrailMsgStyle.LONG


def test_config_env_loads_from_ini(pytester: pytest.Pytester):
    config = pytester.parseconfig()
    options = {
        "--tr-reporting": False,
        "--tr-deselect-tests": True,
        '--tr-tb': ''
    }

    config.getoption = lambda x, y=None: options[x] or y
    config.getini = lambda x, y=None: INI[x] or y
    tr_config = TrConfig(config)
    assert tr_config.run_id == '2'
    assert tr_config.api_url == 'example.com'
    assert tr_config.user_email == 'user@example.com'
    assert tr_config.user_password == 'asdf'
    assert tr_config.project_id == '54'
    assert tr_config.suite_id == '11'
    assert tr_config.tb_style == TestrailMsgStyle.LONG


def test_trconfig_required_keys_missed(pytester: pytest.Pytester):
    config = pytester.parseconfig()
    options = {
        "--tr-reporting": False,
        "--tr-deselect-tests": True,
        "--tr-tb": ''
    }

    config.getini = lambda x: ''
    config.getoption = lambda x: options[x]
    config.getoption = lambda x, y=None: options[x] or y

    with pytest.raises(AssertionError):
        TrConfig(config)
