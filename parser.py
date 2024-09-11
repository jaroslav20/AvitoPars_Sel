from selenium import webdriver
import selenium.common.exceptions as exc
from selenium.webdriver.common.by import By
from selenium_stealth import stealth

import csv
import json
import time
import random
from typing import Optional, Dict


class CfgParamsLoader:
    """Загружает конфигурационные параметры из файла"""

    def __init__(self, config_path: str = 'cfg_params.json'):
        self.cfg_params = self.load_config(config_path)

    @staticmethod
    def load_config(config_path):
        """Загрузка конфигурации из JSON файла"""

        with open(config_path, 'r') as file:
            return json.load(file)


class WebDriverManager:
    """Управляет настройкой и запуском браузера."""

    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None

    def configure_driver(self):
        """Настройка и запуск браузера с необходимыми опциями."""

        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"]) # Исключение переключателя, который указывает на использование автоматизации
        options.add_experimental_option('useAutomationExtension', False) # Отключение расширение автоматизации Chrome
        options.add_argument('--disable-blink-features=AutomationControlled')  # Отключение флага автоматизации

        # Устанавливаем headless режим
        # options.add_argument("--headless=new")  # Новый headless режим для более новых версий Chrome
        # options.add_argument("--window-size=1920,1080")  # Задаем размер окна для корректной работы headless
        # options.add_argument("--disable-gpu")  # Отключаем GPU для headless на старых версиях Chrome

        self.driver = webdriver.Chrome(options=options)

        # Применение stealth-маскировки
        stealth(
            self.driver,
            languages=["ru-RU", "ru"],
            vendor="Google Inc.",
            platform="Win64",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        # Переопределение navigator.webdriver
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                   Object.defineProperty(navigator, 'webdriver', {
                     get: () => undefined
                   })
               '''
        })

    def quit_driver(self) -> None:
        """Закрытие драйвера."""

        if self.driver:
            self.driver.quit()


class URLReader:
    """Читает URL из файла."""

    def __init__(self, file_path: str = 'pars_urls.json'):
        self.file_path: str = file_path

    def read_urls(self) -> Dict[str, str]:
        """Чтение URL из JSON файла"""

        with open(self.file_path, 'r') as file:
            return json.load(file)


class DataExtractor:
    """Извлекает данные с веб-страницы"""

    def __init__(self, cfg_params):
        self.cfg_params = cfg_params

    @staticmethod
    def safe_find(element, selector: str, attr: Optional[str] = None) -> Optional[str]:
        """Безопасный поиск элемента на странице"""

        try:
            if attr:
                return element.find_element(By.CSS_SELECTOR, selector).get_attribute(attr)
            else:
                return element.find_element(By.CSS_SELECTOR, selector).text
        except exc.NoSuchElementException:
            return None

    def extract_data_from_element(self, title) -> Dict[str, Optional[str]]:
        """Извлечение данных из одного объявления"""

        selectors = self.cfg_params['selectors']

        # Динамически генерируем словарь данных на основе конфигурации селекторов
        data = {}
        for field, selector in selectors.items():
            if field == 'url':
                # Если это поле 'url', используем атрибут 'href'
                data['url'] = self.safe_find(title, selector, attr="href")
            else:
                # Для остальных полей используем обычный поиск текста
                data[field] = self.safe_find(title, selector)

        # Если цена присутствует, меняем формат (для примера)
        if 'price' in data and data['price']:
            data['price'] = data['price'].replace(" ", ".")

        return data


class WriterCSV:
    """Записывает данные в .csv файл"""

    def __init__(self, cfg_params, file_name: str):
        self.cfg_params = cfg_params
        self.file_name: str = f"{file_name}.csv"
        self.fieldnames = list(self.cfg_params['selectors'].keys())

    def save_to_csv(self, data):
        with open(self.file_name, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self.fieldnames)

            if file.tell() == 0:
                writer.writeheader()

            writer.writerows(data)


class Parser:
    """Основной парсер для обработки данных со страницы"""

    def __init__(self, driver_manager: WebDriverManager,
                 url_reader: URLReader,
                 data_extractor: DataExtractor,
                 cfg_params):

        self.driver_manager = driver_manager
        self.url_reader = url_reader
        self.data_extractor = data_extractor
        self.cfg_params = cfg_params

    def print_data(self, data: dict):
        """Вывод данных объявления"""

        print("\n".join([f"{k}: {v}" for k, v in data.items()]))
        print("=" * 100)

    def parse_titles(self, csv_writer: WriterCSV):
        """Извлечение всех объявлений со страницы"""

        titles = self.driver_manager.driver.find_elements(By.CSS_SELECTOR, "[data-marker='item']")
        all_data = []
        for title in titles:
            data = self.data_extractor.extract_data_from_element(title)
            all_data.append(data)
            self.print_data(data)

            # Сохраняем данные в CSV для текущего URL
            csv_writer.save_to_csv(all_data)

        return all_data

    def __paginator(self, csv_writer: WriterCSV):

        count = 0
        while True:
            # Парсим текущую страницу
            print(f"Данные по странице {count+1}")
            self.parse_titles(csv_writer)

            # Находим кнопку для перехода на следующую страницу
            next_button = self.driver_manager.driver.find_elements(By.CSS_SELECTOR,
                                                                   "[data-marker='pagination-button/nextPage']")

            # Проверяем, есть ли кнопка "Следующая страница"
            if next_button:
                try:
                    # Нажимаем на кнопку
                    next_button[0].click()
                    count += 1

                    # Делаем паузу, чтобы страница успела загрузиться
                    time.sleep(random.randint(5, 9))
                except Exception as e:
                    print(f"Ошибка при клике на кнопку следующей страницы: {e}")
                    break
            else:
                # Если кнопки "Следующая страница" нет, заканчиваем цикл
                break

    def run(self):
        """Основной метод для запуска парсинга"""

        self.driver_manager.configure_driver()
        urls = self.url_reader.read_urls()

        for file_name, url in urls.items():
            # Переход на страницу
            print(f"Парсинг URL: {url}")
            print("٩(◕‿◕)۶")
            self.driver_manager.driver.get(url)
            time.sleep(15)  # Задержка для загрузки страницы

            # Создание отдельного CSV файла для каждого URL
            csv_writer = WriterCSV(self.cfg_params, file_name)  # Создаем csv_writer

            # Парсинг объявлений на текущей странице с пагинацией
            self.__paginator(csv_writer)

            # Задержка перед переходом к следующему URL
            time.sleep(random.randint(5, 17))

        # Завершение работы драйвера
        self.driver_manager.quit_driver()


if __name__ == "__main__":
    cfg_params = CfgParamsLoader()
    driver_manager = WebDriverManager()
    url_reader = URLReader()
    data_extractor = DataExtractor(cfg_params.cfg_params)

    parser = Parser(driver_manager, url_reader, data_extractor, cfg_params.cfg_params)
    parser.run()



