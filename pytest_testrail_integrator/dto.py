import dataclasses
from typing import List, Union, Tuple

from _pytest._code.code import ExceptionChainRepr
from _pytest.mark import Mark

from pytest_testrail_integrator.constants import PytestStatus


@dataclasses.dataclass
class ReportDTO:
    name: str
    nodeid: str
    markers: List[Mark]
    status: PytestStatus
    duration: float
    longrepr: Union[None, Tuple[str, int, str], ExceptionChainRepr]
    case_id: int
