import tkinter as tk
from model import BookModel
from view import MainView

class MainController:
    def __init__(self, root):
        self.model = BookModel()
        # Передаём функции-события в нужном порядке: добавить, удалить, выдать, вернуть, зарезервировать книгу.
        self.view = MainView(
            root,
            self.add_book,
            self.open_delete_window,
            self.open_issue_window,
            self.open_return_window,
            self.open_reserve_window
        )
        self.load_books()

    def load_books(self):
        self.view.book_list.delete(0, tk.END)
        books = self.model.get_books()
        for book in books:
            # Отображаем также статус книги и, если имеется, имя, на которое зарезервирована книга
            reserved_info = f", зарезервирована на: {book['reserved_by']}" if book.get('reserved_by') else ""
            item_text = f"{book['title']} — {book['author']} (ID: {book['id']}, статус: {book.get('status', 'неизвестно')}{reserved_info})"
            self.view.book_list.insert(tk.END, item_text)

    def add_book(self):
        title = self.view.title_input.get().strip()
        author = self.view.author_input.get().strip()
        if title and author:
            result = self.model.add_book(title, author)
            if result:
                self.load_books()
                self.view.title_input.delete(0, tk.END)
                self.view.author_input.delete(0, tk.END)

    def open_delete_window(self):
        delete_window = tk.Toplevel()
        delete_window.title("Удалить книгу")
        delete_window.geometry("300x150")
        tk.Label(delete_window, text="Введите ID книги для удаления:").pack(pady=5)
        id_entry = tk.Entry(delete_window)
        id_entry.pack(pady=5)
        tk.Button(delete_window, text="Удалить", 
                  command=lambda: self.confirm_delete(id_entry, delete_window)).pack(pady=5)

    def confirm_delete(self, id_entry, window):
        book_id = id_entry.get().strip()
        if book_id:
            if self.model.delete_book_by_id(book_id):
                self.load_books()
            else:
                print("Ошибка: не удалось удалить книгу")
        window.destroy()

    def open_issue_window(self):
        issue_window = tk.Toplevel()
        issue_window.title("Выдать книгу")
        issue_window.geometry("300x200")
        tk.Label(issue_window, text="Введите ID книги для выдачи:").pack(pady=5)
        id_entry = tk.Entry(issue_window)
        id_entry.pack(pady=5)
        tk.Label(issue_window, text="Введите имя (если книга зарезервирована):").pack(pady=5)
        name_entry = tk.Entry(issue_window)
        name_entry.pack(pady=5)
        tk.Button(issue_window, text="Выдать", 
                  command=lambda: self.confirm_issue(id_entry, name_entry, issue_window)).pack(pady=5)

    def confirm_issue(self, id_entry, name_entry, window):
        book_id = id_entry.get().strip()
        name = name_entry.get().strip()
        if book_id:
            if self.model.issue_book_by_id(book_id, name):
                self.load_books()
            else:
                print("Ошибка: не удалось выдать книгу")
        window.destroy()

    def open_return_window(self):
        return_window = tk.Toplevel()
        return_window.title("Вернуть книгу")
        return_window.geometry("300x150")
        tk.Label(return_window, text="Введите ID книги для возврата:").pack(pady=5)
        id_entry = tk.Entry(return_window)
        id_entry.pack(pady=5)
        tk.Button(return_window, text="Вернуть", 
                  command=lambda: self.confirm_return(id_entry, return_window)).pack(pady=5)

    def confirm_return(self, id_entry, window):
        book_id = id_entry.get().strip()
        if book_id:
            if self.model.return_book_by_id(book_id):
                self.load_books()
            else:
                print("Ошибка: не удалось вернуть книгу")
        window.destroy()

    def open_reserve_window(self):
        reserve_window = tk.Toplevel()
        reserve_window.title("Резервировать книгу")
        reserve_window.geometry("300x200")
        tk.Label(reserve_window, text="Введите ID книги для резервирования:").pack(pady=5)
        id_entry = tk.Entry(reserve_window)
        id_entry.pack(pady=5)
        tk.Label(reserve_window, text="Введите имя для резервирования:").pack(pady=5)
        name_entry = tk.Entry(reserve_window)
        name_entry.pack(pady=5)
        tk.Button(reserve_window, text="Резервировать", 
                  command=lambda: self.confirm_reserve(id_entry, name_entry, reserve_window)).pack(pady=5)

    def confirm_reserve(self, id_entry, name_entry, window):
        book_id = id_entry.get().strip()
        name = name_entry.get().strip()
        if book_id and name:
            if self.model.reserve_book_by_id(book_id, name):
                self.load_books()
            else:
                print("Ошибка: не удалось зарезервировать книгу")
        window.destroy()
