import os

import pytest
from _pytest.mark import Mark
from pytest_mock import MockerFixture

from pytest_testrail_integrator.client import TrClient
from pytest_testrail_integrator.config import TrConfig
from pytest_testrail_integrator.service import TrService

pytest_plugins = ('pytester',)


PYTEST_ENV = {
    "TR_RUN_ID": "1",
    "TR_API_URL": "test.com",
    "TR_USER_EMAIL": "test@test.com",
    "TR_USER_PASSWORD": "qwerty",
    "TR_PROJECT_ID": "321",
    "TR_SUITE_ID": '1122'
}


@pytest.fixture()
def setup_env():
    os.environ.update(PYTEST_ENV)
    yield
    [os.environ.pop(x) for x in PYTEST_ENV]


@pytest.fixture()
def mocked_session(mocker: MockerFixture):
    return mocker.create_autospec(pytest.Session)


@pytest.fixture()
def mocked_item(mocker: MockerFixture):
    item: pytest.Item = mocker.create_autospec(pytest.Item)
    item.name = mocker.PropertyMock('item_name')
    item.nodeid = mocker.PropertyMock('item_node_name')
    item.get_closest_marker.return_value = Mark('12345', tuple(), {})
    return item


@pytest.fixture()
def mocked_service(mocker: MockerFixture):
    return mocker.create_autospec(TrService)


@pytest.fixture()
def mocked_config(pytester, mocked_service):
    cfg = pytester.parseconfig()
    options = {
        "--tr-reporting": True,
        "--tr-deselect-tests": True,
        "--tr-tb": 'short'
    }

    cfg.getoption = lambda x, y=None: y or options.get(x)
    cfg.getini = lambda x, y=None: y

    cfg.tr_config = TrConfig(cfg)
    cfg.tr_service = mocked_service
    return cfg


@pytest.fixture()
def mocked_client(mocked_config):
    return TrClient(mocked_config)
