from shutil import which

SELENIUM_DRIVER_NAME = "Firefox"
SELENIUM_DRIVER_EXECUTABLE_PATH: str = which(SELENIUM_DRIVER_NAME) or "firefox"
SELENIUM_BROWSER_EXECUTABLE_PATH: str | None = None
SELENIUM_COMMAND_EXECUTOR: str | None = None
