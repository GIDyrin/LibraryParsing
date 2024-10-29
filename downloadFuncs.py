import requests
from zipfile import ZipFile
import os

def download_img(url, author_name):
    resp = requests.get(url)
    if resp.status_code == 200:
        if not os.path.exists('portraits'):
            os.mkdir('portraits')
        file_name = os.path.join('portraits', author_name + url.split('/')[-1])
        with open(file_name, 'wb') as file:
            # Запись содержимого файла
            for chunk in resp.iter_content(chunk_size=8192):
                file.write(chunk)

        return  file_name


def download_zip(url, author_name):
    resp = requests.get(url)
    if resp.status_code == 200:
        if not os.path.exists('classic_books'):
            os.mkdir('classic_books')
        if not os.path.exists(os.path.join('classic_books', author_name)):
            os.mkdir(os.path.join('classic_books', author_name))
        file_path = os.path.join(os.path.join('classic_books', author_name), url.split('/')[-1])
        # Открытие файла в бинарном режиме
        with open(file_path, 'wb') as file:
            # Запись содержимого файла
            for chunk in resp.iter_content(chunk_size=8192):
                file.write(chunk)

        return file_path


def unzip_archive(filepath, record_path):
    with ZipFile('filepath', 'r') as unzip:
        unzip.extractall(path=record_path)