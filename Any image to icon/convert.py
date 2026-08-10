"""
Конвертер зображень в .ico
Шукає всі зображення поряд з собою, конвертує, кладе .ico поряд з оригіналом.
"""

import os
import sys

try:
    from PIL import Image
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
    from PIL import Image


SIZES = [16, 24, 32, 48, 64, 128, 256]
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}

HERE = os.path.dirname(os.path.abspath(__file__))


def convert(path: str) -> str:
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    side = min(w, h)
    img = img.crop(((w - side) // 2, (h - side) // 2,
                    (w + side) // 2, (h + side) // 2))
    out = os.path.splitext(path)[0] + ".ico"
    img.save(out, format="ICO", sizes=[(s, s) for s in SIZES])
    return out


def main():
    images = [
        os.path.join(HERE, f)
        for f in os.listdir(HERE)
        if os.path.splitext(f)[1].lower() in EXTENSIONS
    ]

    if not images:
        print("Зображень не знайдено поряд з скриптом.")
        return

    for path in images:
        try:
            out = convert(path)
            print(f"✓  {os.path.basename(out)}")
        except Exception as e:
            print(f"✗  {os.path.basename(path)}: {e}")

    print(f"\nГотово. Оброблено: {len(images)} файл(ів).")


if __name__ == "__main__":
    main()
