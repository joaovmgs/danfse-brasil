"""Project-specific exceptions."""


class DanfseError(Exception):
    """Base exception for DANFSe generation errors."""


class InvalidNFSeXmlError(DanfseError):
    """Raised when the XML does not contain the expected NFS-e structure."""
