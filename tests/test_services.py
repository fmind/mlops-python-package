# pylint: disable=missing-docstring

# %% IMPORTS

from loguru import logger

from bikes import services

# %% SERVICES


def test_logger_service(capsys):
    # given
    service = services.LoggerService(sink="stdout", level="INFO")
    # when
    service.start()
    logger.info("INFO")
    logger.debug("DEBUG")
    # then
    capture = capsys.readouterr()
    assert capture.err == "", "No output to stderr!"
    assert "INFO" in capture.out, "INFO should be logged!"
    assert "DEBUG" not in capture.out, "Debug should not be logged!"
