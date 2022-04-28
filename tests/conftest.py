import os

import pytest

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
