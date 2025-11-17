from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Image as RLImage,
    Spacer,
    Paragraph,
    Table,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def combine_layers(layer_paths, output_path="karte_final.png"):
    """
    Kombiniert mehrere PNG-Layer (sichtbare Ebenen) zu einer fertigen Karte.
    Die Reihenfolge in layer_paths bestimmt die z-Reihenfolge.
    """
    if not layer_paths:
        raise ValueError("Keine Layer übergeben!")

    base = Image.open(layer_paths[0]).convert("RGBA")
    width, height = base.size

    for layer_path in layer_paths[1:]:
        layer = Image.open(layer_path).convert("RGBA").resize((width, height))
        base = Image.alpha_composite(base, layer)

    base.save(output_path)
    return output_path


def create_pdf(map_image_path, legend_items, pdf_path="Analysekarte.pdf", title="Analysekarte"):
    """
    Erstellt ein PDF:
    - Seite 1: Fertige Karte
    - Seite 2+: Legende in zwei Spalten

    legend_items = [
        (label, icon_path, color_hex, is_line)
    ]
    """
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    page_width, page_height = A4

    # Seite 1: Titel + Karte
    story.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
    story.append(Spacer(1, 10))

    img = Image.open(map_image_path)
    w, h = img.size
    scale = min((page_width - 20 * mm) / w, (page_height - 40 * mm) / h)

    story.append(RLImage(map_image_path, w * scale, h * scale))
    story.append(Spacer(1, 20))
    story.append(PageBreak())

    # Legendenüberschrift
    story.append(Paragraph("<b>Legende</b>", styles["Heading1"]))
    story.append(Spacer(1, 6))

    table_data = []
    row = []

    for (label, icon, color, is_line) in legend_items:
        if icon:
            cell = RLImage(icon, 10 * mm, 10 * mm)
        else:
            c = colors.HexColor(color) if color else colors.black
            height = 2 * mm if is_line else 6 * mm
            cell = Table([[ "" ]], colWidths=[12 * mm], rowHeights=[height])
            cell.setStyle([('BACKGROUND', (0, 0), (0, 0), c)])

        row.append([cell, Paragraph(label, styles["Normal"])])

        if len(row) == 2:
            table_data.append(row)
            row = []

    if row:
        table_data.append(row)

    table = Table(table_data, colWidths=[14 * mm, 70 * mm, 14 * mm, 70 * mm])
    table.setStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ])

    story.append(table)

    doc.build(story)
    return pdf_path
