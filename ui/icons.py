"""
Vector Icon & Illustration Generator for PDF Unlocker Desktop Windows.
Uses 4x supersampled PIL anti-aliased vector drawing to produce crisp CTkImage icons
across all Windows DPI scales without relying on OS-dependent Unicode emojis.
"""

import math
from typing import Dict, Tuple
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

_ICON_CACHE: Dict[Tuple[str, int, str, str], ctk.CTkImage] = {}


def _hex_to_rgba(hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


def get_icon(name: str, size: int = 20, color: str = "#F3F7FF", bg_color: str = "") -> ctk.CTkImage:
    """Returns a cached anti-aliased vector CTkImage of the given size and color."""
    key = (name, size, color, bg_color)
    if key in _ICON_CACHE:
        return _ICON_CACHE[key]

    scale = 4
    w = size * scale
    h = size * scale
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    fg = _hex_to_rgba(color)
    stroke = max(2, int(round(2.1 * scale)))

    if bg_color:
        bg = _hex_to_rgba(bg_color)
        r = int(w * 0.28)
        draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=bg)

    pad = w * 0.16

    if name == "home":
        # Roof + house body
        pts = [(w * 0.5, pad), (w - pad, h * 0.48), (w * 0.82, h * 0.48),
               (w * 0.82, h - pad), (w * 0.18, h - pad), (w * 0.18, h * 0.48), (pad, h * 0.48)]
        draw.polygon(pts, outline=fg, width=stroke)
        draw.rectangle((w * 0.42, h * 0.60, w * 0.58, h - pad), fill=fg)

    elif name == "unlock":
        # Open padlock shackle + body
        draw.arc((w * 0.28, pad, w * 0.72, h * 0.56), start=180, end=335, fill=fg, width=stroke)
        draw.line((w * 0.28, h * 0.34, w * 0.28, h * 0.48), fill=fg, width=stroke)
        draw.rounded_rectangle((w * 0.20, h * 0.46, w * 0.80, h - pad), radius=int(w * 0.10), outline=fg, width=stroke)
        draw.ellipse((w * 0.45, h * 0.62, w * 0.55, h * 0.72), fill=fg)

    elif name == "recovery":
        # Magnifying glass
        r_end = w * 0.66
        draw.ellipse((pad, pad, r_end, r_end), outline=fg, width=stroke)
        draw.line((w * 0.58, h * 0.58, w - pad, h - pad), fill=fg, width=int(stroke * 1.2))

    elif name == "batch":
        # Stacked list / multiple files card
        draw.rounded_rectangle((pad, pad + h * 0.04, w - pad, h - pad), radius=int(w * 0.10), outline=fg, width=stroke)
        for y_frac in (0.36, 0.52, 0.68):
            draw.line((w * 0.30, h * y_frac, w * 0.72, h * y_frac), fill=fg, width=stroke)

    elif name == "history":
        # Clock face + hands
        draw.ellipse((pad, pad, w - pad, h - pad), outline=fg, width=stroke)
        draw.line((w * 0.5, h * 0.30, w * 0.5, h * 0.52), fill=fg, width=stroke)
        draw.line((w * 0.5, h * 0.52, w * 0.66, h * 0.60), fill=fg, width=stroke)

    elif name in ("settings", "gear"):
        # Gear cog with 8 teeth and center hole
        cx, cy = w * 0.5, h * 0.5
        r_outer = w * 0.36
        r_inner = w * 0.26
        for i in range(8):
            ang = i * (math.pi / 4.0)
            x1 = cx + math.cos(ang) * (r_inner - stroke * 0.3)
            y1 = cy + math.sin(ang) * (r_inner - stroke * 0.3)
            x2 = cx + math.cos(ang) * r_outer
            y2 = cy + math.sin(ang) * r_outer
            draw.line((x1, y1, x2, y2), fill=fg, width=int(stroke * 1.35))
        draw.ellipse((cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner), outline=fg, width=stroke)
        r_hole = w * 0.11
        draw.ellipse((cx - r_hole, cy - r_hole, cx + r_hole, cy + r_hole), outline=fg, width=stroke)

    elif name in ("help", "info_circle"):
        draw.ellipse((pad, pad, w - pad, h - pad), outline=fg, width=stroke)
        r_dot = max(2, int(w * 0.05))
        draw.ellipse((w * 0.5 - r_dot, h * 0.30 - r_dot, w * 0.5 + r_dot, h * 0.30 + r_dot), fill=fg)
        draw.line((w * 0.5, h * 0.44, w * 0.5, h * 0.72), fill=fg, width=stroke)

    elif name == "file_doc":
        # Document with folded top-right corner
        fold = w * 0.22
        pts = [(w * 0.22, pad), (w * 0.78 - fold, pad), (w * 0.78, pad + fold),
               (w * 0.78, h - pad), (w * 0.22, h - pad)]
        draw.polygon(pts, outline=fg, width=stroke)
        draw.line((w * 0.78 - fold, pad, w * 0.78 - fold, pad + fold), fill=fg, width=stroke)
        draw.line((w * 0.78 - fold, pad + fold, w * 0.78, pad + fold), fill=fg, width=stroke)
        draw.line((w * 0.34, h * 0.54, w * 0.66, h * 0.54), fill=fg, width=stroke)
        draw.line((w * 0.34, h * 0.68, w * 0.58, h * 0.68), fill=fg, width=stroke)

    elif name in ("folder", "upload_folder"):
        # Folder tab + body
        pts = [(pad, h * 0.26), (w * 0.40, h * 0.26), (w * 0.48, h * 0.35),
               (w - pad, h * 0.35), (w - pad, h * 0.80), (pad, h * 0.80)]
        draw.polygon(pts, outline=fg, width=stroke)
        if name == "upload_folder":
            draw.line((w * 0.5, h * 0.68, w * 0.5, h * 0.45), fill=fg, width=stroke)
            draw.line((w * 0.40, h * 0.54, w * 0.5, h * 0.44), fill=fg, width=stroke)
            draw.line((w * 0.60, h * 0.54, w * 0.5, h * 0.44), fill=fg, width=stroke)

    elif name == "play":
        pts = [(w * 0.28, h * 0.22), (w * 0.28, h * 0.78), (w * 0.78, h * 0.50)]
        draw.polygon(pts, fill=fg)

    elif name == "stop":
        draw.rounded_rectangle((w * 0.25, h * 0.25, w * 0.75, h * 0.75), radius=int(w * 0.08), fill=fg)

    elif name == "check_circle":
        draw.ellipse((pad * 0.7, pad * 0.7, w - pad * 0.7, h - pad * 0.7), fill=_hex_to_rgba(color, 45), outline=fg, width=stroke)
        draw.line((w * 0.30, h * 0.52, w * 0.45, h * 0.66), fill=fg, width=int(stroke * 1.15))
        draw.line((w * 0.44, h * 0.66, w * 0.72, h * 0.36), fill=fg, width=int(stroke * 1.15))

    elif name == "error_circle":
        draw.ellipse((pad * 0.7, pad * 0.7, w - pad * 0.7, h - pad * 0.7), fill=_hex_to_rgba(color, 45), outline=fg, width=stroke)
        draw.line((w * 0.34, h * 0.34, w * 0.66, h * 0.66), fill=fg, width=stroke)
        draw.line((w * 0.66, h * 0.34, w * 0.34, h * 0.66), fill=fg, width=stroke)

    elif name == "log_list":
        draw.rounded_rectangle((pad, pad, w - pad, h - pad), radius=int(w * 0.12), outline=fg, width=stroke)
        for y_f in (0.35, 0.50, 0.65):
            draw.line((w * 0.30, h * y_f, w * 0.72, h * y_f), fill=fg, width=stroke)

    elif name == "copy":
        draw.rounded_rectangle((w * 0.32, h * 0.30, w * 0.80, h * 0.82), radius=int(w * 0.08), outline=fg, width=stroke)
        draw.line((w * 0.20, h * 0.66, w * 0.20, h * 0.20), fill=fg, width=stroke)
        draw.line((w * 0.20, h * 0.20, w * 0.64, h * 0.20), fill=fg, width=stroke)

    elif name == "save":
        # Shield / download arrow
        draw.line((w * 0.5, h * 0.20, w * 0.5, h * 0.64), fill=fg, width=stroke)
        draw.line((w * 0.34, h * 0.48, w * 0.5, h * 0.64), fill=fg, width=stroke)
        draw.line((w * 0.66, h * 0.48, w * 0.5, h * 0.64), fill=fg, width=stroke)
        draw.line((w * 0.24, h * 0.78, w * 0.76, h * 0.78), fill=fg, width=stroke)

    elif name == "crown":
        pts = [
            (w * 0.18, h * 0.74),
            (w * 0.18, h * 0.34),
            (w * 0.36, h * 0.52),
            (w * 0.50, h * 0.26),
            (w * 0.64, h * 0.52),
            (w * 0.82, h * 0.34),
            (w * 0.82, h * 0.74),
        ]
        draw.polygon(pts, fill=fg)

    elif name == "num_pad":
        # 3x3 keypad dots
        r_d = w * 0.065
        for rx in (0.30, 0.50, 0.70):
            for ry in (0.30, 0.50, 0.70):
                cx, cy = w * rx, h * ry
                draw.ellipse((cx - r_d, cy - r_d, cx + r_d, cy + r_d), fill=fg)

    elif name == "key_star":
        # Key icon
        draw.ellipse((w * 0.18, h * 0.32, w * 0.50, h * 0.64), outline=fg, width=stroke)
        draw.line((w * 0.50, h * 0.48, w * 0.84, h * 0.48), fill=fg, width=stroke)
        draw.line((w * 0.70, h * 0.48, w * 0.70, h * 0.62), fill=fg, width=stroke)
        draw.line((w * 0.82, h * 0.48, w * 0.82, h * 0.62), fill=fg, width=stroke)

    elif name == "mask_code":
        # Lock with asterisk / mask bar
        draw.rounded_rectangle((pad, h * 0.30, w - pad, h * 0.70), radius=int(w * 0.10), outline=fg, width=stroke)
        for rx in (0.34, 0.50, 0.66):
            r_d = w * 0.05
            draw.ellipse((w * rx - r_d, h * 0.50 - r_d, w * rx + r_d, h * 0.50 + r_d), fill=fg)

    elif name == "trash":
        draw.line((w * 0.24, h * 0.28, w * 0.76, h * 0.28), fill=fg, width=stroke)
        draw.rectangle((w * 0.30, h * 0.28, w * 0.70, h * 0.80), outline=fg, width=stroke)
        draw.line((w * 0.42, h * 0.20, w * 0.58, h * 0.20), fill=fg, width=stroke)

    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    ctk_img = ctk.CTkImage(light_image=resized, dark_image=resized, size=(size, size))
    _ICON_CACHE[key] = ctk_img
    return ctk_img


