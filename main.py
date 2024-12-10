import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
from admin import open_admin_window
from client import open_orders_history, open_menu_window
from waiter import open_waiter_window


# Авторизация пользователей
def authenticate_user(username, password):
    try:
        with sqlite3.connect("restaurant.db") as conn:
            cursor = conn.cursor()
            # Проверяем, существует ли пользователь
            cursor.execute("SELECT * FROM users WHERE login = ?", (username,))
            user = cursor.fetchone()
            if user:
                # Если пользователь найден, проверяем пароль
                if user[2] == password:  # предполагается, что пароль хранится в третьей колонке
                    role = user[3]  # роль хранится в четвертой колонке
                    if role == "admin":
                        messagebox.showinfo("Успех", f"Добро пожаловать, администратор!")
                        open_admin_window()
                    elif role == "waiter":
                        messagebox.showinfo("Успех", f"Добро пожаловать, официант!")
                        open_waiter_window()
                    elif role == "client":
                        messagebox.showinfo("Успех", f"Добро пожаловать, клиент!")
                        open_client_window(username)

                    else:
                        messagebox.showerror("Ошибка", "Неизвестная роль пользователя.")
                else:
                    messagebox.showerror("Ошибка", "Неверный пароль.")
            else:
                # Если пользователь не найден, регистрируем его как клиента
                cursor.execute(
                    "INSERT INTO users (login, password, role) VALUES (?, ?, ?)",
                    (username, password, "client")
                )
                conn.commit()
                messagebox.showinfo("Успех", "Регистрация прошла успешно! Вы вошли как клиент.")
                open_client_window(username)
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка", f"Ошибка базы данных: {e}")


# Функция для открытия окна клиента
def open_client_window(username):
    client_window = tk.Toplevel()
    client_window.title(f"Личный кабинет: {username}")
    client_window.geometry("400x300")

    tk.Label(client_window, text=f"Добро пожаловать, {username}!", font=("Arial", 14)).pack(pady=10)
    tk.Button(client_window, text="История заказов",
              command=lambda: open_orders_history(client_window, username)).pack(pady=10)
    tk.Button(client_window, text="Посмотреть меню", command=open_menu_window).pack(pady=10)
    tk.Button(client_window, text="Выйти", command=client_window.destroy).pack(pady=10)


# Главное окно (авторизация)
def create_main_window():
    root = tk.Tk()
    root.title("Авторизация")
    frame = tk.Frame(root)
    frame.pack(pady=50)

    username_label = tk.Label(frame, text="Логин")
    username_label.pack(pady=5)
    username_entry = tk.Entry(frame)
    username_entry.pack(pady=5)

    password_label = tk.Label(frame, text="Пароль")
    password_label.pack(pady=5)
    password_entry = tk.Entry(frame, show="*")
    password_entry.pack(pady=5)

    def on_login_button_click():
        username = username_entry.get()
        password = password_entry.get()
        if not username or not password:
            messagebox.showwarning("Ошибка", "Пожалуйста, заполните все поля!")
            return
        authenticate_user(username, password)

    login_button = tk.Button(frame, text="Войти", command=on_login_button_click)
    login_button.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    create_main_window()
