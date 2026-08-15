"""Regression tests: classify_title + generate_letter."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from generate_cover import classify_title, generate_letter


def test_telecom():
    assert classify_title("Руководитель направления телеком") == "telecom"
    assert classify_title("CTO") == "telecom"
    assert classify_title("DevOps инженер") == "telecom"
    assert classify_title("Руководитель платформы клиентского сервиса") == "telecom"
    assert classify_title("Network Engineer") == "telecom"
    assert classify_title("Технический директор") == "telecom"
    assert classify_title("Инфраструктурный инженер") == "telecom"
    assert classify_title("Solution Architect") == "telecom"
    assert classify_title("Head of CX") == "telecom"
    assert classify_title("Руководитель направления клиентский сервис") == "telecom"
    assert classify_title("Руководитель ИТ-продукта") == "telecom"


def test_ai_product():
    assert classify_title("Head of AI") == "ai_product"
    assert classify_title("CPO") == "ai_product"
    assert classify_title("Директор по продукту AI") == "ai_product"
    assert classify_title("Data Science") == "ai_product"
    assert classify_title("Machine Learning Engineer") == "ai_product"
    assert classify_title("Искусственный интеллект") == "ai_product"
    assert classify_title("Руководитель направления AI") == "ai_product"
    assert classify_title("AI архитектор") == "ai_product"
    assert classify_title("R&D Lead") == "ai_product"
    assert classify_title("Директор по продукту") == "ai_product"
    assert classify_title("NLP инженер") == "ai_product"


def test_strategy():
    assert classify_title("Директор по цифровой трансформации") == "strategy"
    assert classify_title("Head of Digital Transformation") == "strategy"
    assert classify_title("Директор по инновациям и цифровой трансформации") == "strategy"
    assert classify_title("Change Manager") == "strategy"
    assert classify_title("Head of Strategy") == "strategy"
    assert classify_title("Директор по трансформации") == "strategy"
    assert classify_title("Стратегический директор") == "strategy"
    assert classify_title("Operational Excellence Manager") == "strategy"


def test_ba():
    assert classify_title("Бизнес-аналитик") == "ba"
    assert classify_title("Системный аналитик") == "ba"
    assert classify_title("Lead Business Analyst") == "ba"
    assert classify_title("Руководитель бизнес-анализа") == "ba"
    assert classify_title("BPMN аналитик") == "ba"
    assert classify_title("Бизнес-аналитик BPMN") == "ba"
    assert classify_title("Управление требованиями") == "ba"
    assert classify_title("Бизнес-аналитик ERP") == "ba"
    assert classify_title("Руководитель отдела аналитики") == "ba"


def test_unknown():
    assert classify_title("Продавец") == "unknown"
    assert classify_title("Водитель") == "unknown"
    assert classify_title("Учитель математики") == "unknown"
    assert classify_title("Медицинская сестра") == "unknown"
    assert classify_title("Повар") == "unknown"


def test_food_exclusion():
    result = classify_title("R&D технолог мясного направления")
    assert result not in ("telecom", "ai_product"), f"Expected non-telecom/ai, got {result}"


def test_generate_letter():
    letter, cat = generate_letter("CTO", "МТС")
    assert "Максим Хомутов" in letter
    assert "CTO" in letter
    assert "МТС" in letter
    assert cat in ("telecom", "ai_product", "strategy", "ba", "unknown")


def test_generate_letter_unknown():
    letter, cat = generate_letter("Продавец", "Магазин")
    assert "Максим Хомутов" in letter
    assert cat == "unknown"


def test_generate_letter_all_scenarios():
    sources = [
        ("CTO", "МТС", 1, "telecom"),
        ("Head of AI", "Яндекс", 2, "ai_product"),
        ("Директор по трансформации", "Сбер", 3, "strategy"),
        ("Бизнес-аналитик", "СИБУР", 4, "ba"),
    ]
    for title, company, scenario, expected_cat in sources:
        letter, cat = generate_letter(title, company, scenario)
        assert cat == expected_cat, f"Expected {expected_cat}, got {cat} for {title}"
        assert "Максим Хомутов" in letter


def test_generate_letter_deterministic():
    letter1, cat1 = generate_letter("Руководитель направления AI", "Яндекс")
    letter2, cat2 = generate_letter("Руководитель направления AI", "Яндекс")
    assert letter1 == letter2, "Same inputs should produce same letter"
    assert cat1 == cat2
