# Скилл: Аналитика — поиск и устранение неточностей

## 1. Быстрый старт

```
cd C:\NEWTEST\HR
python -c "from generate_cover import classify_title"  # проверка импорта
python -c "import update_vacancies"                     # проверка зависимостей
```

## 2. Регулярный аудит отчёта

### 2.1. Найти нецелевые вакансии в report

```powershell
Select-String -Path vacancies_report.html -Pattern "персональн|премьер|личн|ассистент|помощник"
```

### 2.2. Проверить exclude уже работает

```powershell
C:\Python314\python.exe -c "
EXCLUDE = ['консультант','оператор','водитель','продавец','фармацевт','стоматолог',
           'маркетолог','юрист','бухгалтер','недвижимость','пищев','производств',
           'шоколад','персональн','премьер']
title = 'Персональный менеджер Сбер Премьер'
if any(w in title.lower() for w in EXCLUDE):
    print('OK — отсечена')
else:
    print('НУЖНО ДОБАВИТЬ В EXCLUDE')
"
```

### 2.3. Проверить dummy-зарплаты

```powershell
Select-String -Path vacancies_report.html -Pattern "100 [₽р]|100\b"
```

### 2.4. Проверить double-prefix в истории

```powershell
python -c "import json; d=json.load(open('vacancies_history.json')); print([k for k in d if 'habr-habr' in k])"
```

### 2.5. Проверить зарплаты < 200К

```powershell
python -c "
import re
with open('vacancies_report.html','r',encoding='utf-8') as f:
    for m in re.finditer(r'(\d[\d\s]*)\s*[–-]\s*(\d[\d\s]*)\s*[₽р]|от\s*(\d[\d\s]*)\s*[₽р]|до\s*(\d[\d\s]*)\s*[₽р]', f.read()):
        print(m.group())
"
```

## 3. Оптимизация фильтров

### 3.1. Когда добавлять слово в EXCLUDE_WORDS

- Вакансия не IT (консультант, оператор, продавец, HR, маркетинг, юрист, бухгалтер)
- Вакансия премиального обслуживания (персональный менеджер, премьер)
- Слово уникально для не-ИТ сфер (не отсечёт нужные роли)
- **НЕ добавлять:** общие слова (менеджер, специалист, эксперт, инженер)

### 3.2. Когда НЕ добавлять в EXCLUDE_WORDS

- Слово может быть частью IT-роли (Data Scientist, ML Engineer)
- Слово слишком общее (менеджер выкинет Product Manager)

### 3.3. Тюнинг зарплатного фильтра

```python
HH_SALARY_MIN = 200_000  # в salary_filter()
```

### 3.4. Тюнинг поисковых запросов

Проверить, какие кейворды в HH_QUERIES притягивают нецелевые вакансии. Удалить слишком широкие OR-связки, добавить AND-уточнения.

## 4. Проверка классификации

### 4.1. classify_title() — точность

```powershell
python -c "
from generate_cover import classify_title
tests = [
    ('Системный аналитик', 'ba'),
    ('Head of AI', 'ai_product'),
    ('Директор по цифровой трансформации', 'strategy'),
    ('CTO телеком', 'telecom'),
    ('Продавец', 'unknown'),
]
for title, expected in tests:
    result = classify_title(title)
    status = 'OK' if result == expected else f'НЕВЕРНО (got {result})'
    print(f'{status}: {title} -> {result}')
"
```

### 4.2. Сверка resume.php

Открыть `http://maximum64.beget.tech/resume.php?title=Системный+аналитик&company=Сбер`

- Должен показать сценарий BA (Руководитель бизнес-анализа)
- Никаких «Сценарий N», «Целевые роли», маркеров автосборки

## 5. Валидация cover-писем

Открыть любые 3 cover_v*.html:

- Заголовок письма совпадает с вакансией
- **полужирный текст** отображается как `<strong>` (не `**` literal)
- Нет экранированных сущностей (`&amp;`, `&lt;`) вместо символов

## 6. Восстановление после сбоя

Если отчёт сгенерирован с ошибками:

1. Удалить `vacancies_history.json` (будет пересоздан)
2. Удалить `vacancies_report.html`
3. Удалить `cover_v*.html`
4. Запустить `python update_vacancies.py`

## 7. Критерии качества

| Метрика | Норма | Как проверить |
|---------|-------|---------------|
| Доля нецелевых вакансий | < 2% | Select-String exclude-слов в report |
| Доля dummy-зарплат | 0% | grep "100 ₽" в report |
| Double-prefix в истории | 0 | json check |
| Cover letters с title/company | 100% | spot check 3 шт |
| Классификация | 100% | pytest по тестовым названиям |

## 8. Типовые сценарии

### 8.1. В отчёте появилась нецелевая вакансия

1. Открыть ссылку, скопировать точное название
2. Определить уникальные слова-маркеры (не пересекаются с IT-ролями)
3. Добавить в `EXCLUDE_WORDS` в `update_vacancies.py`
4. Перезапустить `python update_vacancies.py`
5. Проверить, что вакансия исчезла из report

### 8.2. В отчёте вакансия с зарплатой 100 ₽

1. Проверить, что `salary_filter()` в `update_vacancies.py` корректно чистит
2. Если баг — исправить regex или логику
3. Перезапустить

### 8.3. Классификация неверная

1. Проверить `classify_title()` в `generate_cover.py`
2. Добавить/скорректировать ключевые слова для нужного сценария
3. Проверить все тесты `pytest test_classify.py`
4. Проверить `resume.php` на Beget
