# Парсер книг с сайта tululu.org
Скрипт предназначен для скачивания книг с сайта tululu.org. Книги сохраняются в директории `books`, изображения обложек книг - в `images`. В консоль выводится название текстового файла скачанной книги, список жанров, к которым можно отнести данную книгу, и комментарии пользователей сайта tululu.org о данной книге. По умолчанию скрипт пытается скачать 10 первых книг. Количество скачиваемых книг можно регулировать с помощью опциональных аргументов.

### Запуск

- Скачайте код
- Настройте окружение. Для этого выполните следующие действия:
  - установите Python3.x;
  - создайте виртуальное окружение [virtualenv/venv](https://docs.python.org/3/library/venv.html) для изоляции проекта и активируйте его.
  - установите необходимые зависимости:

    ```
    pip install -r requirements.txt
    ```
  - запустите скрипт командой:

    ```
    python parse_books.py [-h] [--start_id START_ID] [--end_id END_ID]
    ```

### Аргументы

Доступны следующие опциональные аргументы:
`-s`, `--start_id` - после данного аргумента через пробел указывается id книги, с которой начинается скачивание;
`-e`, `--end_id` - после данного аргумента через пробел указывается id книги, которая скачивается последней.

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).