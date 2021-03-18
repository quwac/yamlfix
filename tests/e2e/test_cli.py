"""Test the command line interface."""

import re
from textwrap import dedent

import pytest
from click.testing import CliRunner

from yamlfix.entrypoints.cli import cli
from yamlfix.version import __version__


@pytest.fixture(name="runner")
def fixture_runner() -> CliRunner:
    """Configure the Click cli test runner."""
    return CliRunner(mix_stderr=False)


def test_version(runner: CliRunner) -> None:
    """Prints program version when called with --version."""
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert re.match(
        fr" *yamlfix version: {__version__}\n" r" *python version: .*\n *platform: .*",
        result.stdout,
    )


def test_corrects_one_file(runner: CliRunner, tmpdir) -> None:
    """Correct the source code of a file."""
    test_file = tmpdir.join("source.yaml")
    test_file.write("program: yamlfix")
    fixed_source = dedent(
        """\
        ---
        program: yamlfix"""
    )

    result = runner.invoke(cli, [str(test_file)])

    assert result.exit_code == 0
    assert test_file.read() == fixed_source


@pytest.mark.secondary()
def test_corrects_three_files(runner: CliRunner, tmpdir) -> None:
    """Correct the source code of multiple files."""
    test_files = []
    for file_number in range(3):
        test_file = tmpdir.join(f"source_{file_number}.yaml")
        test_file.write("program: yamlfix")
        test_files.append(test_file)
    fixed_source = dedent(
        """\
        ---
        program: yamlfix"""
    )

    result = runner.invoke(cli, [str(test_file) for test_file in test_files])

    assert result.exit_code == 0
    for test_file in test_files:
        assert test_file.read() == fixed_source


def test_corrects_code_from_stdin(runner) -> None:
    """Correct the source code passed as stdin."""
    source = "program: yamlfix"
    fixed_source = dedent(
        """\
        ---
        program: yamlfix"""
    )

    result = runner.invoke(cli, ["-"], input=source)

    assert result.exit_code == 0
    assert result.stdout == fixed_source
