class Author:
    def __init__(self, name: str, bio: str, img_path: str):
        self.name = name
        self.bio = bio
        self.img_path = img_path

    def fill_table(self, cursor):
        bio = None if not self.bio else self.bio
        path = None if not self.img_path else self.img_path
        cursor.execute('INSERT INTO authors(author_name, biography, user_id, image_path) VALUES(%s, %s, NULL, %s);', (self.name, bio, path,) )


class Book:
    def __init__(self, title: str, year: int, path: str, genresList: list[str]):
        self.title = title
        self.year = None if not year else year
        self.path = None if not path else path
        self.genres = genresList


class BooksOfAuthor:
    def __init__(self, auid: int, books: list[Book]):
        self.auid = auid
        self.books = books


    def fill_table(self, cursor):
        if len(self.books) > 0:
            for book in self.books:
                if not book.path:
                    continue
                cursor.execute('INSERT INTO books(book_title, book_year, description, author_id, book_path)'
                           ' VALUES(%s, %s, NULL, %s, %s);', (book.title, book.year, self.auid, book.path,) )



class BooksAndGenres:
    def __init__(self, genres):
        self.genres = genres
        self.lastid = 1


    def setBooks(self, books: list[Book]):
        self.books = books


    def fill_table(self, cursor):
        for book in self.books:
            for genre in book.genres:
                cursor.execute('INSERT INTO book_genres(book_id, genre_id) VALUES(%s, %s)', (self.lastid, self.genres[genre],))
            self.lastid += 1

