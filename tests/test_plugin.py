import ast
import logging
from textwrap import dedent

import pytest

from flake8checker import run_flake8_plugin

logging.basicConfig(level=logging.DEBUG)


@pytest.mark.parametrize("code, expected_errors", [
    ("logger.debug('This is a log message with no arguments')", []),
    ("logger.warning('The temperature is %d degrees Celsius', temperature)",
     []),
    ("logger.error('The temperature is %d degrees Celsius')", [
        (1, 0, "LOG001 Too few arguments for format string", None)
    ]),
    ("logger.info('The temperature is %d degrees Celsius', temperature, humidity)",
     [(1, 0, "LOG001 Too many arguments for format string", None)]),
    (dedent("""
    logger.debug('This is a log message with no arguments')
    logger.warning('The temperature is %d degrees Celsius', temperature, humidity)
    logger.error('The temperature is %d degrees Celsius')
    """), [(3, 0, "LOG001 Too many arguments for format string", None),
          (4, 0, "LOG001 Too few arguments for format string", None)])
])
def test_LogFormattingChecker(code, expected_errors):
    tree = ast.parse(code)
    errors = run_flake8_plugin(tree, "test.py")
    assert errors == expected_errors
