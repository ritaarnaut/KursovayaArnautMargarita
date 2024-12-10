import tkinter as tk
from tkinter import messagebox
import sqlite3


def open_waiter_window():
    """Главное окно официанта."""
    waiter_win = tk.Toplevel()
    waiter_win.title("Окно официанта")
    waiter_win.geometry("400x400")

    tk.Button(waiter_win, text="Принять заказ", command=open_take_order_window).pack(pady=10)
    tk.Button(waiter_win, text="Заказы", command=open_orders_window).pack(pady=10)
    tk.Button(waiter_win, text="Выход", command=waiter_win.destroy).pack(pady=10)


def open_orders_window():
    """Окно списка заказов (бывшая история заказов)."""
    orders_win = tk.Toplevel()
    orders_win.title("Заказы")
    orders_win.geometry("400x400")

    orders_list = tk.Listbox(orders_win, width=50, height=20)
    orders_list.pack(pady=10)

    def load_orders():
        orders_list.delete(0, tk.END)
        try:
            with sqlite3.connect("restaurant.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, client_login, order_details, total_price, status FROM orders")
                orders = cursor.fetchall()
                if orders:
                    for order in orders:
                        orders_list.insert(
                            tk.END,
                            f"Заказ {order[0]} | Клиент: {order[1]} | Детали: {order[2]} | Сумма: {order[3]} руб. | Статус: {order[4]}"
                        )
                else:
                    orders_list.insert(tk.END, "Нет заказов")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки заказов: {e}")

    load_orders()

    def fulfill_order():
        """Функция для выполнения заказа (меняет статус на 'completed')."""
        selected = orders_list.curselection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите заказ для выполнения.")
            return
        selected_order = orders_list.get(selected[0])
        order_id = selected_order.split(" | ")[0].split()[1]

        try:
            with sqlite3.connect("restaurant.db") as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE orders SET status = 'completed' WHERE id = ?", (order_id,))
                conn.commit()
                messagebox.showinfo("Успех", "Заказ выполнен.")
                load_orders()  # Обновляем список заказов
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при выполнении заказа: {e}")

    fulfill_button = tk.Button(orders_win, text="Выдать заказ", command=fulfill_order)
    fulfill_button.pack(pady=10)

    back_button = tk.Button(orders_win, text="Назад", command=orders_win.destroy)
    back_button.pack(pady=10)


def open_take_order_window():
    """Окно для принятия заказа."""
    order_win = tk.Toplevel()
    order_win.title("Принять заказ")
    order_win.geometry("400x500")

    # Поле для поиска блюда
    tk.Label(order_win, text="Поиск блюда:").pack(pady=5)
    search_entry = tk.Entry(order_win, width=30)
    search_entry.pack(pady=5)

    # Список блюд
    menu_list = tk.Listbox(order_win, width=50, height=10)
    menu_list.pack(pady=10)

    def load_menu(search_query=None):
        """Загрузка меню."""
        menu_list.delete(0, tk.END)
        try:
            with sqlite3.connect("restaurant.db") as conn:
                cursor = conn.cursor()
                if search_query:
                    cursor.execute("SELECT name, price FROM menu WHERE name LIKE ?", (f"%{search_query}%",))
                else:
                    cursor.execute("SELECT name, price FROM menu")
                items = cursor.fetchall()
                if items:
                    for item in items:
                        menu_list.insert(tk.END, f"{item[0]} - {item[1]} руб.")
                else:
                    menu_list.insert(tk.END, "Нет доступных блюд.")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки меню: {e}")

    load_menu()

    def search_menu():
        """Обработчик поиска."""
        query = search_entry.get()
        load_menu(query)

    tk.Button(order_win, text="Найти", command=search_menu).pack(pady=5)

    # Поле для выбора количества порций
    tk.Label(order_win, text="Количество порций:").pack(pady=5)
    portion_entry = tk.Entry(order_win, width=10)
    portion_entry.pack(pady=5)

    # Поле для ввода логина клиента
    tk.Label(order_win, text="Введите логин клиента:").pack(pady=5)
    client_login_entry = tk.Entry(order_win, width=30)
    client_login_entry.pack(pady=5)

    def place_order():
        """Функция для принятия заказа."""
        selected = menu_list.curselection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите блюдо из меню.")
            return
        selected_item = menu_list.get(selected[0])
        dish_name = selected_item.split(" - ")[0]
        price = float(selected_item.split(" - ")[1].split()[0])
        portions = portion_entry.get()
        client_login = client_login_entry.get()

        if not portions.isdigit() or int(portions) <= 0:
            messagebox.showerror("Ошибка", "Введите корректное количество порций.")
            return
        if not client_login:
            messagebox.showerror("Ошибка", "Введите логин клиента.")
            return

        total_price = price * int(portions)
        try:
            with sqlite3.connect("restaurant.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO orders (client_login, order_details, total_price, status) VALUES (?, ?, ?, ?)",
                    (client_login, f"{dish_name} x{portions}", total_price, "active")
                )
                conn.commit()
                messagebox.showinfo("Успех", "Заказ успешно добавлен.")
                order_win.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении заказа: {e}")

    tk.Button(order_win, text="Принять заказ", command=place_order).pack(pady=10)
    tk.Button(order_win, text="Назад", command=order_win.destroy).pack(pady=10)


def open_waiter_main_window():
    """Окно для работы официанта"""
    waiter_main_win = tk.Toplevel()
    waiter_main_win.title("Окно официанта")
    waiter_main_win.geometry("400x400")

    tk.Button(waiter_main_win, text="Принять заказ", command=open_take_order_window).pack(pady=10)
    tk.Button(waiter_main_win, text="Заказы", command=open_orders_window).pack(pady=10)
    tk.Button(waiter_main_win, text="Выход", command=waiter_main_win.destroy).pack(pady=10)
