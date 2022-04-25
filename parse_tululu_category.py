import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin


def get_book_links(soup: BeautifulSoup) -> list[str]:
    '''Return book links.'''
    tables = soup.find_all('table', class_='d_book')
    links = [table.find('a', href=True) for table in tables]
    return [urljoin('https://tululu.org', link['href']) for link in links]


def main() -> None:
    '''.'''
    for page in range(1, 5):
        response = requests.get(f'https://tululu.org/l55/{page}')
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        print(*get_book_links(soup), sep='\n')


if __name__ == '__main__':
    main()
