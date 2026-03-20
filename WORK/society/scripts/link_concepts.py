#!/usr/bin/env python3
"""
Скрипт для автоматической расстановки перекрёстных ссылок между статьями.
Работает с новой структурой concepts.json (с секциями).

Использование: python link_concepts.py <articles_dir> <concepts_json>
Пример: python link_concepts.py ../../WEB/society/concepts ../concepts.json
"""

import json
import re
import os
import sys


def load_concepts(json_path):
    """Загружает список понятий из concepts.json (структура с секциями)."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    concepts = {}
    for section in data.get("sections", []):
        for concept in section.get("concepts", []):
            title = concept["title"]
            filename = concept["file"]
            concepts[title] = filename
    return concepts


def make_link_pattern(title):
    """
    Создаёт регулярное выражение для поиска слова/словосочетания.
    Ищет точное совпадение с возможными окончаниями.
    """
    # Экранируем спецсимволы
    escaped = re.escape(title)
    return r"\b" + escaped + r"(?:\w+)?\b"


def replace_with_links(text, concepts, current_filename):
    """
    Заменяет первое упоминание каждого понятия на Markdown-ссылку.
    Не создаёт ссылку на саму себя.
    """
    # Сортируем по длине (сначала длинные фразы)
    sorted_concepts = sorted(concepts.items(), key=lambda x: len(x[0]), reverse=True)

    replacements = 0
    for title, filename in sorted_concepts:
        if filename == current_filename:
            continue

        pattern = make_link_pattern(title)

        def repl(match, fn=filename):
            word = match.group(0)
            return f"[{word}]({fn})"

        new_text, count = re.subn(pattern, repl, text, count=1, flags=re.IGNORECASE)
        if count > 0:
            text = new_text
            replacements += 1

    return text, replacements


def process_directory(articles_dir, concepts_json):
    """Обрабатывает все .md файлы в директории."""
    concepts = load_concepts(concepts_json)

    print(f"Загружено понятий: {len(concepts)}\n")

    processed = 0
    total_links = 0
    for filename in sorted(os.listdir(articles_dir)):
        if not filename.endswith(".md"):
            continue

        filepath = os.path.join(articles_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        new_text, count = replace_with_links(text, concepts, filename)

        if new_text != text:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_text)
            print(f"  [OK] {filename} — {count} ссылок добавлено")
        else:
            print(f"  [--] {filename} — все ссылки уже на месте")

        processed += 1
        total_links += count

    print(f"\nОбработано файлов: {processed}")
    print(f"Добавлено ссылок: {total_links}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: link_concepts.py <articles_dir> <concepts_json>")
        print("Пример: python link_concepts.py ../../WEB/society/concepts ../concepts.json")
        sys.exit(1)

    articles_dir = sys.argv[1]
    concepts_json = sys.argv[2]

    if not os.path.isdir(articles_dir):
        print(f"Ошибка: директория '{articles_dir}' не найдена")
        sys.exit(1)

    if not os.path.isfile(concepts_json):
        print(f"Ошибка: файл '{concepts_json}' не найден")
        sys.exit(1)

    print(f"Директория статей: {articles_dir}")
    print(f"Файл понятий: {concepts_json}\n")

    process_directory(articles_dir, concepts_json)
