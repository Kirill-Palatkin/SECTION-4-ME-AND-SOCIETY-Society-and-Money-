#!/usr/bin/env python3
"""
Скрипт для выполнения всех SPARQL-запросов к Wikidata и сохранения результатов.
Требует: pip install SPARQLWrapper

Использование: python run_sparql.py
"""

from SPARQLWrapper import SPARQLWrapper, JSON
import json
import os
import glob
import sys

SPARQL_DIR = os.path.join(os.path.dirname(__file__), "..", "sparql")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"


def run_query(query_text):
    """Выполняет один SPARQL-запрос и возвращает результат."""
    sparql = SPARQLWrapper(WIKIDATA_ENDPOINT)
    sparql.setQuery(query_text)
    sparql.setReturnFormat(JSON)
    sparql.setTimeout(30)
    try:
        result = sparql.query().convert()
        return result
    except Exception as e:
        print(f"  Ошибка: {e}")
        return None


def run_all():
    """Выполняет все .sparql файлы из директории sparql/ и сохраняет в data/."""
    os.makedirs(DATA_DIR, exist_ok=True)

    sparql_files = sorted(glob.glob(os.path.join(SPARQL_DIR, "*.sparql")))
    if not sparql_files:
        print("Нет .sparql файлов в директории sparql/")
        return

    print(f"Найдено {len(sparql_files)} запросов\n")

    for filepath in sparql_files:
        filename = os.path.basename(filepath)
        query_name = os.path.splitext(filename)[0]
        output_file = os.path.join(DATA_DIR, f"{query_name}.json")

        print(f"[RUN] {filename} ...", end=" ")

        with open(filepath, "r", encoding="utf-8") as f:
            query = f.read()

        # Удаляем комментарии из запроса
        lines = [line for line in query.split("\n") if not line.strip().startswith("#")]
        clean_query = "\n".join(lines).strip()

        result = run_query(clean_query)

        if result:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            bindings = result.get("results", {}).get("bindings", [])
            print(f"OK — {len(bindings)} записей → {query_name}.json")
        else:
            print("FAILED")


if __name__ == "__main__":
    run_all()
