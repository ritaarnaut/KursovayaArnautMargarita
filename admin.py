import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3


# Окно меню
def open_menu_window():
    menu_window = tk.Toplevel()
    menu_window.title("Меню")
    menu_window.geometry("500x500")

    # Поиск по меню
    search_frame = tk.Frame(menu_window)
    search_frame.pack(pady=10)

    search_label = tk.Label(search_frame, text="Поиск:")
    search_label.pack(side=tk.LEFT, padx=5)

    search_entry = tk.Entry(search_frame)
    search_entry.pack(side=tk.LEFT, padx=5)

    def search_menu():
        query = search_entry.get().strip()
        if query:
            load_menu(query)
        else:
            load_menu()

    search_button = tk.Button(search_frame, text="Найти", command=search_menu)
    search_button.pack(side=tk.LEFT, padx=5)

    # Список меню
    menu_list = tk.Listbox(menu_window, width=70, height=20)
    menu_list.pack(pady=10)

    # Загрузка меню из базы данных
    def load_menu(search_query=None):
        menu_list.delete(0, tk.END)
        try:
            with sqlite3.connect("restaurant.db") as conn:
                cursor = conn.cursor()
                if search_query:
                    cursor.execute("SELECT id, name, price FROM menu WHERE name LIKE ?", (f"%{search_query}%",))
                else:
                    cursor.execute("SELECT id, name, price FROM menu")
                items = cursor.fetchall()
                if items:
                    for item in items:
                        menu_list.insert(tk.END, f"{item[0]} | {item[1]} - {item[2]} руб.")
                else:
                    menu_list.insert(tk.END, "Меню пусто")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки меню: {e}")

    load_menu()

    # Удаление выбранного блюда
    def delete_item():
        selected = menu_list.curselection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите блюдо для удаления")
            return
        item = menu_list.get(selected[0])
        item_id = item.split(" | ")[0]

        try:
            with sqlite3.connect("restaurant.db") as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM menu WHERE id=?", (item_id,))
                conn.commit()
                messagebox.showinfo("Успех", "Блюдо удалено")
                load_menu()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении блюда: {e}")

    delete_button = tk.Button(menu_window, text="Удалить блюдо", command=delete_item)
    delete_button.pack(pady=5)

    # Добавление нового блюда
    def open_add_item_window(add_window=None):
        add_window = tk.Toplevel()
        add_window.title("Добавить блюдо")
        add_window.geometry("300x300")

        tk.Label(add_window, text="Название блюда").pack(pady=5)
        name_entry = tk.Entry(add_window)
        name_entry.pack(pady=5)

        tk.Label(add_window, text="Описание блюда").pack(pady=5)
        description_entry = tk.Text(add_window, height=5, width=30)
        description_entry.pack(pady=5)

        tk.Label(add_window, text="Цена").pack(pady=5)
        price_entry = tk.Entry(add_window)
        price_entry.pack(pady=5)

        def add_item():
            name = name_entry.get()
            description = description_entry.get("1.0", tk.END).strip()
            price = price_entry.get()
            if not name or not price:
                messagebox.showwarning("Ошибка", "Заполните все поля")
                return
            try:
                price = float(price)
                with sqlite3.connect("restaurant.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO menu (name, description, price) VALUES (?, ?, ?)",
                                   (name, description, price))
                    conn.commit()
                    messagebox.showinfo("Успех", "Блюдо добавлено")
                    add_window.destroy()
                    load_menu()
            except ValueError:
                messagebox.showerror("Ошибка", "Цена должна быть числом")
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Ошибка при добавлении блюда: {e}")

        tk.Button(add_window, text="Добавить", command=add_item).pack(pady=10)

    add_button = tk.Button(menu_window, text="Добавить блюдо", command=open_add_item_window)
    add_button.pack(pady=5)

    # Кнопка назад
    back_button = tk.Button(menu_window, text="Назад", command=menu_window.destroy)
    back_button.pack(pady=10)


# Скачивание отчета
def download_report():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt")])
    if file_path:
        try:
            with sqlite3.connect("restaurant.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, order_details, total_price FROM orders")
                orders = cursor.fetchall()
                with open(file_path, 'w') as report_file:
                    report_file.write("Отчет о заказах:\n")
                    for order in orders:
                        report_file.write(f"Заказ {order[0]} | {order[1]} - {order[2]} руб.\n")
                messagebox.showinfo("Успех", f"Отчет сохранен: {file_path}")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании отчета: {e}")


# Главное окно администратора
def open_admin_window():
    admin_window = tk.Toplevel()
    admin_window.title("Окно администратора")
    admin_window.geometry("400x400")

    tk.Label(admin_window, text="Добро пожаловать, Администратор!", font=("Arial", 14)).pack(pady=10)

    menu_button = tk.Button(admin_window, text="Меню", command=open_menu_window)
    menu_button.pack(pady=10)

    tk.Button(admin_window, text="Пользователи", command=open_users_window).pack(pady=10)

    report_button = tk.Button(admin_window, text="Скачать отчет", command=download_report)
    report_button.pack(pady=10)

    tk.Button(admin_window, text="Посмотреть отзывы", command=open_reviews_window).pack(pady=10)

    back_button = tk.Button(admin_window, text="Выйти", command=admin_window.destroy)
    back_button.pack(pady=10)


def open_reviews_window():
    """Окно для отображения всех отзывов."""
    reviews_win = tk.Toplevel()
    reviews_win.title("Отзывы")
    reviews_win.geometry("500x500")

    # Список отзывов
    reviews_list = tk.Listbox(reviews_win, width=70, height=20)
    reviews_list.pack(pady=10)

    try:
        with sqlite3.connect("restaurant.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.id, o.order_details, r.rating, r.review_text, r.client_login
                FROM reviews r
                JOIN orders o ON r.order_id = o.id
            """)
            reviews = cursor.fetchall()
            if reviews:
                for review in reviews:
                    reviews_list.insert(
                        tk.END,
                        f"Отзыв №{review[0]} | Заказ: {review[1]} | Оценка: {review[2]} | Отзыв: {review[3]} | Клиент: {review[4]}"
                    )
            else:
                reviews_list.insert(tk.END, "Нет отзывов.")
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка", f"Ошибка загрузки отзывов: {e}")

    back_button = tk.Button(reviews_win, text="Назад", command=reviews_win.destroy)
    back_button.pack(pady=10)

def open_users_window():
    users_window = tk.Toplevel()
    users_window.title("Пользователи")
    users_window.geometry("600x500")

    # Заголовок
    tk.Label(users_window, text="Список пользователей", font=("Arial", 14)).pack(pady=10)

    # Список пользователей
    users_list = tk.Listbox(users_window, width=80, height=15)
    users_list.pack(pady=10)

    # Загрузка пользователей
    def load_users():
        users_list.delete(0, tk.END)
        try:
            with sqlite3.connect("restaurant.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT login, first_name, last_name, phone, birth_date, email FROM users WHERE role = 'client'
                """)
                users = cursor.fetchall()
                if users:
                    for user in users:
                        users_list.insert(
                            tk.END,
                            f"Логин: {user[0]} | Имя: {user[1]} | Фамилия: {user[2]} | Телефон: {user[3]} | Дата рождения: {user[4]} | Почта: {user[5]}"
                        )
                else:
                    users_list.insert(tk.END, "Нет пользователей.")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки пользователей: {e}")

    # Обновляем список пользователей при загрузке
    load_users()

    # Кнопка назад
    back_button = tk.Button(users_window, text="Назад", command=users_window.destroy)
    back_button.pack(pady=10)