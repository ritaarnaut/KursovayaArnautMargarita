import sqlite3

# Создание базы данных и соединение
with sqlite3.connect("restaurant.db") as conn:
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('admin', 'waiter', 'client'))
        )
    """)

    # Таблица меню
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            price REAL NOT NULL CHECK (price > 0)
        )
    """)

    # Таблица заказов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_login TEXT NOT NULL,
            order_details TEXT NOT NULL,
            total_price REAL NOT NULL CHECK (total_price >= 0),
            status TEXT NOT NULL CHECK (status IN ('active', 'completed')),
            FOREIGN KEY (client_login) REFERENCES users (login) ON DELETE CASCADE
        )
    """)

    cursor.execute("""CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    client_login TEXT,
    rating INTEGER,
    review_text TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        """)
    # Добавление тестовых данных
    try:
        # Пользователи
        cursor.executemany("""
            INSERT INTO users (login, password, role) VALUES (?, ?, ?)
        """, [
            ('admin', 'admin123', 'admin'),
            ('waiter', 'waiter123', 'waiter'),
            ('client1', 'clientpass', 'client'),
        ])

        # Меню
        cursor.executemany("""
            INSERT INTO menu (name, description, price) VALUES (?, ?, ?)
        """, [
            ('Пицца', 'Большая сырная пицца', 10.99),
            ('Бургер', 'Сочный бургер с картошкой', 8.99),
            ('Салат', 'Свежий овощной салат', 5.99),
        ])

        # Заказы
        cursor.executemany("""
            INSERT INTO orders (client_login, order_details, total_price, status) VALUES (?, ?, ?, ?)
        """, [
            ('client1', 'Пицца, Салат', 16.98, 'completed'),
            ('client1', 'Бургер', 8.99, 'active'),
        ])

    except sqlite3.IntegrityError:
        # Игнорируем ошибки при повторной вставке данных
        pass

    print("База данных успешно создана и инициализирована.")
