import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from generate_cover import generate_letter

def test_telecom_letter():
    text, cat = generate_letter("Руководитель направления", "МТС", 0, "", "Москва")
    assert cat == "telecom"
    assert "МТС" in text
    assert "Руководитель направления" in text

def test_ai_product_letter():
    text, cat = generate_letter("Head of AI", "Сбер", 0, "400000", "Москва")
    assert cat == "ai_product"
    assert "Сбер" in text
    assert "Head of AI" in text

def test_strategy_letter():
    text, cat = generate_letter("Директор по трансформации", "СИБУР", 0, "", "Москва")
    assert cat == "strategy"
    assert "СИБУР" in text

def test_ba_letter():
    text, cat = generate_letter("Системный аналитик", "Т-Банк", 0, "300000", "Санкт-Петербург")
    assert cat == "ba"
    assert "Т-Банк" in text

def test_unknown_fallback():
    text, cat = generate_letter("Продавец", "Магазин", 0, "", "")
    assert cat == "unknown"

def test_scenario_override():
    text1, cat1 = generate_letter("Любой", "Компания", 1, "", "")
    text2, cat2 = generate_letter("Любой", "Компания", 2, "", "")
    assert cat1 != cat2