def create_app_logo_image(size: int = 48) -> ctk.CTkImage:
    """
    Creates the Section 5.2 TopBar logo:
    48x48 rounded blue square (#0876E8, radius 14px) with crisp white vector padlock.
    """
    key = ("__app_logo__", size, "#0876E8", "#FFFFFF")
    if key in _ICON_CACHE:
        return _ICON_CACHE[key]

    scale = 4
    w = size * scale
    h = size * scale
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded square #0876E8 with 14px radius
    radius = int(14 * (size / 48.0) * scale)
    draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=_hex_to_rgba("#0876E8"))

    # Subtle inner top highlight
    draw.rounded_rectangle(
        (scale, scale, w - 1 - scale, h - 1 - scale),
        radius=max(1, radius - scale),
        outline=(255, 255, 255, 45),
        width=scale
    )

    white = (255, 255, 255, 255)
    shackle_w = int(3.4 * scale * (size / 48.0))

    # Shackle arc
    sx0, sy0, sx1, sy1 = w * 0.33, h * 0.19, w * 0.67, h * 0.54
    draw.arc((sx0, sy0, sx1, sy1), start=180, end=360, fill=white, width=shackle_w)
    draw.line((sx0 + shackle_w * 0.35, (sy0 + sy1) * 0.5, sx0 + shackle_w * 0.35, h * 0.46), fill=white, width=shackle_w)
    draw.line((sx1 - shackle_w * 0.35, (sy0 + sy1) * 0.5, sx1 - shackle_w * 0.35, h * 0.46), fill=white, width=shackle_w)

    # Lock body
    bx0, by0, bx1, by1 = w * 0.25, h * 0.44, w * 0.75, h * 0.80
    draw.rounded_rectangle((bx0, by0, bx1, by1), radius=int(5 * scale * (size / 48.0)), fill=white)

    # Keyhole in blue (#0876E8)
    blue = _hex_to_rgba("#0876E8")
    kr = w * 0.048
    kcx, kcy = w * 0.50, h * 0.58
    draw.ellipse((kcx - kr, kcy - kr, kcx + kr, kcy + kr), fill=blue)
    draw.polygon([(kcx - kr * 0.65, kcy), (kcx + kr * 0.65, kcy), (kcx + kr * 0.9, h * 0.71), (kcx - kr * 0.9, h * 0.71)], fill=blue)

    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    ctk_img = ctk.CTkImage(light_image=resized, dark_image=resized, size=(size, size))
    _ICON_CACHE[key] = ctk_img
    return ctk_img


