import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@pytest.fixture(scope="function")
def browser(request):
    """Фикстура для инициализации и завершения работы браузера"""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    # Поддержка headless режима через командную строку
    if request.config.getoption("--headless"):
        options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    yield driver

    driver.quit()


def pytest_addoption(parser):
    """Добавление кастомной опции для запуска в headless режиме"""
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Запуск в headless режиме (без графического интерфейса)",
    )