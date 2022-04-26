from _pytest.config.argparsing import Parser

from pytest_testrail_integrator.client import TrClient
from pytest_testrail_integrator.service import TrService
from pytest_testrail_integrator.config import TrConfig


def pytest_addoption(parser: Parser):
    group = parser.getgroup('testrail')
    group.addoption(
        '--tr-reporting',
        action='store_true',
        help='Setup TestRail report client for upload test results.'
    )
    group.addoption(
        '--tr_deselect_tests',
        action='store_true',
        help='Deselect tests if its\' case is not present in run.'
    )
    parser.addini('tr_url', default='', help='Testrail Api url.')
    parser.addini('tr_user_email', default='', help='Testrail user\'s email.')
    parser.addini('tr_user_password', default='', help='Testrail user\'s password.')
    parser.addini('tr_project_id', default='', help='Testrail project id for new testrun creation.')


def pytest_configure(config):
    if config.getoption('--tr-reporting'):
        config.tr_config = TrConfig(config)
        config.tr_service = TrService(config)
        plugin = TrClient(config)
        config.pluginmanager.register(plugin)
        config.testrail_reporter = plugin
