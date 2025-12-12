from pathlib import Path
import csv
import os
from tkinter import Tk, filedialog

try:
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


def _ensure_parent(path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def get_downloads_folder():
    """Get the user's Downloads folder path"""
    home = Path.home()
    downloads = home / "Downloads"
    if not downloads.exists():
        downloads.mkdir(parents=True, exist_ok=True)
    return str(downloads)


def get_save_location(default_filename: str, file_type: str = "CSV"):
    """
    Open file dialog to let user choose save location.
    Returns chosen path or None if cancelled.
    
    file_type: "CSV" or "PDF"
    """
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    if file_type.upper() == "CSV":
        filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
        default_ext = ".csv"
    elif file_type.upper() == "PDF":
        filetypes = [("PDF files", "*.pdf"), ("All files", "*.*")]
        default_ext = ".pdf"
    else:
        filetypes = [("All files", "*.*")]
        default_ext = ""
    
    # Start in Downloads folder
    initial_dir = get_downloads_folder()
    
    filepath = filedialog.asksaveasfilename(
        initialdir=initial_dir,
        initialfile=default_filename,
        defaultextension=default_ext,
        filetypes=filetypes,
        title=f"Save {file_type} Report"
    )
    
    root.destroy()
    
    return filepath if filepath else None


def save_csv(path: str, fieldnames: list, rows: list, use_dialog: bool = False):
    """
    Save rows (list of dict) to CSV. Returns path.
    
    If use_dialog=True, opens file dialog for user to choose location.
    Otherwise saves to specified path.
    """
    if use_dialog:
        filename = Path(path).name
        chosen_path = get_save_location(filename, "CSV")
        if not chosen_path:
            print("Save cancelled by user.")
            return None
        path = chosen_path
    
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


from reportlab.pdfbase.pdfmetrics import stringWidth

def save_pdf(path: str, title: str, lines: list, use_dialog: bool = False):
    if use_dialog:
        filename = Path(path).name
        chosen_path = get_save_location(filename, "PDF")
        if not chosen_path:
            print("Save cancelled by user.")
            return None
        path = chosen_path

    _ensure_parent(path)
    if not REPORTLAB_AVAILABLE:
        if not path.lower().endswith(".txt"):
            path = path + ".txt"
        return save_text(path, title, lines)

    c = canvas.Canvas(path, pagesize=landscape(letter))
    width, height = landscape(letter)
    margin = 36
    y = height - margin

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, title)
    y -= 20

    c.setFont("Courier", 10)
    font_name = "Courier"
    font_size = 10

    max_width = width - (margin * 2) 

    for line in lines:
        while stringWidth(line, font_name, font_size) > max_width:
            cut_index = len(line)

            while stringWidth(line[:cut_index], font_name, font_size) > max_width:
                cut_index -= 1

            part = line[:cut_index]
            c.drawString(margin, y, part)
            y -= 12

            line = line[cut_index:] 

            if y < margin:
                c.showPage()
                y = height - margin
                c.setFont(font_name, font_size)

        c.drawString(margin, y, line)
        y -= 12

        if y < margin:
            c.showPage()
            y = height - margin
            c.setFont(font_name, font_size)

    c.save()
    return path


def save_to_downloads(filename: str, content_type: str = "csv"):
    downloads = get_downloads_folder()
    return os.path.join(downloads, filename)