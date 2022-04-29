# Pytest Testrail Integrator.

Pytest-testrail-integrator is a pytest extension for reporting test results to [Testrail](https://www.gurock.com/testrail).

Pytest-testrail-integrator gives an ability to send test results to specific testrail run or can create new one during 
test execution. Fully compatible with `xdist` parallelization tool.

### Installation
```shell
pip install pytest-testrail-integrator
```

### Example 

In order to link pytest test to testrail case you need to mark test with `pytest.mark.case` or `tr_case` 
decorator with testcase id passing as argument.

```python
import pytest

from pytest_testrail_integrator.client import tr_case


@pytest.mark.case('98765')  # Use raw pytest marker.
def test_sum():
    assert 1 + 1 == 2


@tr_case('987654')  # Use custom decorator.
def test_divide():
    assert 2 / 1 == 2
```
Test case id must not start with "C" char and can be either string or integer.


### Main flow overview.
At startup plugin checks if the Testrail run id is passed or not. If not passed - plugin will create new test run by 
itself. Then during tests execution testrail tests will be updated in real time.


### Config for TestRail

* All required configs can be loaded from virtual environment variables(higher priority)
: 
``` shell
TR_RUN_ID
TR_API_URL
TR_USER_EMAIL
TR_USER_PASSWORD
TR_PROJECT_ID
TR_SUTE_ID
```

Or

* Add options to `pytest.ini` file.

### Launch

In order to start tests with Pytest-Message you must provide `--tr-reporting` flag:
```shell
pytest tests --tr-reporting
```

### All available command line options.

| option              | description                                                                                                                                                                              |
|---------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| --tr-reporting      | Create and update testruns with TestRail                                                                                                                                                 |
| --tr-deselect-tests | If pass testrun id only. Selects only tests which have been marked with case decorator with appropriate case id. Other tests are marked as deselected and not started in test execution. |

### All available pytest.ini options.
| option           | description                                                                                           |
|------------------|-------------------------------------------------------------------------------------------------------|
| tr_api_url       | Testrail api url.                                                                                     |
| tr_run_id        | Testrail test run id. If passed test reports are linked to this particular test run.                  |
| tr_user_email    | Testrail User email for API authentication.                                                           |
| tr_user_password | Testrail User password for API authentication.                                                        |
| tr_project_id    | Testrail Project Id. Required for new test run creation if Test Run Id is not passed.                 |
| tr_suite_id      | Testrail Suite Id. Required for new test run creation if Test Run Id is not passed.                   |
| tr_tb            | Traceback level in testrail message reports. ['short', 'long'] options. Short is selected by default. |


### Hooks
#### pytest_tr_generate_run_name(config: pytest.Config) - > str:

Executes for generating new testrail run name right before create test run request is sent. Takes first hook result.
