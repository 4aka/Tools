# pdf2md

Конвертує PDF → Markdown за допомогою [markitdown](https://github.com/microsoft/markitdown).  
Зберігає `.md` поряд з PDF, з тим же ім'ям.

## Встановлення

```bash
pip install markitdown[pdf]
```

> Python 3.10+ обов'язковий.

## Використання

### Windows — подвійний клік
Поклади PDF поряд зі скриптом → двічі клікни `convert.bat`.

### Командний рядок

```bash
# Всі PDF в папці скрипта
python convert.py

# Конкретний файл
python convert.py report.pdf

# Кілька файлів
python convert.py file1.pdf file2.pdf
```

## Обмеження

- Скановані PDF (без текстового шару) — текст не витягується без OCR.
- Для складних layouts якість може бути нижчою — markitdown орієнтований на LLM-pipeline, не на pixel-perfect конвертацію.
