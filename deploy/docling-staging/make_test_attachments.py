"""Generate synthetic attachments for the Docling staging acceptance."""
import argparse
from pathlib import Path

from openpyxl import Workbook
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas


QUANTITY = 3
UNIT_PRICE = 1250
TOTAL = QUANTITY * UNIT_PRICE
LINES = (
    "COTIZACION SINTETICA - DOC-204",
    "Modelo: Terma T-200",
    f"Cantidad: {QUANTITY}",
    "Moneda: PEN",
    f"Precio unitario: {UNIT_PRICE:.2f}",
    f"Importe total: {TOTAL:.2f}",
)


def write_pdfs(folder):
    width, height = A4
    text_pdf = Canvas(str(folder / "cotizacion-texto.pdf"), pagesize=A4)
    for row, line in enumerate(LINES):
        text_pdf.drawString(72, height - 90 - row * 24, line)
    text_pdf.save()

    pixels_per_point = 3
    raster = Image.new("RGB", (round(width * pixels_per_point),
                               round(height * pixels_per_point)), "white")
    draw = ImageDraw.Draw(raster)
    font = ImageFont.truetype("DejaVuSans.ttf", 36)
    for row, line in enumerate(LINES):
        draw.text((216, 234 + row * 72), line, fill="black", font=font)
    scanned_pdf = Canvas(str(folder / "cotizacion-escaneada.pdf"), pagesize=A4)
    scanned_pdf.drawImage(ImageReader(raster), 0, 0, width, height)
    scanned_pdf.save()


def write_workbook(folder):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Cotizacion"
    sheet.append(["Referencia", "Modelo", "Cantidad", "Moneda", "Precio unitario", "Total"])
    sheet.append(["DOC-204", "T-200", QUANTITY, "PEN", UNIT_PRICE, TOTAL])
    sheet["E2"].number_format = "0.00"
    sheet["F2"].number_format = "0.00"
    workbook.save(folder / "cotizacion.xlsx")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    write_pdfs(args.output)
    write_workbook(args.output)


if __name__ == "__main__":
    main()
