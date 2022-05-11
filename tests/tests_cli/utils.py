import shutil
import difflib
import filecmp

import logging
from prettyconf import config

BOOTSTRAP_TESTS = config("BOOTSTRAP_TESTS", default=False)

LOG = logging.getLogger(__name__)


def compare_files(*, got, expected):
    """Compares the contents of a test file against expected

    Args:
        got: file with temp data
        expected: file with expected data

    Note: setting the environment variable BOOTSTRAP_TESTS=1
    will overwrite the contents of the "expected" file with the
    "got" file (ie bootstrapping the test files).
    """
    if BOOTSTRAP_TESTS:
        LOG.warning("BOOTSTRAP_TESTS: copying '%s' to '%s'", got, expected)
        shutil.copy(got, expected)

    got = f"{got}"
    expected = f"{expected}"

    are_files_identical = filecmp.cmp(got, expected)

    if not are_files_identical:
        d = difflib.Differ()
        diff_result = list(
            d.compare(open(got, "r").readlines(), open(expected, "r").readlines())
        )
        LOG.warning(f"Difference between got ({got}) and expected ({expected}) ...")
        for diff_line in diff_result:
            LOG.warning(diff_line)

    return are_files_identical
