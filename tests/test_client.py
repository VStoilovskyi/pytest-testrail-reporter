import pytest
from _pytest.mark import Mark
from pytest_mock import MockerFixture

from pytest_testrail_integrator.client import TrClient


@pytest.mark.usefixtures("setup_env")
class TestClient:

    @pytest.mark.parametrize("deselect_flag, tests_count", [(True, 0), (False, 2)])
    def test_collect_filters_items(self, mocked_config, mocker: MockerFixture, deselect_flag, tests_count, mocked_item):
        """Check if List[Items] is filtered when collecting tests and --tr-deselect-tests either passed or not."""
        mocked_config.tr_config.deselect_tests = deselect_flag

        mocked_item.get_closest_marker.side_effect = [Mark('case', ('12345',), {}), None]
        items = [mocked_item, mocked_item]

        service_mock = mocked_config.tr_service
        service_mock.is_test_run_available.return_value = True
        service_mock.get_cases.return_value = [1234, 5678]

        client = TrClient(mocked_config)
        client.pytest_collection_modifyitems(mocker.MagicMock(), mocked_config, items)
        assert len(items) == tests_count

    def test_client_makereport_no_case_marker(self, mocker: MockerFixture, mocked_client):
        """Checks that no report for tests without case id marker."""
        item: pytest.Item = mocker.create_autospec(pytest.Item)
        item.own_markers = mocker.PropertyMock(Mark('some_marker', tuple(), {}))
        item.get_closest_marker.return_value = None

        mocked_client.pytest_runtest_makereport(item, mocker.MagicMock())