def create_pdf_hero_image(width: int = 110, height: int = 118) -> ctk.CTkImage:
    """
    Creates the Section 7.2 Hero Card illustration:
    Red 3D PDF document with folded corner, 'PDF' text and white padlock on the bottom-right,
    matching the reference mockup.
    """
    key = ("__pdf_hero__", width, str(height), "")
    if key in _ICON_CACHE:
        return _ICON_CACHE[key]

    scale = 3
    w = width * scale
    h = height * scale
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Soft blue glow pedestal at bottom
    draw.ellipse((w * 0.08, h * 0.78, w * 0.92, h * 0.97), fill=(22, 135, 248, 55))
    draw.ellipse((w * 0.16, h * 0.82, w * 0.84, h * 0.94), fill=(35, 181, 255, 85))

    # Back shadow sheet
    draw.rounded_rectangle(
        (w * 0.16, h * 0.10, w * 0.78, h * 0.86),
        radius=int(12 * scale),
        fill=(140, 18, 38, 180)
    )

    # Main red PDF sheet with folded top-right corner
    x0, y0, x1, y1 = int(w * 0.12), int(h * 0.07), int(w * 0.76), int(h * 0.85)
    fold = int(w * 0.18)
    r = int(10 * scale)

    # Fill main body using polygon + rounded corners
    draw.rounded_rectangle((x0, y0, x1, y1), radius=r, fill=(229, 37, 53, 255))
    # Cut out top-right triangle for fold
    draw.polygon([(x1 - fold, y0), (x1 + 2, y0), (x1 + 2, y0 + fold)], fill=(16, 43, 97, 0))
    # Draw folded flap
    draw.polygon(
        [(x1 - fold, y0), (x1 - fold, y0 + fold), (x1, y0 + fold)],
        fill=(255, 115, 128, 255)
    )

    # Subtle document lines at top
    draw.rounded_rectangle((x0 + w * 0.08, y0 + h * 0.14, x0 + w * 0.34, y0 + h * 0.18), radius=scale * 2, fill=(255, 255, 255, 110))
    draw.rounded_rectangle((x0 + w * 0.08, y0 + h * 0.22, x0 + w * 0.44, y0 + h * 0.25), radius=scale * 2, fill=(255, 255, 255, 75))

    # Bold "PDF" text positioned cleanly to the left of the padlock
    try:
        font = ImageFont.truetype("segoeuib.ttf", int(19 * scale))
    except Exception:
        font = ImageFont.load_default()
    draw.text((x0 + w * 0.06, y0 + h * 0.36), "PDF", fill=(255, 255, 255, 255), font=font)

    # White padlock badge at bottom-right of PDF icon
    lx0, ly0, lx1, ly1 = int(w * 0.58), int(h * 0.58), int(w * 0.86), int(h * 0.85)
    sh_w = int(3.2 * scale)
    draw.arc((lx0 + w * 0.05, ly0 - h * 0.13, lx1 - w * 0.05, ly0 + h * 0.10), start=180, end=360, fill=(255, 255, 255, 255), width=sh_w)
    draw.rounded_rectangle((lx0, ly0, lx1, ly1), radius=int(5 * scale), fill=(255, 255, 255, 255))
    # Keyhole inside white padlock
    kcx = (lx0 + lx1) * 0.5
    kcy = ly0 + (ly1 - ly0) * 0.45
    kr = w * 0.028
    red_hole = (200, 28, 45, 255)
    draw.ellipse((kcx - kr, kcy - kr, kcx + kr, kcy + kr), fill=red_hole)
    draw.polygon([(kcx - kr * 0.6, kcy), (kcx + kr * 0.6, kcy), (kcx + kr * 0.85, ly1 - h * 0.05), (kcx - kr * 0.85, ly1 - h * 0.05)], fill=red_hole)

    resized = img.resize((width, height), Image.Resampling.LANCZOS)
    ctk_img = ctk.CTkImage(light_image=resized, dark_image=resized, size=(width, height))
    _ICON_CACHE[key] = ctk_img
    return ctk_img
