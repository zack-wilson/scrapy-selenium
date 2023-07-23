"""This module contains the ``SeleniumMiddleware`` scrapy middleware"""

from importlib import import_module

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.http import HtmlResponse
from selenium.webdriver.support.ui import WebDriverWait

from . import defaults
from .http import SeleniumRequest


class SeleniumMiddleware:
    """Scrapy middleware handling the requests using selenium"""

    def __init__(
        self,
        driver_name: str,
        driver_executable_path: str,
        grid_url: str | None = None,
        command_executor: str | None = None,
        driver_arguments: list[str] | None = None,
        browser_executable_path: str | None = None,
    ):
        """Initialize the selenium webdriver

        Parameters
        ----------
        driver_name: str
            The selenium ``WebDriver`` to use
        driver_executable_path: str
            The path of the executable binary of the driver
        grid_url: str
            The selenium grid url. example: http://127.0.0.1:4444/wd/hub
        driver_arguments: list
            A list of arguments to initialize the driver
        browser_executable_path: str
            The path of the executable binary of the browser
        command_executor: str
            Selenium remote server endpoint
        """
        webdriver_base_path = f"selenium.webdriver.{driver_name.lower()}"

        if grid_url:
            driver_klass_module = import_module("selenium.webdriver.remote.webdriver")
        else:
            driver_klass_module = import_module(f"{webdriver_base_path}.webdriver")

        driver_klass = getattr(driver_klass_module, "WebDriver")

        driver_service_module = import_module(f"{webdriver_base_path}.service")
        driver_service_klass = getattr(driver_service_module, "Service")

        driver_options_module = import_module(f"{webdriver_base_path}.options")
        driver_options_klass = getattr(driver_options_module, "Options")

        driver_service = driver_service_klass()
        driver_options = driver_options_klass()

        if browser_executable_path:
            driver_options.binary_location = browser_executable_path

        if driver_arguments:
            for argument in driver_arguments:
                driver_options.add_argument(argument)

        driver_kwargs = {"service": driver_service, "options": driver_options}

        if grid_url:
            driver_kwargs["command_executor"] = grid_url
        else:
            driver_kwargs["service"] = driver_service_klass(
                executable_path=driver_executable_path
            )

        if not grid_url:
            self.driver = driver_klass(**driver_kwargs)
        else:
            from selenium import webdriver

            capabilities = driver_options.to_capabilities()
            self.driver = webdriver.Remote(
                command_executor=grid_url,
                desired_capabilities=capabilities,
                options=driver_options,
            )

    @classmethod
    def from_crawler(cls, crawler):
        """Initialize the middleware with the crawler settings"""

        driver_name = crawler.settings.get("SELENIUM_DRIVER_NAME")
        driver_executable_path = crawler.settings.get("SELENIUM_DRIVER_EXECUTABLE_PATH")
        browser_executable_path = crawler.settings.get(
            "SELENIUM_BROWSER_EXECUTABLE_PATH"
        )
        command_executor = crawler.settings.get("SELENIUM_COMMAND_EXECUTOR")
        driver_arguments = crawler.settings.get("SELENIUM_DRIVER_ARGUMENTS")

        grid_url = crawler.settings.get("SELENIUM_REMOTE_URL", None)

        if not driver_name:
            raise NotConfigured("SELENIUM_DRIVER_NAME must be set")
        if not (driver_executable_path or grid_url):
            raise NotConfigured(
                "SELENIUM_DRIVER_EXECUTABLE_PATH or SELENIUM_REMOTE_URL  must set one"
            )

        middleware = cls(
            driver_name=driver_name,
            grid_url=grid_url,
            driver_executable_path=driver_executable_path,
            browser_executable_path=browser_executable_path,
            command_executor=command_executor,
            driver_arguments=driver_arguments,
        )

        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)

        return middleware

    def process_request(self, request, spider):
        """Process a request using the selenium driver if applicable"""

        if not isinstance(request, SeleniumRequest):
            return None

        self.driver.get(request.url)

        for cookie_name, cookie_value in request.cookies.items():
            self.driver.add_cookie({"name": cookie_name, "value": cookie_value})

        if request.wait_until:
            WebDriverWait(self.driver, request.wait_time).until(request.wait_until)

        if request.screenshot:
            request.meta["screenshot"] = self.driver.get_screenshot_as_png()

        if request.script:
            self.driver.execute_script(request.script)

        body = str.encode(self.driver.page_source)

        # Expose the driver via the "meta" attribute
        request.meta.update({"driver": self.driver})

        return HtmlResponse(
            self.driver.current_url, body=body, encoding="utf-8", request=request
        )

    def spider_closed(self):
        """Shutdown the driver when spider is closed"""

        self.driver.quit()
