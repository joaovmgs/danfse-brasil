import base64

from danfse_brasil.logo import NFSE_LOGO_DATA_URI


def test_embedded_nfse_logo_is_a_png() -> None:
    prefix, encoded = NFSE_LOGO_DATA_URI.split(",", 1)

    assert prefix == "data:image/png;base64"
    assert base64.b64decode(encoded).startswith(b"\x89PNG\r\n\x1a\n")
