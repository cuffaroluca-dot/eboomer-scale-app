"""Genera QR code per E-Boomer Scale."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import qrcode
from PIL import Image, ImageDraw, ImageFont


BASE_URL = "https://NOMEAPP.streamlit.app"

DATA_PATH = Path("data") / "participants.csv"
OUTPUT_DIR = Path("qr_codes")
QR_SIZE = 720
LABEL_HEIGHT = 110
PADDING = 36


def build_url(query: str) -> str:
    return f"{BASE_URL.rstrip('/')}{query}"


def load_font(size: int) -> ImageFont.ImageFont:
    for font_name in ["arial.ttf", "DejaVuSans-Bold.ttf"]:
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_qr(url: str) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=16,
        border=3,
    )
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="#0f172a", back_color="white").convert("RGB")
    return image.resize((QR_SIZE, QR_SIZE), Image.Resampling.NEAREST)


def draw_centered_label(draw: ImageDraw.ImageDraw, label: str, y: int, width: int) -> None:
    font = load_font(34)
    text = label
    while draw.textbbox((0, 0), text, font=font)[2] > width - (PADDING * 2) and len(text) > 8:
        text = text[:-2].rstrip() + "..."
    bbox = draw.textbbox((0, 0), text, font=font)
    x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((x, y), text, fill="#0f172a", font=font)


def save_labeled_qr(filename: str, label: str, url: str) -> None:
    qr_image = make_qr(url)
    canvas = Image.new("RGB", (QR_SIZE, QR_SIZE + LABEL_HEIGHT), "white")
    canvas.paste(qr_image, (0, 0))
    draw = ImageDraw.Draw(canvas)
    draw_centered_label(draw, label, QR_SIZE + 24, QR_SIZE)
    canvas.save(OUTPUT_DIR / filename)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    participants = pd.read_csv(DATA_PATH, dtype=str).fillna("")

    links = []

    audience_url = build_url("?group=audience")
    save_labeled_qr("audience.png", "Audience", audience_url)
    links.append(f"Audience: {audience_url}")

    admin_url = build_url("?admin=true")
    save_labeled_qr("admin.png", "Admin - Moderatori", admin_url)
    links.append(f"Admin - Moderatori: {admin_url}")

    faculty = participants[participants["group"] == "faculty"]
    for _, row in faculty.iterrows():
        participant_id = row["participant_id"].strip()
        if not participant_id:
            continue
        display_name = row["display_name"].strip() or participant_id
        url = build_url(f"?group=faculty&id={participant_id}")
        save_labeled_qr(f"{participant_id}.png", display_name, url)
        links.append(f"{display_name} ({participant_id}): {url}")

    (OUTPUT_DIR / "links.txt").write_text("\n".join(links) + "\n", encoding="utf-8")
    print(f"Generati {len(links)} link in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
