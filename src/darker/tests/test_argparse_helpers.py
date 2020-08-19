from argparse import ArgumentParser, Namespace
from contextlib import suppress
from logging import CRITICAL, DEBUG, ERROR, INFO, NOTSET, WARNING

import pytest

from darker import argparse_helpers


@pytest.mark.parametrize(
    "line, width, indent, expect",
    [
        ("", 0, "    ", ValueError),
        ("", 1, "    ", []),
        (
            "lorem ipsum dolor sit amet",
            9,
            "    ",
            ["    lorem", "    ipsum", "    dolor", "    sit", "    amet"],
        ),
        (
            "lorem ipsum dolor sit amet",
            15,
            "    ",
            ["    lorem ipsum", "    dolor sit", "    amet"],
        ),
    ],
)
def test_fill_line(line, width, indent, expect):
    with pytest.raises(expect) if type(expect) is type else suppress():

        result = argparse_helpers._fill_line(line, width, indent)

        assert result.splitlines() == expect


@pytest.mark.parametrize(
    "text, width, indent, expect",
    [
        (
            "lorem ipsum dolor sit amet",
            15,
            "    ",
            ["    lorem ipsum", "    dolor sit", "    amet"],
        ),
        (
            "lorem\nipsum dolor sit amet",
            15,
            "    ",
            ["    lorem", "    ipsum dolor", "    sit amet"],
        ),
    ],
)
def test_newline_preserving_formatter(text, width, indent, expect):
    formatter = argparse_helpers.NewlinePreservingFormatter("dummy")

    result = formatter._fill_text(text, width, indent)

    assert result.splitlines() == expect


@pytest.mark.parametrize(
    "const, initial, expect",
    [
        (10, NOTSET, DEBUG),
        (10, DEBUG, INFO),
        (10, INFO, WARNING),
        (10, WARNING, ERROR),
        (10, ERROR, CRITICAL),
        (10, CRITICAL, CRITICAL),
        (-10, DEBUG, DEBUG),
        (-10, INFO, DEBUG),
        (-10, WARNING, INFO),
        (-10, ERROR, WARNING),
        (-10, CRITICAL, ERROR),
    ],
)
def test_log_level_action(const, initial, expect):
    action = argparse_helpers.LogLevelAction([], "log_level", const)
    parser = ArgumentParser()
    namespace = Namespace(log_level=initial)

    action(parser, namespace, [])

    assert namespace.log_level == expect


@pytest.mark.parametrize(
    "const, count, expect",
    [
        (10, NOTSET, WARNING),
        (10, 1, ERROR),
        (10, 2, CRITICAL),
        (10, 3, CRITICAL),
        (-10, NOTSET, WARNING),
        (-10, 1, INFO),
        (-10, 2, DEBUG),
        (-10, 3, DEBUG),
    ],
)
def test_argumentparser_log_level_action(const, count, expect):
    parser = ArgumentParser()
    parser.register("action", "log_level", argparse_helpers.LogLevelAction)
    parser.add_argument("-l", dest="log_level", action="log_level", const=const)

    args = parser.parse_args(count * ["-l"])

    assert args.log_level == expect
