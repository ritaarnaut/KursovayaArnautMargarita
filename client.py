import sqlite3
from tkinter import messagebox, ttk
import tkinter as tk

def open_personal_data_window(username):
    personal_data_window = tk.Toplevel()
    personal_data_window.title("Личные данные")
    personal_data_window.geometry("400x400")

    # Заголовок
    tk.Label(personal_data_window, text="Заполните личные данные", font=("Arial", 14)).pack(pady=10)

    # Поля для ввода данных
    tk.Label(personal_data_window, text="Имя:").pack(pady=5)
    first_name_entry = tk.Entry(personal_data_window, width=30)
    first_name_entry.pack(pady=5)

    tk.Label(personal_data_window, text="Фамилия:").pack(pady=5)
    last_name_entry = tk.Entry(personal_data_window, width=30)
    last_name_entry.pack(pady=5)

    tk.Label(personal_data_window, text="Телефон:").pack(pady=5)
    phone_entry = tk.Entry(personal_data_window, width=30)
    phone_entry.pack(pady=5)

    tk.Label(personal_data_window, text="Дата рождения:").pack(pady=5)
    birth_date_entry = tk.Entry(personal_data_window, width=30)
    birth_date_entry.pack(pady=5)

    tk.Label(personal_data_window, text="Электронная почта:").pack(pady=5)
    email_entry = tk.Entry(personal_data_window, width=30)
    email_entry.pack(pady=5)

    # Функция для загрузки данных
    def load_personal_data():
        """Загрузка личных данных из базы."""
        try:
            with sqlite3.connect("restaurant.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT first_name, last_name, phone, birth_date, email
                    FROM users
                    WHERE login = ?
                """, (username,))
                data = cursor.fetchone()
                if data:
                    first_name_entry.insert(0, data[0])
                    last_name_entry.insert(0, data[1])
                    phone_entry.insert(0, data[2])
                    birth_date_entry.insert(0, data[3])
                    email_entry.insert(0, data[4])
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки данных: {e}")

    # Загружаем данные при открытии окна
    load_personal_data()

    # Кнопка сохранения данных
    def save_personal_data():
        first_name = first_name_entry.get()
        last_name = last_name_entry.get()
        phone = phone_entry.get()
        birth_date = birth_date_entry.get()
        email = email_entry.get()

        if not first_name or not last_name or not phone or not birth_date or not email:
            messagebox.showwarning("Ошибка", "Пожалуйста, заполните все поля!")
            return

        try:
            with sqlite3.connect("restaurant.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users
                    SET first_name = ?, last_name = ?, phone = ?, birth_date = ?, email = ?
                    WHERE login = ?
                """, (first_name, last_name, phone, birth_date, email, username))
                conn.commit()
            messagebox.showinfo("Успех", "Личные данные успешно обновлены.")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка обновления данных: {e}")

    save_button = tk.Button(personal_data_window, text="Сохранить данные", command=save_personal_data)
    save_button.pack(pady=10)

    # Кнопка назад
    back_button = tk.Button(personal_data_window, text="Назад", command=personal_data_window.destroy)
    back_button.pack(pady=10)


