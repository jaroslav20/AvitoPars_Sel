# AvitoPars_Sel

Веб-парсер, написанный на Python с использованием библиотеки selenium_stealth
=======

Этот проект представляет собой веб-парсер, написанный на Python с использованием библиотеки selenium_stealth. Он извлекает данные с веб-страниц и сохраняет их в формате CSV.


## Функциональные возможности

- Парсинг данных с различных веб-страниц, указанных в JSON файле.
- Сохранение извлеченных данных в CSV файл.
- Поддержка пагинации (переход между страницами).
- Использование `selenium_stealth` для сокрытия автоматизации.


## Установка

1. Склонируйте репозиторий с github:

``
git clone https://github.com/jaroslav20/AvitoPars_Sel.git
``
2. Перейдите в директорию проекта:
```
cd AvitoPars_Sel
```

3. Убедитесь, что у вас установлен Python 3.7 или выше.

4. Установите необходимые библиотеки:

   ```bash
   pip install -r requirements.txt
   



## Использование
1. Файл конфигурации cfg_params.json для настройки параметров парсинга.
Перед запуском нужно зайти на avito.ru и настроить по фильтрам то, что вы хотите найти и скопировать получившийся url в файл pars_urls.json, содержащий имя файла на выходе и URL для парсинга.
Сколько url к парсингу, столько и имен файлов:

```
{
    "file_name_1": "https://example.com/page1",
    "file_name_2": "https://example.com/page2",
   
}
```


Почти всегда при ручном завершение скрипта сайт выдает капчу, при следущем запуске. Поэтому headless режим закоментирован, но если давать отрабатывать до конца, можно раскоментировать.

```
class WebDriverManager:
    """Управляет настройкой и запуском браузера."""
    ...
# Устанавливаем headless режим
        # options.add_argument("--headless=new")  # Новый headless режим для более новых версий Chrome
        # options.add_argument("--window-size=1920,1080")  # Задаем размер окна для корректной работы headless
        # options.add_argument("--disable-gpu")  # Отключаем GPU для headless на старых версиях Chrome
```

2. Запустите скрипт parser.py:

```bash
python parser.py
```
3. Скрипт выполнит следующие шаги:

- Инициализирует драйвер браузера с необходимыми параметрами.
- Прочитает URL из файла pars_urls.json.
- Извлечет данные с указанных страниц.
- Сохранит данные в CSV файлы с именами, соответствующими ключам из pars_urls.json.


## Структура проекта:

- parser.py - Основной скрипт для парсинга.
- cfg_params.json - Файл конфигурации с селекторами для извлечения данных.
- pars_urls.json - Файл с URL для парсинга.
- `+` файл\ы.csv с вашими данными по завершение работы скрипта.


## Пример CSV файла:

```
title,price,description,url,data_publ
"Пример заголовка","1000","Пример описания","https://example.com/item1","2024-09-11"
```

## Лицензия
Этот проект предоставляется под лицензией MIT. См. LICENSE для получения дополнительной информации.

## Notes
Весь код проекта служит только в ознакомительных целях и не ставит задачу вдредительства сайта. Все данные собираемые предоставленны в открытый доступ и не содержат конфедициальной информации.

