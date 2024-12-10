import tkinter as tk
from tkinter import messagebox
import sqlite3


# Окно меню для клиента
def open_menu_window():
    menu_win = tk.Toplevel()
    menu_win.title("Меню")
    menu_win.geometry("500x500")

    # Поле для поиска
    tk.Label(menu_win, text="Поиск блюда:").pack(pady=5)
    search_entry = tk.Entry(menu_win, width=30)
    search_entry.pack(pady=5)

    # Список меню
    menu_list = tk.Listbox(menu_win, width=70, height=15)
    menu_list.pack(pady=10)

    # Поле для отображения описания
    description_label = tk.Label(menu_win, text="Описание:", anchor="w", justify="left", wraplength=400)
    description_label.pack(pady=5)

    # Загрузка меню
    def load_menu(search_query=None):
        menu_list.delete(0, tk.END)
        try:
            with sqlite3.connect("restaurant.db") as conn:
                cursor = conn.cursor()
                if search_query:
                    cursor.execute(
                        "SELECT name, description, price FROM menu WHERE name LIKE ?", (f"%{search_query}%",)
                    )
                else:
                    cursor.execute("SELECT name, description, price FROM menu")
                items = cursor.fetchall()
                if items:
                    for item in items:
                        menu_list.insert(tk.END, f"{item[0]} - {item[2]} руб.")
                else:
                    menu_list.insert(tk.END, "Нет доступных блюд.")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки меню: {e}")

    # Обновляем меню при загрузке
    load_menu()

    # Поиск
    def search_menu():
        query = search_entry.get()
        load_menu(query)

    search_button = tk.Button(menu_win, text="Найти", command=search_menu)
    search_button.pack(pady=5)

    # Отображение описания блюда при выборе
    def show_description(event):
        selected = menu_list.curselection()
        if not selected:
            description_label.config(text="Описание: ")
            return
        item = menu_list.get(selected[0])
        item_name = item.split(" - ")[0]
        try:
            with sqlite3.connect("restaurant.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT description FROM menu WHERE name=?", (item_name,))
                description = cursor.fetchone()
                description_label.config(text=f"Описание: {description[0]}" if description and description[0] else "Описание отсутствует.")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки описания: {e}")

    menu_list.bind("<<ListboxSelect>>", show_description)

    # Кнопка назад
    back_button = tk.Button(menu_win, text="Назад", command=menu_win.destroy)
    back_button.pack(pady=10)


def open_orders_history(parent_window, username):
    history_window = tk.Toplevel(parent_window)
    history_window.title("История заказов")
    history_window.geometry("400x400")

    # Заголовок
    tk.Label(history_window, text=f"История заказов: {username}", font=("Arial", 14)).pack(pady=10)

    # Список заказов
    orders_list = tk.Listbox(history_window, width=50, height=20)
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
                    orders_list.insert(
                        tk.END,
                        f"№{order[0]} | {order[1]} - {order[2]} руб. | {order[3]}"
                    )
            else:
                orders_list.insert(tk.END, "Заказы отсутствуют.")
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка", f"Ошибка загрузки истории заказов: {e}")

    # Кнопка назад
    back_button = tk.Button(history_window, text="Назад", command=history_window.destroy)
    back_button.pack(pady=10)

def open_write_review_window(username):
    """Окно для написания отзыва клиентом."""
    review_win = tk.Toplevel()
    review_win.title("Написать отзыв")
    review_win.geometry("400x500")

    # Список заказов клиента
    orders_list = tk.Listbox(review_win, width=50, height=10)
    orders_list.pack(pady=10)

    def load_orders():
        """Загрузка заказов клиента."""
        orders_list.delete(0, tk.END)
        try:
            with sqlite3.connect("restaurant.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, order_details, total_price FROM orders WHERE client_login = ? AND status = 'completed'", (username,))
                orders = cursor.fetchall()
                if orders:
                    for order in orders:
                        orders_list.insert(
                            tk.END,
                            f"Заказ {order[0]} | Детали: {order[1]} | Сумма: {order[2]} руб."
                        )
                else:
                    orders_list.insert(tk.END, "Нет завершенных заказов для отзыва.")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки заказов: {e}")

    load_orders()

    # Поле для оценки от 1 до 5
    tk.Label(review_win, text="Оцените заказ (1-5):").pack(pady=5)
    rating_entry = tk.Entry(review_win, width=10)
    rating_entry.pack(pady=5)

    # Поле для ввода отзыва
    tk.Label(review_win, text="Ваш отзыв:").pack(pady=5)
    review_text = tk.Text(review_win, width=40, height=5)
    review_text.pack(pady=5)

    def submit_review():
        """Функция для отправки отзыва."""
        selected = orders_list.curselection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите заказ для отзыва.")
            return

        order_id = orders_list.get(selected[0]).split(" | ")[0].split()[1]
        rating = rating_entry.get()
        review = review_text.get("1.0", tk.END).strip()

        if not rating.isdigit() or not (1 <= int(rating) <= 5):
            messagebox.showerror("Ошибка", "Введите корректную оценку (от 1 до 5).")
            return
        if not review:
            messagebox.showerror("Ошибка", "Введите отзыв.")
            return

        try:
            with sqlite3.connect("restaurant.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO reviews (order_id, client_login, rating, review_text) VALUES (?, ?, ?, ?)",
                    (order_id, username, rating, review)
                )
                conn.commit()
                messagebox.showinfo("Успех", "Отзыв успешно отправлен.")
                review_win.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при отправке отзыва: {e}")

    submit_button = tk.Button(review_win, text="Отправить отзыв", command=submit_review)
    submit_button.pack(pady=10)

    back_button = tk.Button(review_win, text="Назад", command=review_win.destroy)
    back_button.pack(pady=10)

