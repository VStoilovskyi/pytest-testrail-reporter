import dataclasses
from typing import List, Union, Tuple

from _pytest._code.code import TerminalRepr
from pytest import ExceptionInfo, Mark

from pytest_testrail_integrator.constants import PytestStatus


@dataclasses.dataclass
class ReportDTO:
    name: str
    nodeid: str
    markers: List[Mark]
    status: PytestStatus
    duration: float
    longrepr: Union[None, ExceptionInfo[BaseException], Tuple[str, int, str], str, TerminalRepr]
    case_id: int
