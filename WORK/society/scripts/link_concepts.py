#!/usr/bin/env python3
"""
Скрипт для автоматической расстановки перекрёстных ссылок.
Работает с подпапками (относительные пути между разделами).

Использование: python link_concepts.py <articles_root> <concepts_json>
Пример: python link_concepts.py ../../WEB/society ../concepts.json
"""

import json
import re
import os
import sys


def load_concepts(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    concepts = []
    for section in data.get("sections", []):
        for concept in section.get("concepts", []):
            concepts.append({"title": concept["title"], "file": concept["file"]})
    return concepts


def get_relative_path(from_file, to_file):
    """Вычисляет относительный путь от одной статьи к другой."""
    from_dir = os.path.dirname(from_file)
    return os.path.relpath(to_file, from_dir)


SEMANTIC_MAP = {
    "01_prava_i_obyazannosti/concepts/chto_ya_mogu_s_14_let.md": [
        "паспорт", "паспорта", "паспортом", "получить паспорт",
        "14 лет", "14-лет", "с четырнадцати",
    ],
    "01_prava_i_obyazannosti/concepts/prava_v_shkole_i_doma.md": [
        "права в школе", "права школьника",
        "бесплатное образование", "уважение",
    ],
    "01_prava_i_obyazannosti/concepts/komendantskiy_chas_i_police.md": [
        "комендантский час", "комендантского часа",
        "полицейский", "полицию", "полиция",
        "22:00", "поздно вечером",
    ],
    "01_prava_i_obyazannosti/concepts/obyazannosti_pered_roditelyami.md": [
        "обязанности перед родителями", "ответственность перед законом",
        "уголовная ответственность", "административная ответственность",
        "нарушил закон",
    ],
    "01_prava_i_obyazannosti/concepts/kuda_zhalovatsya.md": [
        "куда жаловаться", "жаловаться",
        "нарушают", "нарушение прав", "уполномоченный",
    ],
    "02_obshestvo_i_pravila/concepts/zachem_zakony.md": [
        "законы", "закон", "закона", "законом",
        "правила", "правил", "правило",
    ],
    "02_obshestvo_i_pravila/concepts/pochemu_nelzya_musorit.md": [
        "мусорить", "мусор", "урна", "чистота",
    ],
    "02_obshestvo_i_pravila/concepts/ya_i_gosudarstvo.md": [
        "государство", "государства", "политика", "политику",
    ],
    "02_obshestvo_i_pravila/concepts/volonterstvo.md": [
        "волонтёрство", "волонтёр", "волонтёры",
        "благотворительность", "помогать бесплатно",
        "молодёжных центрах", "экологические отряды",
        "помогать", "помощь другим",
    ],
    "02_obshestvo_i_pravila/concepts/pravila_rayona.md": [
        "правила района", "соседи", "соседей",
        "подъезде", "подъезд", "дворе", "двор",
    ],
    "03_pervye_dengi/concepts/gde_rabotat_v_14.md": [
        "где работать", "подработка", "подработки",
        "курьер", "почтальон", "зарабатывать",
    ],
    "03_pervye_dengi/concepts/pomoshch_sosedyam.md": [
        "помощь соседям", "выгул собак", "няня", "репетиторство",
    ],
    "03_pervye_dengi/concepts/kak_ne_popast_na_razvod.md": [
        "попасть на развод", "мошенничество при трудоустройстве",
        "предоплату", "заплатить за работу",
    ],
    "03_pervye_dengi/concepts/balans_raboty_i_uchyoby.md": [
        "баланс работы", "совмещать работу", "успевать",
    ],
    "03_pervye_dengi/concepts/dengi_i_roditeli.md": [
        "деньги и родители", "отдавать родителям", "первые деньги",
    ],
    "04_karmannye_dengi/concepts/skolko_dayut_vs_khochetsya.md": [
        "сколько дают", "карманные деньги", "карманных денег",
    ],
    "04_karmannye_dengi/concepts/kopit_ili_tratit.md": [
        "копить", "копилку", "откладывать", "тратить сразу",
        "управление деньгами", "копилка", "тратить",
    ],
    "04_karmannye_dengi/concepts/na_chto_ne_zhalko_deneg.md": [
        "тратить с удовольствием", "хобби", "подарки друзьям",
        "впечатления", "траты", "покупка", "покупки",
        "мороженое", "концерт", "подарок на день рождения",
        "тратить деньги", "управление деньгами",
    ],
    "04_karmannye_dengi/concepts/dolgi_druzya.md": [
        "долги среди друзей", "одалживать", "давать в долг",
    ],
    "04_karmannye_dengi/concepts/kak_dogovoritsya_o_povyshenii.md": [
        "договориться о повышении", "повышение",
        "попросить больше денег",
    ],
    "05_socseti/concepts/pochemu_laiki_vliyayut.md": [
        "лайки влияют", "лайков много", "лайков мало",
        "дофамин", "ставить лайки", "набрало много лайков",
        "лайки", "лайков", "чужое мнение",
    ],
    "05_socseti/concepts/algoritmy_socsetey.md": [
        "алгоритмы соцсетей", "алгоритм", "рекомендации",
        "информационный пузырь",
    ],
    "05_socseti/concepts/blogerstvo.md": [
        "блогерство", "блогер", "блогеры", "подписчики",
    ],
    "05_socseti/concepts/zavist_k_chuzhoy_zhizni.md": [
        "зависть", "завидовать", "сравнивать себя",
    ],
    "05_socseti/concepts/kak_ne_prosidet_v_telefone.md": [
        "просидеть в телефоне", "зависимость от телефона",
        "зависимость от соцсетей", "таймер использования",
    ],
    "06_moshenniki/concepts/vy_vyigrali_ayfon.md": [
        "выиграли айфон", "выиграл приз", "розыгрыш",
    ],
    "06_moshenniki/concepts/phishing.md": [
        "фишинг", "фишинга", "подозрительная ссылка",
        "код из смс", "данные карты", "подозрительным ссылкам",
        "украсть данные", "перевести деньги", "мошенники",
    ],
    "06_moshenniki/concepts/legkiy_zarabotok.md": [
        "лёгкий заработок", "заработок без усилий",
        "заработать быстро", "пирамида", "предоплату",
        "заработать", "заработка", "развод",
    ],
    "06_moshenniki/concepts/moshenniki_v_igrakh.md": [
        "мошенники в играх", "обмен аккаунтами", "скины",
        "аккаунтами", "аккаунтов", "игровая валюта",
    ],
    "06_moshenniki/concepts/kuda_bezhat_esli_obmanuli.md": [
        "куда бежать", "обманули", "мошенничество",
        "заявление в полицию",
    ],
}


def make_patterns(search_terms):
    patterns = []
    for term in search_terms:
        if ' ' in term:
            patterns.append(re.escape(term))
        elif len(term) >= 4:
            patterns.append(r'\b' + re.escape(term) + r'\w*\b')
    return patterns


def replace_with_links(text, concepts, current_file):
    """Добавляет ссылки на другие статьи с правильными относительными путями."""
    lines = text.split('\n')
    header_lines = []
    body_lines = []
    in_body = False
    for line in lines:
        if not in_body and (line.startswith('#') or line.strip() == ''):
            header_lines.append(line)
        else:
            in_body = True
            body_lines.append(line)

    header = '\n'.join(header_lines)
    body = '\n'.join(body_lines)

    MAX_LINKS = 5
    replacements = 0

    for concept in concepts:
        if replacements >= MAX_LINKS:
            break

        target_file = concept["file"]
        if target_file == current_file:
            continue

        # Вычисляем относительный путь
        rel_path = get_relative_path(current_file, target_file)

        if f']({rel_path})' in body:
            continue

        search_terms = SEMANTIC_MAP.get(target_file, [])
        if not search_terms:
            continue

        patterns = make_patterns(search_terms)
        linked = False

        for pattern in patterns:
            if linked:
                break

            def repl(match, rp=rel_path):
                return f"[{match.group(0)}]({rp})"

            try:
                new_body, count = re.subn(pattern, repl, body, count=1, flags=re.IGNORECASE)
                if count > 0:
                    body = new_body
                    replacements += 1
                    linked = True
            except re.error:
                continue

    return header + '\n' + body, replacements


def process_directory(articles_root, concepts_json):
    concepts = load_concepts(concepts_json)
    print(f"Понятий: {len(concepts)}")
    print(f"Семантических записей: {len(SEMANTIC_MAP)}\n")

    processed = 0
    total_links = 0

    for concept in concepts:
        filepath = os.path.join(articles_root, concept["file"])
        if not os.path.exists(filepath):
            print(f"  [!!] {concept['file']} — файл не найден")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        new_text, count = replace_with_links(text, concepts, concept["file"])

        if new_text != text:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_text)
            print(f"  [OK] {concept['file']} — {count} ссылок")
        else:
            print(f"  [--] {concept['file']} — нет совпадений")

        processed += 1
        total_links += count

    print(f"\nОбработано: {processed} файлов")
    print(f"Добавлено: {total_links} ссылок")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: link_concepts.py <articles_root> <concepts_json>")
        sys.exit(1)
    process_directory(sys.argv[1], sys.argv[2])