def open_orders_history(parent_window, username):
    history_window = tk.Toplevel(parent_window)
    history_window.title("История заказов")
    history_window.geometry("500x500")

    # Заголовок
    tk.Label(history_window, text=f"История заказов: {username}", font=("Arial", 14)).pack(pady=10)

    # Список заказов
    orders_list = tk.Listbox(history_window, width=70, height=20)
    orders_list.pack(pady=10)

    # Загрузка истории заказов
    try:
        with sqlite3.connect("restaurant.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, order_details, total_price, status
                FROM orders
                WHERE client_login = ?
            """, (username,))
            orders = cursor.fetchall()

            if orders:
                for order in orders:
                    # Отображаем заказ с деталями
                    order_id, order_details, total_price, status = order
                    orders_list.insert(
                        tk.END,
                        f"№{order_id} | {order_details} - {total_price} руб. | Статус: {status}"
                    )

                    # Выводим детали заказа
                    cursor.execute("""
                        SELECT dish_name, quantity FROM order_items
                        WHERE order_id = ?
                    """, (order_id,))
                    items = cursor.fetchall()

                    for item in items:
                        dish_name, quantity = item
                        orders_list.insert(tk.END, f"  {dish_name} x{quantity}")

            else:
                orders_list.insert(tk.END, "Заказы отсутствуют.")
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка", f"Ошибка загрузки истории заказов: {e}")

    # Кнопка назад
    back_button = tk.Button(history_window, text="Назад", command=history_window.destroy)
    back_button.pack(pady=10)


def open_menu_window():
    menu_window = tk.Toplevel()
    menu_window.title("Меню")
    menu_window.geometry("400x400")

    # Заголовок
    tk.Label(menu_window, text="Меню", font=("Arial", 14)).pack(pady=10)

    # Поле для поиска блюда
    tk.Label(menu_window, text="Поиск по меню:").pack(pady=5)
    search_entry = tk.Entry(menu_window, width=30)
    search_entry.pack(pady=5)

    def search_menu():
        search_query = search_entry.get().strip()
        if search_query:
            # Фильтруем блюда по поисковому запросу
            try:
                with sqlite3.connect("restaurant.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT dish_name, description, price FROM menu
                        WHERE dish_name LIKE ?
                    """, (f"%{search_query}%",))
                    dishes = cursor.fetchall()

                    # Очищаем текущий список
                    for widget in dish_list_frame.winfo_children():
                        widget.destroy()

                    if dishes:
                        # Отображаем найденные блюда
                        for dish in dishes:
                            dish_name, description, price = dish
                            tk.Label(dish_list_frame, text=f"{dish_name} - {description} - {price} руб.", anchor="w", width=40).pack(pady=2)
                    else:
                        messagebox.showinfo("Результат", "Блюда не найдены.")

            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Ошибка базы данных: {e}")
        else:
            # Если запрос пустой, показываем все блюда
            show_all_dishes()

    # Кнопка поиска
    search_button = tk.Button(menu_window, text="Найти", command=search_menu)
    search_button.pack(pady=10)

    # Список блюд
    dish_list_frame = tk.Frame(menu_window)
    dish_list_frame.pack(pady=10)

    def show_all_dishes():
        # Загружаем все блюда из базы данных
        try:
            with sqlite3.connect("restaurant.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT dish_name, description, price FROM menu")
                dishes = cursor.fetchall()

                # Очищаем текущий список
                for widget in dish_list_frame.winfo_children():
                    widget.destroy()

                # Отображаем все блюда
                for dish in dishes:
                    dish_name, description, price = dish
                    tk.Label(dish_list_frame, text=f"{dish_name} - {description} - {price} руб.", anchor="w", width=40).pack(pady=2)

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка базы данных: {e}")

    # Показываем все блюда при открытии окна
    show_all_dishes()

    # Кнопка назад
    back_button = tk.Button(menu_window, text="Назад", command=menu_window.destroy)
    back_button.pack(pady=10)

def open_write_review_window(username):
    review_window = tk.Toplevel()
    review_window.title("Написать отзыв")
    review_window.geometry("400x400")

    # Заголовок
    tk.Label(review_window, text="Оставьте свой отзыв", font=("Arial", 14)).pack(pady=10)

    # Выбор заказа
    tk.Label(review_window, text="Выберите заказ:").pack(pady=5)
    order_combobox = ttk.Combobox(review_window, state="readonly", width=30)
    order_combobox.pack(pady=5)

    # Получаем список заказов пользователя
    try:
        with sqlite3.connect("restaurant.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT order_id, order_date FROM orders
                WHERE user_login = ?
                ORDER BY order_date DESC
            """, (username,))
            orders = cursor.fetchall()

            if orders:
                # Добавляем заказы в выпадающий список
                order_combobox['values'] = [f"№{order[0]} - {order[1]}" for order in orders]
            else:
                messagebox.showwarning("Ошибка", "У вас нет заказов.")
                return

    except sqlite3.Error as e:
        messagebox.showerror("Ошибка", f"Ошибка базы данных: {e}")

    # Поле для ввода оценки
    tk.Label(review_window, text="Оценка (1-5):").pack(pady=5)
    rating_entry = tk.Entry(review_window, width=10)
    rating_entry.pack(pady=5)

    # Поле для ввода текста отзыва
    tk.Label(review_window, text="Ваш отзыв:").pack(pady=5)
    review_text = tk.Text(review_window, width=30, height=10)
    review_text.pack(pady=10)

    def save_review():
        # Получаем выбранный заказ
        selected_order = order_combobox.get()
        if not selected_order:
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите заказ.")
            return

        # Получаем номер заказа из строки
        order_id = selected_order.split(" - ")[0][1:]

        # Получаем оценку
        try:
            rating = int(rating_entry.get())
            if rating < 1 or rating > 5:
                messagebox.showwarning("Ошибка", "Оценка должна быть от 1 до 5.")
                return
        except ValueError:
            messagebox.showwarning("Ошибка", "Пожалуйста, введите корректную оценку.")
            return

        # Получаем текст отзыва
        review = review_text.get("1.0", tk.END).strip()
        if not review:
            messagebox.showwarning("Ошибка", "Пожалуйста, напишите отзыв!")
            return

        try:
            # Сохраняем отзыв в базу данных
            with sqlite3.connect("restaurant.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO reviews (user_login, order_id, rating, review_text)
                    VALUES (?, ?, ?, ?)
                """, (username, order_id, rating, review))
                conn.commit()

            messagebox.showinfo("Успех", "Отзыв успешно оставлен!")
            review_window.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка базы данных: {e}")

    # Кнопка сохранить отзыв
    save_button = tk.Button(review_window, text="Сохранить отзыв", command=save_review)
    save_button.pack(pady=10)

    # Кнопка назад
    back_button = tk.Button(review_window, text="Назад", command=review_window.destroy)
    back_button.pack(pady=10)

