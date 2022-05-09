import pytest
from pytest import PytestPluginManager, Parser
from testrail_api import TestRailAPI

from pytest_testrail_integrator.client import TrClient
from pytest_testrail_integrator.config import TrConfig
from pytest_testrail_integrator.service import TrService


def pytest_addoption(parser: Parser):
    group = parser.getgroup('testrail')
    group.addoption(
        '--tr-reporting',
        action='store_true',
        help='Setup TestRail report client for upload test results.'
    )
    group.addoption(
        '--tr-deselect-tests',
        action='store_true',
        help='Deselect tests if its\' case is not present in run.'
    )
    group.addoption(
        '--tr-tb',
        action='store',
        help='Sets traceback level in testrail message reports.'
    )
    parser.addini('tr_url', default='', help='Testrail Api url.')
    parser.addini('tr_user_email', default='', help='Testrail user\'s email.')
    parser.addini('tr_user_password', default='', help='Testrail user\'s password.')
    parser.addini('tr_project_id', default='', help='Testrail project id for new testrun creation.')
    parser.addini('tr_suite_id', default='', help='Testrail suite id to create test run from.')
    parser.addini('tr_run_id', default='', help='Testrail run id to update tests in.')
    parser.addini('tr_tb', default='', help='Sets traceback level in testrail message reports.')


@pytest.hookimpl
def pytest_addhooks(pluginmanager: PytestPluginManager):
    from pytest_testrail_integrator import new_hooks
    pluginmanager.add_hookspecs(new_hooks)


def pytest_configure(config):
    if config.getoption('--tr-reporting'):
        tr_config = TrConfig(config)
        tr_api = TestRailAPI(tr_config.api_url, tr_config.user_email, tr_config.user_password)
        config.tr_config = tr_config
        config.tr_service = TrService(config, tr_api)
        plugin = TrClient(config)
        config.pluginmanager.register(plugin)
        if config.pluginmanager.hasplugin("xdist"):

            from pytest_testrail_integrator.xdist.xdist_tr_adapter import XdistTrClintAdapter
            config.pluginmanager.register(XdistTrClintAdapter(plugin))

        config.testrail_reporter = plugin
