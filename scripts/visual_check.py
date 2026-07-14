"""Generate and render a DANFSe sample for visual inspection."""

from __future__ import annotations

import argparse
from pathlib import Path

from danfse_brasil import parse_danfse, render_danfse_pdf, validate_danfse_data
from danfse_brasil.constants import DEFAULT_VISUAL_CHECK_OUTPUT_DIR, DEFAULT_VISUAL_CHECK_XML


A4_WIDTH_PT = 595.28
A4_HEIGHT_PT = 841.89
PAGE_TOLERANCE_PT = 2.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera PDF e PNG de inspecao visual do DANFSe.")
    parser.add_argument("xml", type=Path, nargs="?", default=DEFAULT_VISUAL_CHECK_XML, help="XML da NFS-e.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_VISUAL_CHECK_OUTPUT_DIR, help="Diretorio dos artefatos.")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = args.output_dir / "danfse-visual-check.pdf"
    png_path = args.output_dir / "danfse-visual-check-page1.png"

    data = parse_danfse(args.xml)
    issues = validate_danfse_data(data)
    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity != "error"]

    for issue in warnings:
        print(f"AVISO: {issue.code}: {issue.message}")
    if errors:
        for issue in errors:
            print(f"ERRO: {issue.code}: {issue.message}")
        raise SystemExit(3)

    render_danfse_pdf(data, pdf_path)
    print(f"PDF: {pdf_path}")

    try:
        import fitz
    except ImportError:
        print("PNG: instale PyMuPDF ou rode com: uv run --with pymupdf python scripts/visual_check.py")
        return

    doc = fitz.open(pdf_path)
    if doc.page_count != 1:
        raise SystemExit(f"ERRO: esperado PDF com 1 pagina, encontrado {doc.page_count}.")

    page = doc[0]
    width_ok = abs(page.rect.width - A4_WIDTH_PT) <= PAGE_TOLERANCE_PT
    height_ok = abs(page.rect.height - A4_HEIGHT_PT) <= PAGE_TOLERANCE_PT
    if not width_ok or not height_ok:
        raise SystemExit(
            "ERRO: pagina fora do tamanho A4 esperado "
            f"({page.rect.width:.2f} x {page.rect.height:.2f} pt)."
        )

    pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    pixmap.save(png_path)
    print(f"PNG: {png_path}")
    print(f"Paginas: {doc.page_count}")
    print(f"Tamanho pagina: {page.rect.width:.2f} x {page.rect.height:.2f} pt")


if __name__ == "__main__":
    main()
