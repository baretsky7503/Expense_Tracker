import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Трекер расходов")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)

        # Файл для хранения расходов
        self.data_file = "expenses.json"
        self.expenses = self.load_expenses()

        # Категории расходов
        self.categories = ["Еда", "Транспорт", "Развлечения", "Коммунальные услуги",
                           "Здоровье", "Одежда", "Образование", "Другое"]

        # Сортировка расходов по дате (новые сверху)
        self.expenses.sort(key=lambda x: x['date'], reverse=True)

        # Создание интерфейса
        self.create_input_frame()
        self.create_table_frame()
        self.create_filter_frame()
        self.create_summary_frame()

        # Обновление таблицы
        self.refresh_table()

    def load_expenses(self):
        """Загрузка расходов из JSON-файла"""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_expenses(self):
        """Сохранение расходов в JSON-файл"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, indent=4, ensure_ascii=False)

    def create_input_frame(self):
        """Форма для добавления расхода"""
        input_frame = tk.LabelFrame(self.root, text="Добавление расхода", font=("Arial", 12, "bold"), padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Сумма
        tk.Label(input_frame, text="Сумма (₽):", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.amount_entry = tk.Entry(input_frame, width=15, font=("Arial", 10))
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        # Категория
        tk.Label(input_frame, text="Категория:", font=("Arial", 10)).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.category_combo = ttk.Combobox(input_frame, values=self.categories, width=18, state="readonly")
        self.category_combo.set("Выберите категорию")
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)

        # Дата
        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):", font=("Arial", 10)).grid(row=0, column=4, sticky="w", padx=5,
                                                                                  pady=5)
        self.date_entry = tk.Entry(input_frame, width=15, font=("Arial", 10))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)

        # Кнопка добавления
        self.add_btn = tk.Button(input_frame, text="➕ Добавить расход", command=self.add_expense,
                                 bg="#2c3e50", fg="white", font=("Arial", 10, "bold"))
        self.add_btn.grid(row=0, column=6, padx=20, pady=5)

    def create_table_frame(self):
        """Таблица для отображения расходов"""
        table_frame = tk.LabelFrame(self.root, text="Список расходов", font=("Arial", 12, "bold"), padx=10, pady=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Создание таблицы (Treeview)
        columns = ("ID", "Дата", "Категория", "Сумма (₽)")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        # Настройка заголовков
        self.tree.heading("ID", text="ID")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Сумма (₽)", text="Сумма (₽)")

        # Настройка ширины колонок
        self.tree.column("ID", width=50)
        self.tree.column("Дата", width=120)
        self.tree.column("Категория", width=150)
        self.tree.column("Сумма (₽)", width=100)

        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления
        btn_frame = tk.Frame(table_frame)
        btn_frame.pack(fill="x", pady=5)

        self.delete_btn = tk.Button(btn_frame, text="🗑 Удалить выбранный расход", command=self.delete_expense,
                                    bg="#e74c3c", fg="white", font=("Arial", 10))
        self.delete_btn.pack(side="left", padx=5)

        self.edit_btn = tk.Button(btn_frame, text="✏ Редактировать выбранный расход", command=self.edit_expense,
                                  bg="#f39c12", fg="white", font=("Arial", 10))
        self.edit_btn.pack(side="left", padx=5)

    def create_filter_frame(self):
        """Фрейм для фильтрации"""
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", font=("Arial", 12, "bold"), padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по категории
        tk.Label(filter_frame, text="Категория:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5)
        self.filter_category = ttk.Combobox(filter_frame, values=["Все"] + self.categories, width=18, state="readonly")
        self.filter_category.set("Все")
        self.filter_category.grid(row=0, column=1, padx=5, pady=5)

        # Фильтр по дате (диапазон)
        tk.Label(filter_frame, text="Дата с:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5)
        self.filter_date_from = tk.Entry(filter_frame, width=12, font=("Arial", 10))
        self.filter_date_from.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(filter_frame, text="по:", font=("Arial", 10)).grid(row=0, column=4, padx=5, pady=5)
        self.filter_date_to = tk.Entry(filter_frame, width=12, font=("Arial", 10))
        self.filter_date_to.grid(row=0, column=5, padx=5, pady=5)

        # Кнопки фильтрации
        self.apply_filter_btn = tk.Button(filter_frame, text="🔍 Применить фильтр", command=self.apply_filter,
                                          bg="#3498db", fg="white", font=("Arial", 9))
        self.apply_filter_btn.grid(row=0, column=6, padx=5, pady=5)

        self.reset_filter_btn = tk.Button(filter_frame, text="🔄 Сбросить", command=self.reset_filter,
                                          bg="#95a5a6", fg="white", font=("Arial", 9))
        self.reset_filter_btn.grid(row=0, column=7, padx=5, pady=5)

    def create_summary_frame(self):
        """Фрейм для отображения суммы расходов за период"""
        summary_frame = tk.LabelFrame(self.root, text="Статистика", font=("Arial", 12, "bold"), padx=10, pady=10)
        summary_frame.pack(fill="x", padx=10, pady=5)

        self.summary_label = tk.Label(summary_frame, text="Общая сумма расходов за выбранный период: 0.00 ₽",
                                      font=("Arial", 12, "bold"), fg="#2c3e50")
        self.summary_label.pack(pady=10)

        # Кнопка быстрого выбора периода
        period_frame = tk.Frame(summary_frame)
        period_frame.pack(pady=5)

        tk.Button(period_frame, text="Сегодня", command=self.set_today_period,
                  bg="#ecf0f1", font=("Arial", 9)).pack(side="left", padx=5)
        tk.Button(period_frame, text="Эта неделя", command=self.set_week_period,
                  bg="#ecf0f1", font=("Arial", 9)).pack(side="left", padx=5)
        tk.Button(period_frame, text="Этот месяц", command=self.set_month_period,
                  bg="#ecf0f1", font=("Arial", 9)).pack(side="left", padx=5)
        tk.Button(period_frame, text="Все время", command=self.set_all_period,
                  bg="#ecf0f1", font=("Arial", 9)).pack(side="left", padx=5)

    def validate_expense_data(self, amount, category, date):
        """Проверка корректности ввода"""
        # Проверка суммы
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть числом!")
            return False

        # Проверка категории
        if category not in self.categories:
            messagebox.showerror("Ошибка", "Выберите категорию из списка!")
            return False

        # Проверка даты
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return False

        return True

    def add_expense(self):
        """Добавление расхода"""
        amount = self.amount_entry.get().strip()
        category = self.category_combo.get()
        date = self.date_entry.get().strip()

        if not self.validate_expense_data(amount, category, date):
            return

        expense = {
            "id": len(self.expenses) + 1,
            "amount": float(amount),
            "category": category,
            "date": date
        }

        self.expenses.append(expense)
        self.expenses.sort(key=lambda x: x['date'], reverse=True)
        self.save_expenses()
        self.refresh_table()
        self.apply_filter()  # Обновить фильтр и сумму

        # Очистка полей
        self.amount_entry.delete(0, tk.END)
        self.category_combo.set("Выберите категорию")
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        messagebox.showinfo("Успех", f"Расход {amount} ₽ добавлен!")

    def delete_expense(self):
        """Удаление выбранного расхода"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите расход для удаления!")
            return

        item = self.tree.item(selected[0])
        expense_id = int(item['values'][0])

        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", "Удалить выбранный расход?"):
            self.expenses = [e for e in self.expenses if e['id'] != expense_id]
            # Обновить ID
            for i, exp in enumerate(self.expenses):
                exp['id'] = i + 1
            self.save_expenses()
            self.refresh_table()
            self.apply_filter()
            messagebox.showinfo("Успех", "Расход удалён!")

    def edit_expense(self):
        """Редактирование выбранного расхода"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите расход для редактирования!")
            return

        item = self.tree.item(selected[0])
        expense_id = int(item['values'][0])
        expense = next(e for e in self.expenses if e['id'] == expense_id)

        # Создание окна редактирования
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактирование расхода")
        edit_window.geometry("400x250")
        edit_window.resizable(False, False)

        tk.Label(edit_window, text="Сумма (₽):", font=("Arial", 10)).pack(pady=5)
        amount_entry = tk.Entry(edit_window, font=("Arial", 10))
        amount_entry.insert(0, str(expense['amount']))
        amount_entry.pack(pady=5)

        tk.Label(edit_window, text="Категория:", font=("Arial", 10)).pack(pady=5)
        category_combo = ttk.Combobox(edit_window, values=self.categories, state="readonly")
        category_combo.set(expense['category'])
        category_combo.pack(pady=5)

        tk.Label(edit_window, text="Дата (ГГГГ-ММ-ДД):", font=("Arial", 10)).pack(pady=5)
        date_entry = tk.Entry(edit_window, font=("Arial", 10))
        date_entry.insert(0, expense['date'])
        date_entry.pack(pady=5)

        def save_edit():
            new_amount = amount_entry.get().strip()
            new_category = category_combo.get()
            new_date = date_entry.get().strip()

            # Валидация
            try:
                new_amount_float = float(new_amount)
                if new_amount_float <= 0:
                    messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                    return
            except ValueError:
                messagebox.showerror("Ошибка", "Сумма должна быть числом!")
                return

            if new_category not in self.categories:
                messagebox.showerror("Ошибка", "Выберите категорию!")
                return

            try:
                datetime.strptime(new_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты!")
                return

            # Сохранение изменений
            expense['amount'] = new_amount_float
            expense['category'] = new_category
            expense['date'] = new_date

            self.expenses.sort(key=lambda x: x['date'], reverse=True)
            self.save_expenses()
            self.refresh_table()
            self.apply_filter()
            edit_window.destroy()
            messagebox.showinfo("Успех", "Расход обновлён!")

        tk.Button(edit_window, text="Сохранить", command=save_edit,
                  bg="#27ae60", fg="white", font=("Arial", 10)).pack(pady=10)

    def apply_filter(self):
        """Применение фильтров"""
        category_filter = self.filter_category.get()
        date_from = self.filter_date_from.get().strip()
        date_to = self.filter_date_to.get().strip()

        filtered = self.expenses.copy()

        # Фильтр по категории
        if category_filter != "Все":
            filtered = [e for e in filtered if e['category'] == category_filter]

        # Фильтр по дате
        if date_from:
            try:
                datetime.strptime(date_from, "%Y-%m-%d")
                filtered = [e for e in filtered if e['date'] >= date_from]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты 'с'!")
                return

        if date_to:
            try:
                datetime.strptime(date_to, "%Y-%m-%d")
                filtered = [e for e in filtered if e['date'] <= date_to]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты 'по'!")
                return

        self.display_expenses(filtered)
        self.update_summary(filtered)

    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_category.set("Все")
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_to.delete(0, tk.END)
        self.display_expenses(self.expenses)
        self.update_summary(self.expenses)

    def refresh_table(self):
        """Обновление таблицы (без фильтров)"""
        self.display_expenses(self.expenses)
        self.update_summary(self.expenses)

    def display_expenses(self, expenses_list):
        """Отображение расходов в таблице"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Добавление расходов
        for expense in expenses_list:
            self.tree.insert("", "end", values=(
                expense['id'],
                expense['date'],
                expense['category'],
                f"{expense['amount']:.2f}"
            ))

    def update_summary(self, expenses_list):
        """Обновление отображения общей суммы"""
        total = sum(e['amount'] for e in expenses_list)
        self.summary_label.config(text=f"Общая сумма расходов за выбранный период: {total:.2f} ₽")

    def set_today_period(self):
        """Установить период: сегодня"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_from.insert(0, today)
        self.filter_date_to.delete(0, tk.END)
        self.filter_date_to.insert(0, today)
        self.apply_filter()

    def set_week_period(self):
        """Установить период: текущая неделя"""
        today = datetime.now()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_from.insert(0, start_of_week.strftime("%Y-%m-%d"))
        self.filter_date_to.delete(0, tk.END)
        self.filter_date_to.insert(0, today.strftime("%Y-%m-%d"))
        self.apply_filter()

    def set_month_period(self):
        """Установить период: текущий месяц"""
        today = datetime.now()
        start_of_month = today.replace(day=1)
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_from.insert(0, start_of_month.strftime("%Y-%m-%d"))
        self.filter_date_to.delete(0, tk.END)
        self.filter_date_to.insert(0, today.strftime("%Y-%m-%d"))
        self.apply_filter()

    def set_all_period(self):
        """Установить период: всё время"""
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_to.delete(0, tk.END)
        self.apply_filter()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()