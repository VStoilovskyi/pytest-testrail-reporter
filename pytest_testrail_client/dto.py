import dataclasses
from typing import List, Union

from _pytest._code import ExceptionInfo
from _pytest._code.code import TerminalRepr
from _pytest.mark import Mark

from src.plugins.pytest_tr_client.constants import PytestStatus


@dataclasses.dataclass
class ReportDTO:
    name: str
    nodeid: str
    markers: List[Mark]
    status: PytestStatus
    duration: float
    longrepr: Union[None, ExceptionInfo[BaseException], tuple[str, int, str], str, TerminalRepr]
    case_id: int
