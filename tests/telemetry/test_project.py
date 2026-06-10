from unittest.mock import patch, mock_open

from pylog.telemetry.project import get_project_name


@patch("pylog.telemetry.project.Path.exists")
@patch("builtins.open", new_callable=mock_open)
def test_get_project_name_success(mock_file, mock_exists):
    mock_exists.return_value = True

    mock_file.return_value.read.return_value = b"""
        [project]
        name = "simple-otel-logger"
    """

    result = get_project_name()

    assert result == "simple-otel-logger"


@patch("pylog.telemetry.project.tomllib.load")
@patch("pylog.telemetry.project.Path.exists")
def test_get_project_name_missing_project(mock_exists, mock_toml):
    mock_exists.return_value = True

    mock_toml.return_value = {}

    assert get_project_name() == "unknown-service"


@patch("pylog.telemetry.project.Path.exists")
def test_get_project_name_file_not_found(mock_exists):
    mock_exists.return_value = False

    assert get_project_name() == "unknown-service"
