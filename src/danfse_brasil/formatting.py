"""Formatting helpers for DANFSe fields."""

from __future__ import annotations

from datetime import datetime

from .models import MISSING_VALUE


def missing_if_blank(value: str | None) -> str:
    if value is None:
        return MISSING_VALUE
    value = value.strip()
    return value if value else MISSING_VALUE


def strip_nfse_prefix(value: str | None) -> str:
    value = missing_if_blank(value)
    if value == MISSING_VALUE:
        return value
    return value[3:] if value.startswith("NFS") else value


def format_date(value: str | None) -> str:
    value = missing_if_blank(value)
    if value == MISSING_VALUE:
        return value
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return value
    return parsed.strftime("%d/%m/%Y")


def format_datetime(value: str | None) -> str:
    value = missing_if_blank(value)
    if value == MISSING_VALUE:
        return value
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return value
    return parsed.strftime("%d/%m/%Y %H:%M:%S")


def ellipsize(value: str, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    if max_chars <= 3:
        return "." * max_chars
    return f"{value[: max_chars - 3]}..."


def format_cnpj(value: str | None) -> str:
    value = missing_if_blank(value)
    if value == MISSING_VALUE or len(value) != 14 or not value.isdigit():
        return value
    return f"{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}"


def format_cpf(value: str | None) -> str:
    value = missing_if_blank(value)
    if value == MISSING_VALUE or len(value) != 11 or not value.isdigit():
        return value
    return f"{value[:3]}.{value[3:6]}.{value[6:9]}-{value[9:]}"


def format_cep(value: str | None) -> str:
    value = missing_if_blank(value)
    if value == MISSING_VALUE or len(value) != 8 or not value.isdigit():
        return value
    return f"{value[:2]}.{value[2:5]}-{value[5:]}"


def first_present(*values: str | None) -> str:
    for value in values:
        formatted = missing_if_blank(value)
        if formatted != MISSING_VALUE:
            return formatted
    return MISSING_VALUE


def join_present(*values: str | None, sep: str = ", ") -> str:
    present = [value.strip() for value in values if value and value.strip()]
    return sep.join(present) if present else MISSING_VALUE
