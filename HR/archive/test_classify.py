import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from generate_cover import classify_title

def test_telecom():
    assert classify_title("Руководитель направления клиентского сервиса") == "telecom"
    assert classify_title("CTO") == "telecom"
    assert classify_title("DevOps инженер") == "telecom"
    assert classify_title("Начальник отдела инфраструктуры") == "telecom"
    assert classify_title("Руководитель платформы") == "telecom"
    assert classify_title("Delivery Manager") == "telecom"

def test_ai_product():
    assert classify_title("Head of AI") == "ai_product"
    assert classify_title("Data Scientist") == "ai_product"
    assert classify_title("ML Engineer") == "ai_product"
    assert classify_title("Директор по продукту AI") == "ai_product"
    assert classify_title("CPO") == "ai_product"
    assert classify_title("Data Engineer") == "ai_product"

def test_strategy():
    assert classify_title("Директор по цифровой трансформации") == "strategy"
    assert classify_title("Head of Innovation") == "strategy"
    assert classify_title("Strategy Manager") == "strategy"
    assert classify_title("Change Manager") == "strategy"

def test_ba():
    assert classify_title("Системный аналитик") == "ba"
    assert classify_title("Бизнес-аналитик") == "ba"
    assert classify_title("Lead Business Analyst") == "ba"
    assert classify_title("BPMN аналитик") == "ba"
    assert classify_title("Специалист по управлению требованиями") == "ba"

def test_unknown():
    assert classify_title("Продавец") == "unknown"
    assert classify_title("Водитель") == "unknown"
    assert classify_title("Персональный менеджер") == "unknown"

def test_case_insensitive():
    assert classify_title("head of ai") == "ai_product"
    assert classify_title("SYSTEM ANALYST") == "ba"

def test_empty():
    assert classify_title("") == "unknown"

def test_ba_vs_strategy():
    # BA должен победить при равных скор
    assert classify_title("Бизнес-аналитик цифровая трансформация") == "ba"
