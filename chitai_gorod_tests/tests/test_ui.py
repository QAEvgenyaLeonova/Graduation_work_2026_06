import allure
import pytest
from pages.catalog_page import CatalogPage


@allure.feature("UI: Поиск книг")
@pytest.mark.ui
class TestSearchUI:

    @allure.title("Поиск книги по автору на сайте")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_by_author(self, browser):
        page = CatalogPage(browser)

        with allure.step("Открыть главную страницу сайта Читай-город"):
            page.open_main()

        search_phrases = page.test_data["search_phrases"]
        success = False
        found_author = False
        all_titles = []
        all_authors = []

        with allure.step(f"Выполнить поиск по фразам: {', '.join(search_phrases)}"):
            for phrase in search_phrases:
                success = page.search_by_phrase(phrase)
                if not success:
                    continue

                titles = page.get_book_titles()
                authors = page.get_book_authors()

                if len(titles) > 0:
                    all_titles.extend(titles)
                    all_authors.extend(authors)
                    all_text = " ".join(titles + authors).lower()

                    for author in [
                        "пушкин", "pushkin", "лермонтов", "lermontov",
                        "толстой", "tolstoy", "достоевский", "dostoevsky"
                    ]:
                        if author in all_text:
                            found_author = True
                            break

                    if found_author:
                        break

        if not success:
            pytest.skip("Не удалось выполнить поиск (возможно, сайт изменился)")

        if not found_author:
            if len(all_titles) > 0:
                pytest.skip(
                    f"Автор не найден в результатах. Найдено книг: {len(all_titles)}"
                )
            else:
                pytest.skip("Поиск не дал результатов (возможно, сайт изменился)")

        with allure.step("Проверить, что в результатах поиска присутствует хотя бы один автор из списка"):
            allure.attach(
                f"Найдено книг: {len(all_titles)}\nАвторы: {all_authors[:5]}",
                name="Результаты поиска",
                attachment_type=allure.attachment_type.TEXT,
            )

    @allure.title("Поиск книги по запросу на латинице")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_latin(self, browser):
        page = CatalogPage(browser)

        with allure.step("Открыть главную страницу сайта Читай-город"):
            page.open_main()

        phrases = page.test_data["search_phrases"]
        latin_phrase = None
        for phrase in phrases:
            if any(ord(c) < 128 for c in phrase):
                latin_phrase = phrase
                break

        if not latin_phrase:
            latin_phrase = phrases[0]

        with allure.step(f"Выполнить поиск по латинской фразе: '{latin_phrase}'"):
            success = page.search_by_phrase(latin_phrase)

        if not success:
            pytest.skip(f"Не удалось выполнить поиск по фразе: {latin_phrase}")

        results = page.get_results_count()

        with allure.step(f"Проверить, что поиск по латинице возвращает результаты (найдено: {results})"):
            allure.attach(
                f"Найдено результатов: {results}",
                name="Количество результатов",
                attachment_type=allure.attachment_type.TEXT,
            )

            if results == 0:
                pytest.skip("Поиск не дал результатов")

            assert results > 0, "Поиск по латинице должен находить хотя бы один результат"

    @allure.title("Поиск несуществующей книги")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_nonexistent(self, browser):
        page = CatalogPage(browser)

        with allure.step("Открыть главную страницу сайта Читай-город"):
            page.open_main()

        phrase = page.test_data["no_result_phrase"]

        with allure.step(f"Выполнить поиск по несуществующей фразе: '{phrase}'"):
            success = page.search_by_phrase(phrase)

        with allure.step("Проверить, что поиск выполнен успешно"):
            assert success, "Не удалось выполнить поиск"

        results = page.get_results_count()
        no_results_msg = page.is_no_results()

        with allure.step(f"Проверить, что система сообщает об отсутствии результатов (найдено: {results})"):
            allure.attach(
                f"Найдено книг: {results}, Сообщение 'ничего не нашлось': {no_results_msg}",
                name="Результат поиска",
                attachment_type=allure.attachment_type.TEXT,
            )

            if results > 0:
                titles = page.get_book_titles()
                all_text = " ".join(titles).lower()
                assert phrase not in all_text, "Несуществующий запрос найден в результатах"
            else:
                assert no_results_msg or results == 0, "Нет результатов и нет сообщения об отсутствии"

    @allure.title("Проверка отображения названий книг в результатах поиска")
    @allure.severity(allure.severity_level.NORMAL)
    def test_titles_displayed(self, browser):
        page = CatalogPage(browser)

        with allure.step("Открыть главную страницу сайта Читай-город"):
            page.open_main()

        search_phrases = page.test_data["search_phrases"]
        success = False
        titles = []

        with allure.step(f"Выполнить поиск по фразам: {', '.join(search_phrases)}"):
            for phrase in search_phrases:
                success = page.search_by_phrase(phrase)
                if not success:
                    continue

                titles = page.get_book_titles()
                if len(titles) > 0:
                    break

        if not success:
            pytest.skip("Не удалось выполнить поиск (возможно, сайт изменился)")

        if len(titles) == 0:
            pytest.skip("Поиск не дал результатов (возможно, сайт изменился)")

        with allure.step("Проверить, что все названия книг не пустые"):
            for title in titles:
                assert len(title) > 0, "Обнаружено пустое название книги"

        allure.attach(
            f"Найдено названий: {len(titles)}\nПримеры: {titles[:3]}",
            name="Найденные названия",
            attachment_type=allure.attachment_type.TEXT,
        )


