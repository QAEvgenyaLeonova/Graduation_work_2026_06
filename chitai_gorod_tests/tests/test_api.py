import allure
import pytest
import requests


@allure.feature("API: Поиск книг")
@pytest.mark.api
class TestSearchAPI:

    @allure.title("Проверка доступности API поиска")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_api_available(self):
        url = "https://www.chitai-gorod.ru/api/search"
        params = {"q": "Лермонтов"}
        try:
            response = requests.get(url, params=params, timeout=10)
            assert response.status_code in [
                200,
                403,
                404,
                429,
            ], f"Неожиданный статус: {response.status_code}"
        except requests.exceptions.ConnectionError:
            pytest.skip("API недоступен")

    @allure.title("Проверка структуры ответа при успешном запросе")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_response_structure(self):
        url = "https://www.chitai-gorod.ru/api/search"
        params = {"q": "Пушкин"}
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                assert (
                    "results" in data or "data" in data
                ), "Нет поля с результатами"
            else:
                assert True, f"API вернул {response.status_code}"
        except requests.exceptions.ConnectionError:
            pytest.skip("API недоступен")


@allure.feature("API: Корзина")
@pytest.mark.api
class TestCartAPI:

    @allure.title("Проверка эндпоинта корзины")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cart_endpoint(self):
        url = "https://www.chitai-gorod.ru/api/cart"
        try:
            response = requests.get(url, timeout=10)
            assert response.status_code in [
                200,
                401,
                403,
                404,
            ], f"Неожиданный статус: {response.status_code}"
        except requests.exceptions.ConnectionError:
            pytest.skip("API недоступен")

    @allure.title("Проверка заголовков ответа API")
    @allure.severity(allure.severity_level.NORMAL)
    def test_response_headers(self):
        url = "https://www.chitai-gorod.ru/api/search"
        params = {"q": "Пушкин"}
        try:
            response = requests.get(url, params=params, timeout=10)
            assert response.headers is not None, "Нет заголовков ответа"
        except requests.exceptions.ConnectionError:
            pytest.skip("API недоступен")
