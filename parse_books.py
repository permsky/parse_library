import os
import requests

from bs4 import BeautifulSoup
from urllib.error import HTTPError


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


def download_books(books_count: int) -> None:
    '''Download books from tululu.org.'''
    os.makedirs('books', exist_ok=True)

    for id in range(1, books_count + 1):
        url = f'https://tululu.org/txt.php?id={id}'
        response = requests.get(url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except HTTPError:
            continue
        book = parse_book(id)
        filename = f'books/{book[1]} - {book[0]}.txt'
        with open(filename, 'w') as file:
            file.write(response.text)


if __name__ == '__main__':
    download_books(10)
