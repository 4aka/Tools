#!/usr/bin/env python3
"""
PDF → Markdown converter
Використання:
  python convert.py              # конвертує всі PDF поряд зі скриптом
  python convert.py file.pdf     # конвертує конкретний файл
  python convert.py *.pdf        # кілька файлів
"""

import sys
import os
from pathlib import Path


def convert_pdf(pdf_path: Path) -> bool:
    try:
        from markitdown import MarkItDown
    except ImportError:
        print("❌ markitdown не встановлено. Запусти: pip install markitdown[pdf]")
        sys.exit(1)

    md_path = pdf_path.with_suffix(".md")

    print(f"⏳ Конвертую: {pdf_path.name}", end=" ... ", flush=True)
    try:
        result = MarkItDown().convert(str(pdf_path))
        md_path.write_text(result.text_content, encoding="utf-8")
        print(f"✅ → {md_path.name}")
        return True
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False


def main():
    script_dir = Path(__file__).parent.resolve()

    # Визначаємо список файлів
    if len(sys.argv) > 1:
        files = [Path(f) for f in sys.argv[1:]]
    else:
        files = sorted(script_dir.glob("*.pdf"))

    if not files:
        print("⚠️  PDF файли не знайдено.")
        print(f"   Поклади PDF поряд зі скриптом: {script_dir}")
        return

    total = len(files)
    ok = 0

    for f in files:
        # Якщо відносний шлях — резолвимо від script_dir
        if not f.is_absolute():
            f = script_dir / f

        if not f.exists():
            print(f"⚠️  Файл не знайдено: {f}")
            continue

        if f.suffix.lower() != ".pdf":
            print(f"⚠️  Пропускаю (не PDF): {f.name}")
            continue

        if convert_pdf(f):
            ok += 1

    print()
    print(f"{'✅ Готово' if ok == total else '⚠️  Завершено з помилками'}: {ok}/{total} файлів конвертовано")


if __name__ == "__main__":
    main()
