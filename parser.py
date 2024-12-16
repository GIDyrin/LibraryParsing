import re
from bs4 import BeautifulSoup as bs
from downloadFuncs import download_zip, download_img
import requests
from entities import Author, Book, BooksOfAuthor, BooksAndGenres
from db import operateWithDB

fetch_url = 'http://az.lib.ru'
file_format = '.fb2.zip'

def map_of_genres():
    genresMap = {}
    with open('genre.txt', 'r', encoding='cp1251') as genres:
        i = 1
        for genre in genres:
            genresMap[genre.strip()] = i
            i += 1

    return genresMap

def get_bio(page, author_url):
    # Сводка по биографии
    bio = ''
    ref = page.find('a', href='about.shtml', string='Подробнее')
    if not ref:
        bio = page.find('i').text.strip()
    else:
        about = author_url + ref.get('href')
        resp = requests.get(fetch_url + about)
        biog = bs(resp.text, 'lxml')
        br = biog.find('br', clear='all')
        while br.next.name != 'center':
            check = br.name
            br = br.next_element
            bio += br.text.strip()

    return bio + '\n'


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
                    check = a_tag.text
                    if len(check) > 0:
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
    bio = get_bio(htmlContext, author_url)

    #ФИО
    h2_text = htmlContext.h2.get_text()
    name = h2_text.split(':')[-2].strip()

    info_table = htmlContext.table

    #Годы жизни
    lines = info_table.find_all('li')
    lifeline = lines[1].text
    places = lines[2].text

    opa = lifeline.split('--')
    if len(opa) < 2:
        bio += '\n ' + places
    else:
        opa[0] = opa[0].strip()
        opa[1] = opa[1].strip()
        bio += '\n ' + opa[0] + ' - ' + opa[1] + '\n ' + places
    return Author(name ,bio, photo_path)


def fetch_author_books(htmlContext, author_name, author_url):
    books = []
    book_genres = []
    dl_block = htmlContext.dl
    links = get_books_links(dl_block)
    for link in links:
        file_path = download_zip(fetch_url + author_url + author_name + '-' + link.a.get('href').split('.')[0] + file_format, author_name)
        if not file_path:
            continue
        small_tags = link.find_all('small')
        title = link.a.text
        # Фильтруем по регулярному выражению
        date = [tag.text for tag in small_tags if re.match(r'\[(\d+)\]', tag.text)][0]
        date = date[1:-1]

        rate = [tag.text for tag in small_tags if re.match(r'Оценка:.', tag.text)]
        comment = re.split(r'Комментарии:', small_tags[1].text)
        if rate or len(comment) > 1:
            genre = False
            if len(comment) > 1:
                genre = comment[0]
            if rate:
                genre = genre if isinstance(genre, str) else rate[0]
                if rate:
                    genre = re.sub(r'Оценка:[0-9*,.]+', '', genre)
                book_genres = [gen.strip() for gen in genre.split(',')]
        else:
            book_genres = [genre.strip() for genre in small_tags[1].text.split(',')]
        books.append(Book(title, int(date), file_path, book_genres))

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
genreInserter = BooksAndGenres(map_of_genres())

db = operateWithDB()
print(len(authors_links))

for i in range(0, len(authors_links)):
    author_entity, books_entity = process_author_page(authors_links[i])
    db.execute_operations(author_entity.fill_table)
    boa = BooksOfAuthor(i + 1, books_entity)
    db.execute_operations(boa.fill_table)
    genreInserter.setBooks(books_entity)
    db.execute_operations(genreInserter.fill_table)
    print(f'{i + 1} of 3745')
db.close()








