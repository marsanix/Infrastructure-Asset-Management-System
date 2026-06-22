"""
Annotate IAMS screenshots with red boxes, step numbers, and labels.
Uses Pillow (PIL) — no external dependencies beyond that.

Usage: python annotate_screenshots.py
Output: docs/screenshots/annotated/ folder
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), 'screenshots')
OUTPUT_DIR = os.path.join(SCREENSHOTS_DIR, 'annotated')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Try to load a nice font, fallback to default
def get_font(size=16):
    font_paths = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()

def get_bold_font(size=18):
    font_paths = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return get_font(size)


FONT = get_font(14)
FONT_LABEL = get_font(13)
FONT_BOLD = get_bold_font(16)
FONT_NUM = get_bold_font(20)

RED = (220, 38, 38)
RED_LIGHT = (254, 202, 202, 100)
GREEN = (22, 163, 74)
BLUE = (37, 99, 235)
ORANGE = (234, 88, 12)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def draw_box(draw, box, color=RED, width=3, label=None):
    """Draw a rectangle with optional label."""
    x1, y1, x2, y2 = box
    draw.rectangle([x1, y1, x2, y2], outline=color, width=width)
    if label:
        # Label background
        bbox = draw.textbbox((0, 0), label, font=FONT_LABEL)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        lx, ly = x1, y1 - th - 6
        if ly < 0:
            ly = y2 + 2
        draw.rectangle([lx, ly, lx + tw + 8, ly + th + 4], fill=color)
        draw.text((lx + 4, ly + 2), label, fill=WHITE, font=FONT_LABEL)


def draw_number(draw, pos, number, color=RED):
    """Draw a circled number."""
    x, y = pos
    r = 14
    draw.ellipse([x - r, y - r, x + r, y + r], fill=color, outline=color)
    text = str(number)
    bbox = draw.textbbox((0, 0), text, font=FONT_NUM)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x - tw // 2, y - th // 2 - 2), text, fill=WHITE, font=FONT_NUM)


def draw_arrow(draw, start, end, color=RED, width=3):
    """Draw a line with arrowhead."""
    draw.line([start, end], fill=color, width=width)
    # Arrowhead
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    arrow_len = 12
    for offset in [2.5, -2.5]:
        ax = end[0] - arrow_len * math.cos(angle + offset * 0.3)
        ay = end[1] - arrow_len * math.sin(angle + offset * 0.3)
        draw.line([end, (ax, ay)], fill=color, width=width)


def annotate_login(img):
    """Annotate login page screenshot."""
    draw = ImageDraw.Draw(img)
    w, h = img.size

    # Title
    draw.rectangle([10, 10, 350, 40], fill=RED)
    draw.text((18, 14), "HALAMAN LOGIN — Step-by-step", fill=WHITE, font=FONT_BOLD)

    # Find approximate positions based on typical 1920x1080 layout
    # Email field area (roughly center of page)
    cx, cy = w // 2, h // 2
    # These are approximate — adjust based on actual screenshot size

    # Step numbers and labels
    draw_number(draw, (cx - 180, cy - 80), 1, BLUE)
    draw.text((cx - 160, cy - 90), "Isi Email", fill=BLUE, font=FONT_BOLD)

    draw_number(draw, (cx - 180, cy + 10), 2, BLUE)
    draw.text((cx - 160, cy + 0), "Isi Password", fill=BLUE, font=FONT_BOLD)

    draw_number(draw, (cx - 180, cy + 100), 3, GREEN)
    draw.text((cx - 160, cy + 90), "Klik Masuk", fill=GREEN, font=FONT_BOLD)

    return img


def annotate_dashboard(img):
    """Annotate dashboard with KPI labels."""
    draw = ImageDraw.Draw(img)
    w, h = img.size

    draw.rectangle([10, 10, 300, 40], fill=RED)
    draw.text((18, 14), "DASHBOARD — Ringkasan KPI", fill=WHITE, font=FONT_BOLD)

    # Sidebar indicator
    draw_box(draw, (0, 60, 200, h - 20), color=BLUE, width=2, label="Sidebar Menu")

    # Top-right area (theme/language buttons)
    draw_box(draw, (w - 200, 50, w - 10, 85), color=ORANGE, width=2, label="Theme & Language")

    return img


def annotate_assets_list(img):
    """Annotate assets list page."""
    draw = ImageDraw.Draw(img)
    w, h = img.size

    draw.rectangle([10, 10, 350, 40], fill=RED)
    draw.text((18, 14), "HALAMAN ASET — Daftar Perangkat", fill=WHITE, font=FONT_BOLD)

    # Top button area
    draw_number(draw, (w - 120, 145), 1, GREEN)
    draw.text((w - 250, 130), "Tambah Aset", fill=GREEN, font=FONT_BOLD)

    # Filter area
    draw_box(draw, (210, 175, w - 20, 230), color=ORANGE, width=2, label="Filter & Search")

    # Table area
    draw_box(draw, (210, 240, w - 20, h - 50), color=BLUE, width=2, label="Tabel Data Aset")

    return img


def annotate_assets_form(img):
    """Annotate add asset form."""
    draw = ImageDraw.Draw(img)
    w, h = img.size

    draw.rectangle([10, 10, 380, 40], fill=RED)
    draw.text((18, 14), "FORM TAMBAH ASET — Isi semua field", fill=WHITE, font=FONT_BOLD)

    return img


def annotate_incidents_list(img):
    """Annotate incidents list."""
    draw = ImageDraw.Draw(img)
    w, h = img.size

    draw.rectangle([10, 10, 400, 40], fill=RED)
    draw.text((18, 14), "HALAMAN INSIDEN — Daftar Gangguan", fill=WHITE, font=FONT_BOLD)

    draw_number(draw, (w - 120, 145), 1, GREEN)
    draw.text((w - 260, 130), "Insiden Baru", fill=GREEN, font=FONT_BOLD)

    return img


def annotate_audit_logs(img):
    """Annotate audit logs."""
    draw = ImageDraw.Draw(img)
    w, h = img.size

    draw.rectangle([10, 10, 450, 40], fill=RED)
    draw.text((18, 14), "AUDIT LOG — Catatan Aktivitas Sistem", fill=WHITE, font=FONT_BOLD)

    # Filter area
    draw_box(draw, (210, 145, w - 20, 260), color=ORANGE, width=2, label="Filter: Action & Status")

    # Table
    draw_box(draw, (210, 270, w - 20, h - 50), color=BLUE, width=2, label="Log (append-only, tidak bisa dihapus)")

    return img


def annotate_users(img):
    """Annotate users page."""
    draw = ImageDraw.Draw(img)
    w, h = img.size

    draw.rectangle([10, 10, 400, 40], fill=RED)
    draw.text((18, 14), "PENGGUNA — Admin Only", fill=WHITE, font=FONT_BOLD)

    draw_number(draw, (w - 120, 145), 1, GREEN)
    draw.text((w - 270, 130), "Tambah User", fill=GREEN, font=FONT_BOLD)

    return img


def annotate_reports(img):
    """Annotate reports page."""
    draw = ImageDraw.Draw(img)
    w, h = img.size

    draw.rectangle([10, 10, 400, 40], fill=RED)
    draw.text((18, 14), "LAPORAN — Warranty Watch", fill=WHITE, font=FONT_BOLD)

    return img


def annotate_dark_mode(img):
    """Annotate dark mode screenshot."""
    draw = ImageDraw.Draw(img)
    w, h = img.size

    draw.rectangle([10, 10, 320, 40], fill=ORANGE)
    draw.text((18, 14), "DARK MODE — Tampilan Gelap", fill=WHITE, font=FONT_BOLD)

    return img


def annotate_english(img):
    """Annotate english screenshot."""
    draw = ImageDraw.Draw(img)
    w, h = img.size

    draw.rectangle([10, 10, 350, 40], fill=BLUE)
    draw.text((18, 14), "ENGLISH — Multi-language", fill=WHITE, font=FONT_BOLD)

    return img


def annotate_generic(img, title):
    """Generic annotation — just add a title banner."""
    draw = ImageDraw.Draw(img)
    w, h = img.size
    tw = min(len(title) * 10 + 30, w - 20)
    draw.rectangle([10, 10, tw, 40], fill=RED)
    draw.text((18, 14), title, fill=WHITE, font=FONT_BOLD)
    return img


# ═══════════════════════════════════════════════════════════════
# MAIN: Process all screenshots
# ═══════════════════════════════════════════════════════════════

ANNOTATIONS = {
    '01-landing-page.png': ('LANDING PAGE — Halaman Publik', None),
    '02-login-page.png': ('', annotate_login),
    '02b-login-filled.png': ('LOGIN — Form Terisi (Demo Admin)', None),
    '03-dashboard.png': ('', annotate_dashboard),
    '04-assets-list.png': ('', annotate_assets_list),
    '04b-assets-add-form.png': ('', annotate_assets_form),
    '04c-assets-edit-form.png': ('FORM EDIT ASET', None),
    '04d-assets-filter-active.png': ('FILTER AKTIF — Status: Active', None),
    '04e-assets-checkout-history.png': ('RIWAYAT CHECKOUT — Siapa Pernah Pakai', None),
    '05-incidents-list.png': ('', annotate_incidents_list),
    '05b-incidents-add-form.png': ('FORM INSIDEN BARU', None),
    '06-problems-list.png': ('HALAMAN PROBLEM — Root Cause Analysis', None),
    '06b-problems-add-form.png': ('FORM PROBLEM BARU', None),
    '07-requests-list.png': ('HALAMAN PERMINTAAN — 7 Tipe Request', None),
    '07b-requests-add-form.png': ('FORM BUAT REQUEST', None),
    '08-changes-list.png': ('HALAMAN PERUBAHAN — Approval Workflow', None),
    '08b-changes-add-form.png': ('FORM BUAT PERUBAHAN', None),
    '09-licenses-list.png': ('LISENSI SOFTWARE — Tracking Expiry', None),
    '10-master-data.png': ('DATA MASTER — Admin Only', None),
    '10b-master-data-add-form.png': ('FORM TAMBAH DATA MASTER', None),
    '11-users-roles.png': ('', annotate_users),
    '11b-users-add-form.png': ('FORM TAMBAH USER', None),
    '12-audit-logs.png': ('', annotate_audit_logs),
    '13-reports.png': ('', annotate_reports),
    '14-dashboard-dark-mode.png': ('', annotate_dark_mode),
    '15-dashboard-english.png': ('', annotate_english),
}


def process():
    count = 0
    for filename, (title, custom_fn) in ANNOTATIONS.items():
        src = os.path.join(SCREENSHOTS_DIR, filename)
        if not os.path.exists(src):
            print(f"  SKIP (not found): {filename}")
            continue

        img = Image.open(src).convert('RGBA')

        # Create overlay for semi-transparent elements
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))

        # Convert to RGB for drawing
        img_rgb = img.convert('RGB')

        if custom_fn:
            img_rgb = custom_fn(img_rgb)
        elif title:
            img_rgb = annotate_generic(img_rgb, title)

        # Save
        dst = os.path.join(OUTPUT_DIR, filename)
        img_rgb.save(dst, 'PNG', optimize=True)
        count += 1
        print(f"  ✅ {filename}")

    print(f"\nDone! {count} annotated screenshots saved to: {OUTPUT_DIR}")


if __name__ == '__main__':
    print("Annotating IAMS screenshots...")
    print(f"Source: {SCREENSHOTS_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print()
    process()
