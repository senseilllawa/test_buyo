# Parsers for brain.com.ua

Three product parsers for [brain.com.ua](https://brain.com.ua/): Requests + BeautifulSoup, Selenium and Playwright. Parsed data is stored in PostgreSQL through Django ORM.

## What is collected

- full product title
- color
- memory
- manufacturer
- regular price
- sale price (or `None`)
- photo URLs (list)
- product code
- reviews count
- screen diagonal
- display resolution
- all characteristics from the product tab (dict)

## Stack

- Python 3.9+
- Django 4.2 + PostgreSQL
- Requests / BeautifulSoup
- Selenium
- Playwright

Selectors for BS4 are picked by class names. Selenium and Playwright use XPath only.

## Project structure

```text
.
├── parser_bs4.py          # direct product URL
├── parser_selenium.py     # search on the homepage
├── parser_playwright.py   # same flow as Selenium
├── load_django.py         # Django bootstrap for scripts
├── manage.py
├── parser_app/            # Product model
└── brain_parser/          # Django settings
```

## Setup

1. Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

2. Create a PostgreSQL database `brain_parser`. Default connection in `brain_parser/settings.py`:

```text
HOST: 127.0.0.1
PORT: 5432
NAME: brain_parser
USER: postgres
PASSWORD: postgres
```

3. Apply migrations:

```bash
python manage.py migrate
```

## Run parsers

Requests / BeautifulSoup — product page:

```bash
python parser_bs4.py
```

URL: `https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_Black_Titanium-p1145443.html`

Selenium and Playwright — homepage search `Apple iPhone 15 128GB Black`, click Find, open the first result:

```bash
python parser_selenium.py
python parser_playwright.py
```

Each script prints a dict via `pprint` and saves the row with `get_or_create`.

## Where results are stored

PostgreSQL table: `parser_app_product`

CSV export is done in pgAdmin: right-click the table → **Import/Export Data** → Export → CSV. No extra script is needed.
