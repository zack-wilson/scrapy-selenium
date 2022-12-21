from importlib.metadata import PackageNotFoundError, version

from .http import SeleniumRequest
from .middlewares import SeleniumMiddleware

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError
