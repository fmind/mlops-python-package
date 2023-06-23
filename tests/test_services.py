"""Test the services module."""
# pylint: disable=missing-docstring

# %% IMPORTS

from loguru import logger

from wines import services

# %% SERVICES


def test_logger_service(logger_service: services.LoggerService, capsys):
    # given
    service = logger_service
    # when
    service.start()
    logger.info("INFO")
    logger.debug("DEBUG")
    service.stop()  # no effect
    # then
    capture = capsys.readouterr()
    assert capture.out == "", "No output to stdout!"
    assert "INFO" in capture.err, "INFO should be logged!"
    assert "DEBUG" not in capture.err, "Debug should not be logged!"
