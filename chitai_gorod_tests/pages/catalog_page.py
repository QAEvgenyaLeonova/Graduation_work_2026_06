import json
import os
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
    NoSuchElementException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import allure


class CatalogPage:
    """Page Object для главной страницы сайта Читай-город"""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)
        self.short_wait = WebDriverWait(driver, 3)

        # Загрузка тестовых данных
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "..", "..", "test_data.json")
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                self.test_data = json.load(f)
        except FileNotFoundError:
            self.test_data = {"search_phrases": ["Пушкин"], "no_result_phrase": "xyz"}

    MAIN_PAGE_URL = "https://www.chitai-gorod.ru/"

    # Локаторы
    INPUT_SEARCH = "//input[@id='app-search']"
    SEARCH_BUTTON = "//button[@type='submit' and @aria-label='Найти']"
    PRODUCT_CARD = "//article[contains(@class, 'product-card')]"
    BOOK_TITLE = "//div[@class='product-card__title']"
    BOOK_AUTHOR = "//span[@class='product-card__subtitle']"
    NO_RESULTS = "//div[contains(text(), 'ничего не нашлось')]"
    ADD_TO_CART = '//button[@data-testid-button-mini-product-card="canBuy"]'
    CART_COUNT = "//div[@data-testid-indicator-header]"
    CART_BUTTON = '//button[@aria-label="Корзина"]'
    CART_ITEM = '//div[@class="cart-item"]'
    EMPTY_CART = '//p[@class="cart-multiple-delete__title"]'
    CLEAR_CART = '//button[@data-testid-button-cart="clearAll"]'
    CHECKOUT_BUTTON = '//div[text()=" Оформить"]'

    @allure.step("Открыть главную страницу")
    def open_main(self) -> None:
        self.driver.get(self.MAIN_PAGE_URL)
        self._close_overlay()

    @allure.step("Закрыть оверлей")
    def _close_overlay(self) -> None:
        try:
            overlays = [
                "//button[contains(., 'Да, я здесь')]",
                "//button[@aria-label='Закрыть']",
                "//div[@class='modal__close']",
                "//button[contains(@class, 'close')]"
            ]
            for overlay_xpath in overlays:
                try:
                    button = self.short_wait.until(
                        EC.element_to_be_clickable((By.XPATH, overlay_xpath))
                    )
                    button.click()
                    break
                except (TimeoutException, StaleElementReferenceException):
                    continue
        except Exception:
            pass

    @allure.step("Поиск по фразе: {phrase}")
    def search_by_phrase(self, phrase: str) -> bool:
        self._close_overlay()
        try:
            input_element = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, self.INPUT_SEARCH))
            )
            input_element.clear()
            input_element.send_keys(phrase)
            input_element.send_keys(Keys.ENTER)
            self._wait_for_results()
            return True
        except Exception as e:
            allure.attach(self.driver.get_screenshot_as_png(), name="search_error",
                          attachment_type=allure.attachment_type.PNG)
            return False

    @allure.step("Ожидать загрузки результатов")
    def _wait_for_results(self) -> None:
        try:
            self.wait.until(
                lambda driver: (
                    len(driver.find_elements(By.XPATH, self.PRODUCT_CARD)) > 0 or
                    len(driver.find_elements(By.XPATH, self.NO_RESULTS)) > 0
                )
            )
        except TimeoutException:
            pass

    @allure.step("Получить названия книг")
    def get_book_titles(self) -> list:
        try:
            elements = self.driver.find_elements(By.XPATH, self.BOOK_TITLE)
            return [el.text.strip() for el in elements if el.text.strip()]
        except:
            return []

    @allure.step("Получить авторов книг")
    def get_book_authors(self) -> list:
        try:
            elements = self.driver.find_elements(By.XPATH, self.BOOK_AUTHOR)
            return [el.text.strip() for el in elements if el.text.strip()]
        except:
            return []

    @allure.step("Получить количество результатов")
    def get_results_count(self) -> int:
        try:
            elements = self.driver.find_elements(By.XPATH, self.PRODUCT_CARD)
            return len(elements)
        except:
            return 0

    @allure.step("Проверить наличие сообщения об отсутствии результатов")
    def is_no_results(self) -> bool:
        try:
            element = self.driver.find_element(By.XPATH, self.NO_RESULTS)
            return element.is_displayed()
        except NoSuchElementException:
            return False

    @allure.step("Проверить наличие поля поиска")
    def is_search_input_present(self, timeout: int = 5) -> bool:
        return self._is_element_present(self.INPUT_SEARCH, timeout)

    @allure.step("Проверить наличие кнопки поиска")
    def is_search_button_present(self, timeout: int = 5) -> bool:
        return self._is_element_present(self.SEARCH_BUTTON, timeout)

    @allure.step("Проверить наличие иконки корзины")
    def is_cart_button_present(self, timeout: int = 5) -> bool:
        return self._is_element_present(self.CART_BUTTON, timeout)

    @allure.step("Проверить наличие кнопки 'Оформить'")
    def is_checkout_visible(self, timeout: int = 5) -> bool:
        try:
            wait = WebDriverWait(self.driver, timeout)
            button = wait.until(EC.element_to_be_clickable((By.XPATH, self.CHECKOUT_BUTTON)))
            return button.is_displayed()
        except TimeoutException:
            return False

    @allure.step("Проверить, пуста ли корзина")
    def is_cart_empty(self) -> bool:
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, self.EMPTY_CART)))
            return True
        except TimeoutException:
            items = self.driver.find_elements(By.XPATH, self.CART_ITEM)
            return len(items) == 0

    @allure.step("Добавить первую книгу в корзину")
    def add_first_book_to_cart(self) -> bool:
        try:
            button = self.wait.until(EC.element_to_be_clickable((By.XPATH, self.ADD_TO_CART)))
            try:
                button.click()
            except:
                self.driver.execute_script("arguments[0].click();", button)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    @allure.step("Получить количество товаров в корзине")
    def get_cart_count(self) -> int:
        try:
            element = self.wait.until(EC.presence_of_element_located((By.XPATH, self.CART_COUNT)))
            return int(element.text)
        except (TimeoutException, ValueError):
            return 0

    @allure.step("Перейти в корзину")
    def go_to_cart(self) -> None:
        try:
            button = self.wait.until(EC.element_to_be_clickable((By.XPATH, self.CART_BUTTON)))
            button.click()
        except:
            pass

    @allure.step("Очистить корзину")
    def clear_cart(self) -> bool:
        try:
            button = self.wait.until(EC.element_to_be_clickable((By.XPATH, self.CLEAR_CART)))
            button.click()
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def _is_element_present(self, xpath: str, timeout: int) -> bool:
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except TimeoutException:
            return False
        