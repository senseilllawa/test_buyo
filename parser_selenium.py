from load_django import *
from parser_app.models import Product
from pprint import pprint
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

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


def get_text_by_xpath(driver, xpath):
    try:
        return clean_text(driver.find_element(By.XPATH, xpath).get_attribute('textContent'))
    except NoSuchElementException:
        return None


def get_spec_value(driver, label):
    xpath = f"//div[@class='br-pr-chr']//span[normalize-space()=\"{label}\"]/following-sibling::span"
    try:
        return clean_text(driver.find_element(By.XPATH, xpath).get_attribute('textContent'))
    except NoSuchElementException:
        return None


options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--start-maximized')
options.add_argument('--lang=uk-UA')
options.add_experimental_option('excludeSwitches', ['enable-automation'])

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 30)

try:
    driver.get(HOME_URL)
    time.sleep(2)

    search_inputs = driver.find_elements(By.XPATH, SEARCH_INPUT_XPATH)
    search_input = None
    for item in search_inputs:
        if item.is_displayed():
            search_input = item
            break
    if search_input is None:
        search_input = wait.until(EC.element_to_be_clickable((By.XPATH, SEARCH_INPUT_XPATH)))
    search_input.click()
    search_input.clear()
    search_input.send_keys(SEARCH_QUERY)
    time.sleep(1)

    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, SEARCH_BUTTON_XPATH)))
    search_button.click()

    first_product = wait.until(EC.element_to_be_clickable((By.XPATH, FIRST_PRODUCT_XPATH)))
    first_product.click()

    wait.until(EC.presence_of_element_located((By.XPATH, TITLE_XPATH)))
    time.sleep(2)

    product = {}
    product['parser_name'] = 'selenium'
    product['url'] = driver.current_url

    try:
        product['title'] = get_text_by_xpath(driver, TITLE_XPATH)
    except NoSuchElementException:
        product['title'] = None

    try:
        product['color'] = get_spec_value(driver, 'Колір')
    except NoSuchElementException:
        product['color'] = None

    try:
        product['memory'] = get_spec_value(driver, "Вбудована пам'ять")
    except NoSuchElementException:
        product['memory'] = None

    try:
        product['manufacturer'] = get_spec_value(driver, 'Виробник')
    except NoSuchElementException:
        product['manufacturer'] = None

    try:
        old_price = get_text_by_xpath(driver, OLD_PRICE_XPATH)
    except NoSuchElementException:
        old_price = None

    try:
        current_price = get_text_by_xpath(driver, NEW_PRICE_XPATH)
    except NoSuchElementException:
        current_price = None

    if old_price:
        product['regular_price'] = old_price
        product['sale_price'] = current_price
    else:
        product['regular_price'] = current_price
        product['sale_price'] = None

    try:
        photos = []
        images = driver.find_elements(By.XPATH, PHOTOS_XPATH)
        for img in images:
            src = img.get_attribute('src')
            if src:
                photos.append(src)
        product['photos'] = photos
    except NoSuchElementException:
        product['photos'] = None

    try:
        product['product_code'] = get_text_by_xpath(driver, PRODUCT_CODE_XPATH)
    except NoSuchElementException:
        product['product_code'] = None

    try:
        reviews_text = get_text_by_xpath(driver, REVIEWS_XPATH)
        product['reviews_count'] = int(reviews_text) if reviews_text else None
    except (NoSuchElementException, ValueError, TypeError):
        product['reviews_count'] = None

    try:
        product['screen_diagonal'] = get_spec_value(driver, 'Діагональ екрану')
    except NoSuchElementException:
        product['screen_diagonal'] = None

    try:
        product['display_resolution'] = get_spec_value(driver, 'Роздільна здатність екрану')
    except NoSuchElementException:
        product['display_resolution'] = None

    try:
        characteristics = {}
        rows = driver.find_elements(By.XPATH, CHARS_ROWS_XPATH)
        for row in rows:
            key_els = row.find_elements(By.XPATH, './span')
            value_els = row.find_elements(By.XPATH, './span/following-sibling::span')
            if not key_els or not value_els:
                continue
            key = clean_text(key_els[0].get_attribute('textContent'))
            value = clean_text(value_els[0].get_attribute('textContent'))
            if key:
                characteristics[key] = value
        product['characteristics'] = characteristics
    except NoSuchElementException:
        product['characteristics'] = None

    pprint(product)
    Product.objects.get_or_create(**product)

except TimeoutException:
    print('Timeout while waiting for page elements')
    raise
finally:
    driver.quit()
