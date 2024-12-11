import sqlite3
from tkinter import messagebox
import tkinter as tk  # исправленный импорт

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


# Пустые функции для примера
def open_orders_history():
    return None

def open_menu_window():
    return None

def open_write_review_window():
    return None
