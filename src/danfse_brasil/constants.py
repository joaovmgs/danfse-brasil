"""Project-wide constants for DANFSe generation."""

from __future__ import annotations

from pathlib import Path


PACKAGE_NAME = "danfse-brasil"
DANFSE_VERSION_LABEL = "DANFSe v2.0"
DOCUMENT_TITLE = "Documento Auxiliar da NFS-e"

NT008_DANFSE_URL = (
    "https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/rtc/"
    "nt-008-se-cgnfse-danfse-20260505.pdf"
)
NT009_RTC_URL = (
    "https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/rtc/"
    "nt-009-se-cgnfse-v1-0-1.pdf"
)
PUBLIC_CONSULTATION_URL = "https://www.nfse.gov.br/ConsultaPublica/?tpc=1&chave="
NFSE_LOGO_URL = (
    "https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/logos-da-nfs-e/"
    "Logo%20-%20NFS-e%20-%20Horizontal.png/@@images/image"
)

LEGACY_PISCOFINS_LAST_YEAR = 2026
MISSING_VALUE = "-"
REQUIRED_FONTS = ("Arial", "Microsoft Sans Serif")

DEFAULT_CLI_OUTPUT = Path("danfse.pdf")
DEFAULT_VISUAL_CHECK_XML = Path("xml.xml")
DEFAULT_VISUAL_CHECK_OUTPUT_DIR = Path("tmp/pdfs")
DEFAULT_WINDOWS_WEASYPRINT_DLL_DIR = Path(r"C:\msys64\mingw64\bin")
