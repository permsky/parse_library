import argparse
import os
import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit


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


def parse_book_title_and_author(soup: BeautifulSoup) -> tuple[str, str]:
    '''Parse book title and author.'''
    title = soup.find('h1').text.split('::')
    return title[0].strip(), title[1].strip()


def download_txt(
    response: requests.models.Response,
    filename: str,
    folder: str='books/'
) -> str:
    '''Download txt-file and return filepath.'''
    filename = sanitize_filename(filename)
    folder = sanitize_filepath(folder)
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    with open(filepath, 'w') as file:
        file.write(response.text)
    return filepath


def parse_img_url(soup: BeautifulSoup) -> str:
    '''Get book cover image url.'''
    img = soup.find('div', class_='bookimage').find('a').find('img')['src']
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
    comments_section = soup.find_all('div', class_='texts')
    comments = list()
    if comments_section:
        for comment in comments_section:
            comments.append(comment.find('span', class_='black').text)
    return comments


def parse_book_genres(soup: BeautifulSoup) -> list[str]:
    '''Parse book genres.'''
    genres_links = soup.find('span', class_='d_book').find_all('a')
    genres = list()
    for genre_link in genres_links:
        genres.append(genre_link.text)
    return genres


def parse_book_page(soup: BeautifulSoup) -> dict:
    '''Parse book page.'''
    book = dict()
    title, author = parse_book_title_and_author(soup)
    book['title'] = title
    book['author'] = author
    book['img_url'] = parse_img_url(soup)
    book['genres'] = parse_book_genres(soup)
    book['comments'] = parse_comments(soup)
    return book


def main() -> None:
    '''Download books from tululu.org.'''
    parser = argparse.ArgumentParser(
        description='''
            Скачивание книг из онлайн-библиотеки по id книги, начиная
            с start_id и заканчивая end_id.
        '''
    )
    parser.add_argument('-s', '--start_id', help='Начальный id', default=1)
    parser.add_argument('-e', '--end_id', help='Финальный id', default=10)
    args = parser.parse_args()

    for id in range(int(args.start_id), int(args.end_id) + 1):
        url = f'https://tululu.org/txt.php?id={id}'
        txt_response = requests.get(url)
        txt_response.raise_for_status()
        try:
            check_for_redirect(txt_response)
        except HTTPError:
            continue
        response = requests.get(f'https://tululu.org/b{id}/')
        response.raise_for_status()
        book = parse_book_page(BeautifulSoup(response.text, 'lxml'))
        filename = f'{book["author"]} - {book["title"]}.txt'
        print(filename)
        download_txt(
            response=txt_response,
            filename=filename
        )
        download_image(book['img_url'])
        for genre in book['genres']:
            print(f'\n{genre}')
        comments = book['comments']
        if comments:
            for comment in comments:
                print(f'\n{comment}')


if __name__ == '__main__':
    main()
