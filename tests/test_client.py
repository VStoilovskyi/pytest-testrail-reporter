import pytest
from _pytest.mark import Mark
from pytest_mock import MockerFixture

from pytest_testrail_integrator.client import TrClient
from pytest_testrail_integrator.config import TrConfig


class TestClient:

    @pytest.mark.parametrize("deselect_flag, tests_count", [(True, 0), (False, 1)])
    def test_collect_filters_items(self, pytester: pytest.Pytester, mocker: MockerFixture, deselect_flag, tests_count):
        """Check if List[Items] is filtered when collecting tests and --tr-deselect-tests either passed or not."""
        config = pytester.parseconfig()
        options = {
            "--tr-reporting": True,
            "--tr_deselect_tests": deselect_flag
        }

        config.getoption = lambda x, y=None: options[x] or y
        config.getini = lambda x, y=None: y
        config.tr_config = TrConfig(config)

        item = mocker.MagicMock()
        item.get_closest_marker.return_value = Mark('case', ('1234',), {})
        items = [item]

        service_mock = mocker.MagicMock()
        config.tr_service = service_mock
        service_mock.is_test_run_available.return_value = True
        service_mock.tests.return_value = [1234, 5678]

        client = TrClient(config)
        client.pytest_collection_modifyitems(mocker.MagicMock(), config, items)
        assert len(items) == tests_count
