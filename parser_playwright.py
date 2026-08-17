from load_django import *
from parser_app.models import Product
from pprint import pprint
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

SEARCH_QUERY = 'Apple iPhone 15 128GB Black'
HOME_URL = 'https://brain.com.ua/'

SEARCH_INPUT_XPATH = "//input[@class='quick-search-input']"
SEARCH_BUTTON_XPATH = "//input[@class='qsr-submit']"
FIRST_PRODUCT_XPATH = "//div[contains(@class,'product-wrapper')]//div[contains(@class,'br-pp-desc')]//a"
TITLE_XPATH = "//h1[@class='main-title']"
PRODUCT_CODE_XPATH = "//span[@class='br-pr-code-val']"
REVIEWS_XPATH = "//a[contains(@class,'reviews-count')]/span"
PHOTOS_XPATH = "//div[contains(@class,'br-prs-s')]//img[@class='br-main-img']"
OLD_PRICE_XPATH = "//div[contains(@class,'main-price-block')]/div[@class='br-pr-op']/div[@class='price-wrapper']/span"
NEW_PRICE_XPATH = "//div[contains(@class,'main-price-block')]/div[@class='br-pr-np']/div[@class='price-wrapper']/span"
CHARS_ROWS_XPATH = "//div[@class='br-pr-chr']/div[@class='br-pr-chr-item']/div/div"


def clean_text(value):
    if not value:
        return None
    text = ' '.join(value.replace('\xa0', ' ').split())
    return text or None


def get_text_by_xpath(page, xpath):
    locator = page.locator(f'xpath={xpath}')
    try:
        if locator.count() == 0:
            return None
        return clean_text(locator.first.text_content())
    except PlaywrightTimeoutError:
        return None


def get_spec_value(page, label):
    xpath = f"//div[@class='br-pr-chr']//span[normalize-space()=\"{label}\"]/following-sibling::span"
    return get_text_by_xpath(page, xpath)


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        locale='uk-UA',
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    )
    page = context.new_page()
    page.set_default_timeout(30000)

    try:
        page.goto(HOME_URL, wait_until='domcontentloaded')
        page.wait_for_timeout(2000)

        search_inputs = page.locator(f'xpath={SEARCH_INPUT_XPATH}')
        search_input = None
        for item in search_inputs.all():
            if item.is_visible():
                search_input = item
                break
        if search_input is None:
            search_input = page.locator(f'xpath={SEARCH_INPUT_XPATH}')
        search_input.click()
        search_input.fill(SEARCH_QUERY)
        page.wait_for_timeout(1000)

        page.locator(f'xpath={SEARCH_BUTTON_XPATH}').click()
        page.wait_for_selector(f'xpath={FIRST_PRODUCT_XPATH}')
        page.wait_for_timeout(1000)

        page.locator(f'xpath={FIRST_PRODUCT_XPATH}').first.click()
        page.wait_for_selector(f'xpath={PRODUCT_CODE_XPATH}')
        page.wait_for_timeout(2000)

        product = {}
        product['parser_name'] = 'playwright'
        product['url'] = page.url

        try:
            product['title'] = get_text_by_xpath(page, TITLE_XPATH)
        except PlaywrightTimeoutError:
            product['title'] = None

        try:
            product['color'] = get_spec_value(page, 'Колір')
        except PlaywrightTimeoutError:
            product['color'] = None

        try:
            product['memory'] = get_spec_value(page, "Вбудована пам'ять")
        except PlaywrightTimeoutError:
            product['memory'] = None

        try:
            product['manufacturer'] = get_spec_value(page, 'Виробник')
        except PlaywrightTimeoutError:
            product['manufacturer'] = None

        try:
            old_price = get_text_by_xpath(page, OLD_PRICE_XPATH)
        except PlaywrightTimeoutError:
            old_price = None

        try:
            current_price = get_text_by_xpath(page, NEW_PRICE_XPATH)
        except PlaywrightTimeoutError:
            current_price = None

        if old_price:
            product['regular_price'] = old_price
            product['sale_price'] = current_price
        else:
            product['regular_price'] = current_price
            product['sale_price'] = None

        try:
            photos = []
            images = page.locator(f'xpath={PHOTOS_XPATH}')
            for img in images.all():
                src = img.get_attribute('src')
                if src:
                    photos.append(src)
            product['photos'] = photos
        except PlaywrightTimeoutError:
            product['photos'] = None

        try:
            product['product_code'] = get_text_by_xpath(page, PRODUCT_CODE_XPATH)
        except PlaywrightTimeoutError:
            product['product_code'] = None

        try:
            reviews_text = get_text_by_xpath(page, REVIEWS_XPATH)
            product['reviews_count'] = int(reviews_text) if reviews_text else None
        except (PlaywrightTimeoutError, ValueError, TypeError):
            product['reviews_count'] = None

        try:
            product['screen_diagonal'] = get_spec_value(page, 'Діагональ екрану')
        except PlaywrightTimeoutError:
            product['screen_diagonal'] = None

        try:
            product['display_resolution'] = get_spec_value(page, 'Роздільна здатність екрану')
        except PlaywrightTimeoutError:
            product['display_resolution'] = None

        try:
            characteristics = {}
            rows = page.locator(f'xpath={CHARS_ROWS_XPATH}')
            for row in rows.all():
                key_el = row.locator("xpath=./span")
                value_el = row.locator("xpath=./span/following-sibling::span")
                if key_el.count() == 0 or value_el.count() == 0:
                    continue
                key = clean_text(key_el.first.text_content())
                value = clean_text(value_el.first.text_content())
                if key:
                    characteristics[key] = value
            product['characteristics'] = characteristics
        except PlaywrightTimeoutError:
            product['characteristics'] = None

        pprint(product)
        Product.objects.get_or_create(**product)

    finally:
        browser.close()
