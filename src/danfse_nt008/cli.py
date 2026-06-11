"""Command line interface for DANFSe generation."""

from __future__ import annotations

import argparse
from pathlib import Path

from .compliance import font_warnings
from .html import render_danfse_html
from .pdf import render_danfse_pdf
from .validation import validate_danfse_data
from .xml import parse_danfse


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera o DANFSe conforme a NT 008.")
    parser.add_argument("xml", type=Path, help="Arquivo XML da NFS-e.")
    parser.add_argument("-o", "--output", type=Path, default=Path("danfse-header.pdf"))
    parser.add_argument(
        "--strict-fonts",
        action="store_true",
        help="Falha se Arial e Microsoft Sans Serif nao estiverem disponiveis.",
    )
    args = parser.parse_args()

    warnings = font_warnings()
    if args.strict_fonts and warnings:
        for warning in warnings:
            print(f"ERRO: {warning}")
        raise SystemExit(2)
    for warning in warnings:
        print(f"AVISO: {warning}")

    data = parse_danfse(args.xml)
    issues = validate_danfse_data(data)
    if issues:
        for issue in issues:
            print(f"ERRO: {issue.code}: {issue.message}")
        raise SystemExit(3)

    if args.output.suffix.lower() == ".pdf":
        render_danfse_pdf(data, args.output)
    else:
        args.output.write_text(render_danfse_html(data), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
