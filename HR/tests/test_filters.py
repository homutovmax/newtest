"""Regression tests: EXCLUDE_WORDS, SBER filters, location logic."""
import sys, os, ast

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _get_list(var_name, filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == var_name:
                    if isinstance(node.value, ast.List):
                        return [ast.literal_eval(e) for e in node.value.elts]
    return []


def test_exclude_words_well_formed():
    words = _get_list('EXCLUDE_WORDS',
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'update_vacancies.py'))
    assert len(words) > 50, f"Only {len(words)} EXCLUDE_WORDS — too few"
    for w in words:
        assert w == w.lower(), f"Not lowercase: {repr(w)}"
        assert '  ' not in w, f"Double space in: {repr(w)}"


def test_sber_mgmt_well_formed():
    words = _get_list('SBER_MGMT',
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'update_vacancies.py'))
    assert len(words) > 15, f"Only {len(words)} SBER_MGMT — too few"
    for w in words:
        assert '  ' not in w, f"Double space in: {repr(w)}"


def test_sber_reject_well_formed():
    words = _get_list('SBER_REJECT',
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'update_vacancies.py'))
    assert len(words) > 30, f"Only {len(words)} SBER_REJECT — too few"
    for w in words:
        assert '  ' not in w, f"Double space in: {repr(w)}"


def test_moscow_spb():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
    from scrapers.shared import is_moscow_spb
    assert is_moscow_spb("Москва")
    assert is_moscow_spb("Санкт-Петербург")
    assert is_moscow_spb("Московская область")
    assert is_moscow_spb("Удалённо")
    assert is_moscow_spb("Remote")
    assert is_moscow_spb("Can be done remotely")
    assert not is_moscow_spb("Казань")
    assert not is_moscow_spb("Новосибирск")
    assert not is_moscow_spb("Екатеринбург")
    assert is_moscow_spb("")
    assert is_moscow_spb(None)
