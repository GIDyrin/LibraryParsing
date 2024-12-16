import psycopg2

class operateWithDB:
    def __init__(self):
        conn = psycopg2.connect(
            dbname='library',
            user='postgres',
            password='admin',
            host='localhost',
            port='5432'  # стандартный порт PostgreSQL
        )

        self.conn = conn


    def execute_operations(self, what_to_execute):
        # Создание курсора для выполнения запросов
        cur = self.conn.cursor()
        try:
            what_to_execute(cur)
            self.conn.commit()
        except Exception as e:
            print("Произошла ошибка:", e)
            self.conn.rollback()

        cur.close()


    def close(self):
        self.conn.close()
