import requests
from zipfile import ZipFile
import os


def unzip_archive(filepath, record_path):
    with ZipFile(filepath, 'r') as unzip:
        unzip.extractall(path=record_path)


def download_zip(url, author_name):
    if not os.path.exists('classic_books'):
        os.mkdir('classic_books')
    if not os.path.exists(os.path.join('classic_books', author_name)):
        os.mkdir(os.path.join('classic_books', author_name))
    author_path = os.path.join('classic_books', author_name)
    zip_path = os.path.join(os.path.join('classic_books', author_name), url.split('/')[-1])
    file_path = zip_path.split('.')
    file_path = file_path[0] + '.' + file_path[1]

    if os.path.isfile(file_path):
        return file_path

    resp = requests.get(url)
    if resp.status_code == 200:
        # Открытие файла в бинарном режиме
        with open(zip_path, 'wb') as file:
            # Запись содержимого файла
            for chunk in resp.iter_content(chunk_size=32768):
                file.write(chunk)

        unzip_archive(zip_path, author_path)
        os.remove(zip_path)
        return file_path


def download_img(url, author_name):
    if not os.path.exists('portraits'):
        os.mkdir('portraits')
    file_name = os.path.join('portraits', author_name + url.split('/')[-1])
    if os.path.isfile(file_name):
        return file_name

    resp = requests.get(url)
    if resp.status_code == 200:

        with open(file_name, 'wb') as file:
            # Запись содержимого файла
            for chunk in resp.iter_content(chunk_size=65536):
                file.write(chunk)

        return  file_name



