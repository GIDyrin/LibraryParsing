import psycopg2

def connect_to_db(what_to_execute):
    # Укажите параметры подключения
    conn = psycopg2.connect(
        dbname='library',
        user='postgres',
        password='admin',
        host='localhost',  # адрес сервера (можно указать IP)
        port='5432'        # стандартный порт PostgreSQL
    )

    # Создание курсора для выполнения запросов
    cur = conn.cursor()
    try:
        what_to_execute(cur)
        conn.commit()
    except Exception as e:
        print("Произошла ошибка:", e)
        conn.rollback()

    conn.close()
    conn.close()