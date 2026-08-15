"""Regression tests: _cover_html output formatting, no raw HTML in text."""
import sys, os, re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))


def test_cover_html_structure():
    """_cover_html must produce valid HTML, not escaped-as-text HTML."""
    from generate_covers import _cover_html
    html = _cover_html("CTO", "МТС", "Москва", "300 000 ₽",
                       "Уважаемые коллеги!\n\n**bold text**\n\nnormal text", "telecom")
    assert '<!DOCTYPE html>' in html
    assert '<strong>bold text</strong>' in html, f"**bold** should be <strong>: {html}"
    assert 'Уважаемые коллеги!' in html
    assert '.letter-text' in html
    assert 'copyLetter' in html
    lt_match = re.search(r'<div class="letter-text">(.*?)</div>', html, re.DOTALL)
    assert lt_match, "Missing .letter-text div"
    lt = lt_match.group(1)
    assert '<br>normal text' in lt, f"newline should be <br> in letter-text: {lt}"


def test_cover_html_escapes_title():
    """Title should be HTML-escaped but not double-escaped."""
    from generate_covers import _cover_html
    html = _cover_html("C++ Developer & Tester", "M&T Co", "Moscow", "",
                       "Text", "telecom")
    assert 'C++' in html
    assert '&amp;' in html


def test_cover_html_no_double_escape():
    """HTML-escaped content should not be double-escaped in output."""
    from generate_covers import _cover_html
    html = _cover_html("C++ & Go", "M&T Co", "Moscow", "", "Text", "telecom")
    assert '&amp;amp;' not in html, "Double-ampersand escape detected"
    assert '&lt;' not in html, "Unexpected &lt; in output"


def test_cover_html_empty_location_ok():
    """Empty location should not cause errors."""
    from generate_covers import _cover_html
    html = _cover_html("Title", "Co", "", "", "Text", "telecom")
    assert '<!DOCTYPE html>' in html
    assert 'Text' in html


def test_cover_html_category_badge():
    """Category should be shown in a badge."""
    from generate_covers import _cover_html
    for cat in ("telecom", "ai_product", "strategy", "ba"):
        html = _cover_html("Title", "Co", "Moscow", "", "Text", cat)
        assert cat in html, f"Category {cat} should appear in HTML"
