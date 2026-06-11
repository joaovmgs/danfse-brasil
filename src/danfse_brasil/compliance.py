"""Runtime checks for normative DANFSe requirements."""

from __future__ import annotations

import subprocess


REQUIRED_FONTS = ("Arial", "Microsoft Sans Serif")


def font_warnings() -> list[str]:
    warnings: list[str] = []
    for font in REQUIRED_FONTS:
        matched = _fc_match(font)
        if matched is None:
            warnings.append(f"Nao foi possivel validar a fonte obrigatoria: {font}.")
            continue
        if f'"{font}"' not in matched:
            warnings.append(f'Fonte obrigatoria "{font}" nao instalada; fontconfig retornou: {matched}')
    return warnings


def _fc_match(font: str) -> str | None:
    try:
        result = subprocess.run(
            ["fc-match", font],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()
