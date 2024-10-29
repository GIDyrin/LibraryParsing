import re
from bs4 import BeautifulSoup as bs
from downloadFuncs import download_zip, download_img, unzip_archive
import requests
from zipfile import ZipFile
from entities import Author, Book


fetch_url = 'http://az.lib.ru'
file_format = '.fb2.zip'


def get_authors_links(htmlContext):
    ps = htmlContext.find_all('p')
    all_links = []
    for author in ps:
        author_p = bs(author.decode(), 'lxml')
        refs = author_p.find_all('a')
        refs.pop(len(refs) - 1)
        refs.pop(0)
        for anchor in refs:
            all_links.append(anchor.get('href'))
    return all_links


def get_books_links(dl_block):
    links = []
    flag = True
    for tag in dl_block.children:
        if tag.name == 'p' and (tag.text.strip() == 'О творчестве автора:' or tag.text.strip() == 'Об авторе:'):
            flag = False
            continue
        elif tag.name == 'p' and not (tag.text.strip() == 'О творчестве автора:' or tag.text.strip() == 'Об авторе:'):
            flag = True
            continue

        if flag:
            if tag.name:
                a_tag = tag.find('a', href=re.compile(r"^text.+"))
                if a_tag:
                    links.append(a_tag.parent)
    return links


def process_author_page(url_to_author):
    author_resp = requests.get(fetch_url + url_to_author)
    author_name = url_to_author.split('/')[2]

    htmlText = bs(author_resp.text, 'lxml')
    author = fetch_author_info(htmlText, author_name, url_to_author)
    books = fetch_author_books(htmlText, author_name, url_to_author)
    return author, books


def fetch_author_info(htmlContext, author_name, author_url):
    portrait = htmlContext.find('img')
    photo_path = ''
    if portrait:
        img_url = fetch_url + author_url + portrait.get('src')
        photo_path = download_img(img_url, author_name)

    #Сводка по биографии
    bio = htmlContext.find('i').text.strip()

    #ФИО
    h2_text = htmlContext.h2.get_text()
    name = h2_text.split(':')[-2].strip()

    info_table = htmlContext.table

    #Годы жизни
    lines = info_table.find_all('li')
    lifeline = lines[1].text
    places = lines[2].text

    opa = lifeline.split('--')
    opa[0] = opa[0].strip()
    opa[1] = opa[1].strip()
    bio += '\n ' + opa[0] + ' - ' + opa[1] + '\n ' + places
    return Author(name ,bio, photo_path)


def fetch_author_books(htmlContext, author_name, author_url):
    books = []
    dl_block = htmlContext.dl
    links = get_books_links(dl_block)
    for link in links:
        file_path = download_zip(fetch_url + author_url + author_name + '-' + link.a.get('href').split('.')[0] + file_format, author_name)
        small_tags = link.find_all('small')
        title = link.a.text
        # Фильтруем по регулярному выражению
        date = [tag for tag in small_tags if re.match(r'\[(\d+)\]', tag.text)]
        book_genres = [genre.strip() for genre in small_tags[-1].text.split(',')]
        books.append(Book(title, date, file_path))

    return books


response = requests.get(fetch_url)

if not response.ok:
    print('FETCHING ERROR, USING PREVIOUS HTMLTREE')
    with open('html.txt', 'r', encoding='cp1251') as f:
        htmlTree = f.read()
else:
    with open('html.txt', 'w', encoding='cp1251') as f:
        f.write(response.text)
    htmlTree = response.text

soup = bs(htmlTree, 'lxml')
authors_links = get_authors_links(soup)

for i in range(5):
    author_entity, books_entity = process_author_page(authors_links[i])







