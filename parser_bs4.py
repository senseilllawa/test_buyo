from load_django import *
from parser_app.models import Product
from pprint import pprint
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Accept-Language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Referer': 'https://www.google.com/',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'DNT': '1',
}

url = 'https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_Black_Titanium-p1145443.html'


def clean_text(value):
    if not value:
        return None
    text = ' '.join(value.replace('\xa0', ' ').split())
    return text or None


def get_spec_value(chars_block, label):
    if not chars_block:
        return None
    try:
        for span in chars_block.find_all('span'):
            if span.get_text(strip=True) == label:
                sibling = span.find_next_sibling('span')
                if sibling:
                    return clean_text(sibling.get_text(' ', strip=True))
    except AttributeError:
        return None
    return None


response = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

product = {}
product['parser_name'] = 'requests_bs4'
product['url'] = url

try:
    product['title'] = clean_text(soup.find('h1', class_='main-title').text)
except AttributeError:
    product['title'] = None

chars_block = soup.find('div', class_='br-pr-chr')

try:
    product['color'] = get_spec_value(chars_block, 'Колір')
except AttributeError:
    product['color'] = None

try:
    product['memory'] = get_spec_value(chars_block, "Вбудована пам'ять")
except AttributeError:
    product['memory'] = None

try:
    product['manufacturer'] = get_spec_value(chars_block, 'Виробник')
except AttributeError:
    product['manufacturer'] = None

price_block = soup.find('div', class_='main-price-block')

try:
    old_price = clean_text(price_block.find('div', class_='br-pr-op').find('span').text)
except AttributeError:
    old_price = None

try:
    current_price = clean_text(price_block.find('div', class_='br-pr-np').find('span').text)
except AttributeError:
    current_price = None

if old_price:
    product['regular_price'] = old_price
    product['sale_price'] = current_price
else:
    product['regular_price'] = current_price
    product['sale_price'] = None

try:
    slider = soup.find('div', class_='br-prs-s')
    photos = []
    for img in slider.find_all('img', class_='br-main-img'):
        src = img.get('src')
        if src:
            photos.append(src)
    product['photos'] = photos
except AttributeError:
    product['photos'] = None

try:
    product['product_code'] = clean_text(soup.find('span', class_='br-pr-code-val').text)
except AttributeError:
    product['product_code'] = None

try:
    product['reviews_count'] = int(soup.find('a', class_='reviews-count').find('span').text.strip())
except (AttributeError, ValueError):
    product['reviews_count'] = None

try:
    product['screen_diagonal'] = get_spec_value(chars_block, 'Діагональ екрану')
except AttributeError:
    product['screen_diagonal'] = None

try:
    product['display_resolution'] = get_spec_value(chars_block, 'Роздільна здатність екрану')
except AttributeError:
    product['display_resolution'] = None

try:
    characteristics = {}
    for item in chars_block.find_all('div', class_='br-pr-chr-item'):
        inner = item.find('div')
        for row in inner.find_all('div', recursive=False):
            spans = row.find_all('span', recursive=False)
            if len(spans) < 2:
                continue
            key = clean_text(spans[0].get_text(strip=True))
            value = clean_text(spans[1].get_text(' ', strip=True))
            if key:
                characteristics[key] = value
    product['characteristics'] = characteristics
except AttributeError:
    product['characteristics'] = None

pprint(product)

Product.objects.get_or_create(**product)
