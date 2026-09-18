"""Public exception types for pyadaptagrams."""


class AdaptagramsError(RuntimeError):
    """Base exception raised by pyadaptagrams."""


class GeometryError(ValueError, AdaptagramsError):
    """Raised when graph geometry is missing or invalid."""


class UnsupportedGraphError(AdaptagramsError):
    """Raised for a graph structure unsupported by the native algorithm."""
