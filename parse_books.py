from urllib import response
import os
import requests


os.makedirs('books', exist_ok=True)

for id in range(1, 11):
    url = f'https://tululu.org/txt.php?id={id}'
    response = requests.get(url)
    response.raise_for_status()
    filename = f'books/book_id{id}.txt'
    with open(filename, 'w') as file:
        file.write(response.text)
