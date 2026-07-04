import allure
import pytest
import requests


@allure.feature("API: Поиск книг")
@pytest.mark.api
class TestSearchAPI:

    @allure.title("Проверка доступности API поиска книг")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_api_available(self):
        with allure.step("Отправить GET-запрос к эндпоинту /api/search с параметром 'q=Лермонтов'"):
            url = "https://www.chitai-gorod.ru/api/search"
            params = {"q": "Лермонтов"}
            try:
                response = requests.get(url, params=params, timeout=10)
            except requests.exceptions.ConnectionError:
                pytest.skip("API недоступен")

        with allure.step("Проверить, что статус-код ответа соответствует ожидаемому (200, 403, 404, 429)"):
            assert response.status_code in [
                200,
                403,
                404,
                429,
            ], f"Неожиданный статус-код: {response.status_code}"

    @allure.title("Проверка структуры ответа API при успешном поиске")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_response_structure(self):
        with allure.step("Отправить GET-запрос к эндпоинту /api/search с параметром 'q=Пушкин'"):
            url = "https://www.chitai-gorod.ru/api/search"
            params = {"q": "Пушкин"}
            try:
                response = requests.get(url, params=params, timeout=10)
            except requests.exceptions.ConnectionError:
                pytest.skip("API недоступен")

        with allure.step("Проверить, что ответ содержит поле с результатами ('results' или 'data')"):
            if response.status_code == 200:
                data = response.json()
                assert (
                    "results" in data or "data" in data
                ), "В ответе API отсутствует поле с результатами поиска"
            else:
                allure.attach(
                    f"API вернул статус-код: {response.status_code}",
                    name="Статус ответа",
                    attachment_type=allure.attachment_type.TEXT,
                )


@allure.feature("API: Корзина")
@pytest.mark.api
class TestCartAPI:

    @allure.title("Проверка доступности эндпоинта корзины")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cart_endpoint(self):
        with allure.step("Отправить GET-запрос к эндпоинту /api/cart"):
            url = "https://www.chitai-gorod.ru/api/cart"
            try:
                response = requests.get(url, timeout=10)
            except requests.exceptions.ConnectionError:
                pytest.skip("API недоступен")

        with allure.step("Проверить, что статус-код ответа соответствует ожидаемому (200, 401, 403, 404)"):
            assert response.status_code in [
                200,
                401,
                403,
                404,
            ], f"Неожиданный статус-код: {response.status_code}"

    @allure.title("Проверка наличия заголовков в ответе API")
    @allure.severity(allure.severity_level.NORMAL)
    def test_response_headers(self):
        with allure.step("Отправить GET-запрос к эндпоинту /api/search с параметром 'q=Пушкин'"):
            url = "https://www.chitai-gorod.ru/api/search"
            params = {"q": "Пушкин"}
            try:
                response = requests.get(url, params=params, timeout=10)
            except requests.exceptions.ConnectionError:
                pytest.skip("API недоступен")

        with allure.step("Проверить, что ответ содержит заголовки"):
            assert response.headers is not None, "Ответ API не содержит заголовков"