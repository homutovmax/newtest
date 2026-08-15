"""Regression tests: dummy salary stripping, esc(), parse_salary_min."""
import sys, os, re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))


def _strip_dummy(salary):
    """Same logic used in both update_vacancies.py and shared.py to strip dummy 100₽."""
    if not salary:
        return ''
    c = re.sub(r'[\s\u00a0\u20bd\u0440\u0443\u0431\.]', '', salary)
    if c in ('', '100', '0', '\u2013'):
        return ''
    return salary


def test_dummy_100_ruble():
    assert _strip_dummy('100 ₽') == ''
    assert _strip_dummy('100 руб.') == ''
    assert _strip_dummy('100руб') == ''
    assert _strip_dummy('100') == ''


def test_dummy_0():
    assert _strip_dummy('0') == ''
    assert _strip_dummy('0 ₽') == ''


def test_dummy_dash():
    assert _strip_dummy('\u2013') == ''
    assert _strip_dummy('–') == ''


def test_real_salary_preserved():
    assert _strip_dummy('200 000 ₽') == '200 000 ₽'
    assert _strip_dummy('150 000 – 250 000 ₽') == '150 000 – 250 000 ₽'
    assert _strip_dummy('от 300 000 ₽') == 'от 300 000 ₽'
    assert _strip_dummy('до 200 000 ₽') == 'до 200 000 ₽'


def test_none_empty():
    assert _strip_dummy('') == ''
    assert _strip_dummy(None) == ''


def test_esc():
    from src.scrapers.shared import esc
    assert esc('<script>') == '&lt;script&gt;'
    assert esc('"test"') == '&quot;test&quot;'
    assert esc("M&T") == "M&amp;T"
    assert esc(None) == ''
    assert esc('') == ''
    assert esc(0) == '0'
    assert esc(100) == '100'


def test_parse_salary_min():
    from src.scrapers.shared import parse_salary_min
    assert parse_salary_min('200 000 ₽') == 200000
    assert parse_salary_min('150 000 – 250 000 ₽') == 150000
    assert parse_salary_min('от 300 000 ₽') == 300000
    assert parse_salary_min('') == 0
    assert parse_salary_min(None) == 0
    assert parse_salary_min('0') == 0
