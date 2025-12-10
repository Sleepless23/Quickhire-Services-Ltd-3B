from pathlib import Path
import csv

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


def _ensure_parent(path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def save_csv(path: str, fieldnames: list, rows: list):
    """Save rows (list of dict) to CSV. Returns path."""
    _ensure_parent(path)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return path


def save_text(path: str, title: str, lines: list):
    """Save a simple text summary."""
    _ensure_parent(path)
    if not path.lower().endswith(".txt"):
        path = path + ".txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(title + "\n")
        f.write("=" * max(40, len(title)) + "\n\n")
        for ln in lines:
            f.write(ln + "\n")
    return path


def save_pdf(path: str, title: str, lines: list):
    """
    Save a basic PDF using reportlab if available. Otherwise write txt fallback.
    Returns final path.
    """
    _ensure_parent(path)
    if not REPORTLAB_AVAILABLE:
        if not path.lower().endswith(".txt"):
            path = path + ".txt"
        return save_text(path, title, lines)

    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    margin = 36
    y = height - margin

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, title)
    y -= 18
    c.setFont("Helvetica", 10)

    for line in lines:
        while len(line) > 100:
            part = line[:100]
            c.drawString(margin, y, part)
            y -= 12
            line = line[100:]
            if y < margin:
                c.showPage()
                y = height - margin
                c.setFont("Helvetica", 10)
        c.drawString(margin, y, line)
        y -= 12
        if y < margin:
            c.showPage()
            y = height - margin
            c.setFont("Helvetica", 10)

    c.save()
    return path
