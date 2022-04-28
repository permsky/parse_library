import argparse
import json
import os
import requests
import sys

from bs4 import BeautifulSoup
from loguru import logger
from pathvalidate import sanitize_filename, sanitize_filepath
from urllib.parse import urljoin, urlsplit


def check_for_redirect(response: requests.models.Response) -> None:
    '''Check exist book or not.'''
    if response.history:
        raise requests.HTTPError('\nОшибка при запросе текста книги')


def parse_book_title_and_author(soup: BeautifulSoup) -> tuple[str, str]:
    '''Parse book title and author.'''
    title = soup.select_one('h1').text.split('::')
    return title[0].strip(), title[1].strip()


def parse_book_links(soup: BeautifulSoup) -> list[str]:
    '''Parse book links.'''
    tables = soup.select('.d_book')
    links = [table.select_one('a[href]')['href'] for table in tables]
    return [urljoin('https://tululu.org', link) for link in links]


def dump_to_json(book: dict) -> None:
    '''Write information about book in json-file.'''
    with open('books.json', 'w', encoding='utf-8') as books_file:
        json.dump(book, books_file, indent=4, ensure_ascii=False)


def save_txt(
    response: requests.models.Response,
    filename: str,
    folder: str='books/'
) -> str:
    '''Save txt-file and return filepath.'''
    filename = sanitize_filename(filename)
    folder = sanitize_filepath(folder)
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    with open(filepath, 'w') as file:
        file.write(response.text)
    return filepath


def parse_img_url(soup: BeautifulSoup) -> str:
    '''Get book cover image url.'''
    img = soup.select_one('.bookimage a img')['src']
    if img:
        return urljoin('https://tululu.org', img)
    return 'https://tululu.org/images/nopic.gif'


def download_image(url: str) -> None:
    '''Download book cover images.'''
    response = requests.get(url)
    response.raise_for_status()
    os.makedirs('images', exist_ok=True)
    filename = urlsplit(url)[-3].split('/')[-1]
    filepath = os.path.join('images', filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def parse_comments(soup: BeautifulSoup) -> list[str]:
    '''Parse comments for book.'''
    comments_section = soup.select('.texts')
    comments = [comment.select_one('.black').text for comment \
        in comments_section]
    return comments


def parse_book_genres(soup: BeautifulSoup) -> list[str]:
    '''Parse book genres.'''
    genres_links = soup.select_one('span.d_book').select('a')
    return [genre_link.text for genre_link in genres_links]


def parse_book_page(soup: BeautifulSoup) -> dict:
    '''Parse book page.'''
    title, author = parse_book_title_and_author(soup)
    return {
        'title': title,
        'author': author,
        'img_url': parse_img_url(soup),
        'genres': parse_book_genres(soup),
        'comments': parse_comments(soup)
    }


def parse_last_page_number(soup:BeautifulSoup) -> str:
    '''Parse last page number of list of books.'''
    pages = soup.select('.center a')
    return [page.text for page in pages][-1]


@logger.catch
def main() -> None:
    '''Download books from tululu.org.'''
    logger.add(sys.stderr, level='ERROR')

    parser = argparse.ArgumentParser(
        description='''
            Скачивание научной фантастики из онлайн-библиотеки по номеру
            страницы сайта, начиная с start_page (по умолчанию 1)
            и заканчивая end_page-1 (по умолчанию 10).
        '''
    )
    parser.add_argument(
        '-s',
        '--start_page',
        type=int,
        help='Стартовая страница',
    )
    parser.add_argument(
        '-e',
        '--end_page',
        type=int,
        help='Последняя страница',
    )
    args = parser.parse_args()

    start_page = 1
    end_page = 11
    if args.start_page:
        response = requests.get(f'https://tululu.org/l55')
        response.raise_for_status()
        end_page = 1 + int(
            parse_last_page_number(
                BeautifulSoup(response.text, 'lxml')
            )
        )
        start_page = int(args.start_page)
        if args.end_page:
            if start_page >= end_page - 1:
                print('start_page не может быть больше или равно end_page')
                sys.exit()
            end_page = int(args.end_page)
    books = list()
    for page in range(start_page, end_page):
        response = requests.get(f'https://tululu.org/l55/{page}')
        response.raise_for_status()
        links = parse_book_links(BeautifulSoup(response.text, 'lxml'))
        for link in links:
            book_id = link[20:-1]
            get_params = {'id': book_id}
            txt_response = requests.get(
                'https://tululu.org/txt.php',
                params=get_params
            )
            try:
                txt_response.raise_for_status()
                check_for_redirect(txt_response)
                response = requests.get(link)
                response.raise_for_status()
                book = parse_book_page(BeautifulSoup(response.text, 'lxml'))
                download_image(book['img_url'])
            except requests.HTTPError as err:
                logger.error(err)
                continue
            filename = f'{book_id}. {book["author"]} - {book["title"]}.txt'
            save_txt(
                response=txt_response,
                filename=filename
            )
            book['book_path'] = os.path.join('books', filename)
            books.append(book)
        dump_to_json(books)


if __name__ == '__main__':
    main()
