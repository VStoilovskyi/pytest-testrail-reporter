import enum

TR_MARKER_NAME = 'case'
TR_PASSED_TESTS_FLUSH_SIZE = 500


class TestrailStatus(enum.Enum):
    PASSED = 1
    BLOCKED = 2
    UNTESTED = 3
    RETEST = 4
    FAILED = 5
    IN_PROGRESS = 6
    SKIP = 7
    REOPENED = 8
    BROKEN = 9


class PytestStatus(enum.Enum):
    PASSED = 'passed'
    FAILED = 'failed'
    SKIPPED = 'skipped'
    BROKEN = 'broken'


TESTRAIL_STATUS_PRIORITY = {
    TestrailStatus.PASSED: 1,
    TestrailStatus.SKIP: 2,
    TestrailStatus.FAILED: 3,
    TestrailStatus.BROKEN: 4,
}
PYTEST_TO_TESTRAIL_STATUS = {
    PytestStatus.PASSED: TestrailStatus.PASSED,
    PytestStatus.FAILED: TestrailStatus.FAILED,
    PytestStatus.SKIPPED: TestrailStatus.SKIP,
    PytestStatus.BROKEN: TestrailStatus.BROKEN,
}


class TestrailMsgStyle(enum.Enum):
    LONG = 'long'
    SHORT = 'short'
