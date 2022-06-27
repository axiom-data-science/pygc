from pygc.gc import great_circle
from pygc.gc import great_distance

__all__ = ["great_circle", "great_distance"]

try:
    from ._version import __version__
except ImportError:
    __version__ = "unknown"