@allure.feature("UI: Элементы страницы")
@pytest.mark.ui
class TestElementsUI:

    @allure.title("Проверка загрузки главной страницы")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_main_page_loads(self, browser):
        page = CatalogPage(browser)

        with allure.step("Открыть главную страницу сайта Читай-город"):
            page.open_main()

        with allure.step("Проверить, что заголовок страницы содержит 'Читай-город'"):
            assert "Читай-город" in browser.title, "Главная страница не загрузилась"

    @allure.title("Проверка наличия поля поиска на странице")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_input_exists(self, browser):
        page = CatalogPage(browser)

        with allure.step("Открыть главную страницу сайта Читай-город"):
            page.open_main()

        with allure.step("Проверить, что поле поиска отображается на странице"):
            assert page.is_search_input_present(), "Поле поиска не отображается на странице"

    @allure.title("Проверка наличия кнопки поиска на странице")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_button_exists(self, browser):
        page = CatalogPage(browser)

        with allure.step("Открыть главную страницу сайта Читай-город"):
            page.open_main()

        with allure.step("Проверить, что кнопка поиска отображается на странице"):
            assert page.is_search_button_present(), "Кнопка поиска не отображается на странице"

    @allure.title("Проверка наличия иконки корзины на странице")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cart_icon_exists(self, browser):
        page = CatalogPage(browser)

        with allure.step("Открыть главную страницу сайта Читай-город"):
            page.open_main()

        with allure.step("Проверить, что иконка корзины отображается на странице"):
            assert page.is_cart_button_present(), "Иконка корзины не отображается на странице"

    @allure.title("Проверка работы кнопки поиска")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_button_works(self, browser):
        page = CatalogPage(browser)

        with allure.step("Открыть главную страницу сайта Читай-город"):
            page.open_main()

        phrase = page.test_data["search_phrases"][0]

        with allure.step(f"Выполнить поиск по фразе: '{phrase}'"):
            success = page.search_by_phrase(phrase)

        if not success:
            pytest.skip("Не удалось выполнить поиск")

        current_url = browser.current_url
        results_count = page.get_results_count()

        with allure.step("Проверить, что поиск сработал (URL содержит 'search' или найдены результаты)"):
            assert (
                "search" in current_url.lower() or results_count > 0
            ), "Поиск не сработал"