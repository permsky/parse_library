import os
import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath
from typing import Union
from urllib.error import HTTPError
from urllib.parse import urljoin


def check_for_redirect(response: requests.models.Response) -> None:
    '''Check exist book or not.'''
    if response.history:
        if response.history[0].status_code == 302:
            raise HTTPError(
                url=response.url,
                code=302,
                msg='Книга не найдена',
                hdrs='',
                fp=None
            )


def parse_book(id: int) -> tuple[str, str]:
    '''Parse book title and author.'''
    url = f'https://tululu.org/b{id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.find('h1').text
    title = title.split('::')
    return title[0].strip(), title[1].strip()


def download_txt(
    url: str,
    filename: str,
    folder: str='books/'
) -> str:
    '''Download txt-file and return filepath.'''
    filename = sanitize_filename(filename)
    folder = sanitize_filepath(folder)
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    response = requests.get(url)
    response.raise_for_status()
    with open(filepath, 'w') as file:
        file.write(response.text)
    return filepath


def get_img_url(id: int) -> str:
    '''Get book cover image url.'''
    url = f'https://tululu.org/b{id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    img = soup.find('div', class_='bookimage').find('a').find('img')['src']
    if img:
        return urljoin('https://tululu.org', img)
    return 'https://tululu.org/images/nopic.gif'


def download_books(books_count: int) -> None:
    '''Download books from tululu.org.'''
    for id in range(1, books_count + 1):
        url = f'https://tululu.org/txt.php?id={id}'
        response = requests.get(url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except HTTPError:
            continue
        book = parse_book(id)
        filename = f'{book[1]} - {book[0]}.txt'
        download_txt(
            url=url,
            filename=filename
        )


if __name__ == '__main__':
    download_books(10)
