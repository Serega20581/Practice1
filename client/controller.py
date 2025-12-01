import tkinter as tk
from tkinter import messagebox
from model import BookModel
from view import MainView
import traceback
import concurrent.futures

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
            self.open_reserve_window,
            on_item_double_click=self.on_item_double_click,
            on_refresh=self.refresh,
            on_sort=self.sort_by_column
        )
        # register search callback so the view can notify controller on filter changes
        try:
            self.view.set_search_callback(self._on_search)
        except Exception:
            pass
        # cached books retrieved from server (used for local filtering)
        self._books = []
        # Executor for background tasks to reuse threads and limit concurrency
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        # register context menu callback
        self.view.set_menu_callback(self._on_menu_action)
        # register selection callback
        try:
            self.view.set_selection_callback(self._on_selection_changed)
        except Exception:
            pass
        self.load_books()

    def load_books(self):
        # Fetch books in a background thread to avoid blocking UI
        def _fetch():
            try:
                books = self.model.get_books() or []
            except Exception:
                traceback.print_exc()
                books = []

            def _update_ui():
                tree = self.view.book_list
                for item in tree.get_children():
                    tree.delete(item)
                # update cache
                self._books = books
                for book in books:
                    status = (book.get('status') or '').lower()
                    tag = 'available'
                    if 'выдан' in status or 'выдана' in status:
                        tag = 'issued'
                    elif 'зарезерв' in status:
                        tag = 'reserved'
                    tree.insert('', tk.END, values=(book.get('id'), book.get('title'), book.get('author'), book.get('status', 'неизвестно'), book.get('reserved_by') or ''), tags=(tag,))
                self.view.set_status(f'Загружено записей: {len(books)}')
                try:
                    self.view.set_busy(False)
                except Exception:
                    pass

            try:
                try:
                    self.view.set_busy(True, 'Загрузка...')
                except Exception:
                    pass
                self.view.root.after(0, _update_ui)
            except Exception:
                pass

        # submit to executor
        try:
            self._executor.submit(_fetch)
        except Exception:
            # fallback to thread
            threading = __import__('threading')
            threading.Thread(target=_fetch, daemon=True).start()

    def on_item_double_click(self, book_id):
        # Открыть окно действий для выбранной книги
        self.open_item_actions(book_id)

    def _on_selection_changed(self, book_id):
        # Can be used to enable/disable buttons or preload data; currently we just keep selection state
        self._selected_book_id = book_id
    

    # Search / filter / refresh / sort helpers
    def refresh(self):
        self.load_books()

    def _matches_filter(self, book, text: str, status_filter: str):
        if text:
            text = text.lower()
            title = (book.get('title') or '').lower()
            author = (book.get('author') or '').lower()
            reserved = (book.get('reserved_by') or '').lower()
            if text not in title and text not in author and text not in reserved:
                return False
        if status_filter and status_filter != 'Все':
            s = (book.get('status') or '').lower()
            if status_filter not in s:
                return False
        return True

    def filter_and_show(self):
        # read filters from view and apply client-side
        tree = self.view.book_list
        for item in tree.get_children():
            tree.delete(item)
        # use cached copy to avoid network calls on every keystroke
        all_books = list(self._books)
        text = self.view.search_entry.get().strip()
        status_f = self.view.status_filter.get().strip()
        filtered = [b for b in all_books if self._matches_filter(b, text, status_f)]
        for book in filtered:
            status = (book.get('status') or '').lower()
            tag = 'available'
            if 'выдан' in status or 'выдана' in status:
                tag = 'issued'
            elif 'зарезерв' in status:
                tag = 'reserved'
            tree.insert('', tk.END, values=(book.get('id'), book.get('title'), book.get('author'), book.get('status', 'неизвестно'), book.get('reserved_by') or ''), tags=(tag,))
        self.view.set_status(f'Загружено записей: {len(filtered)} (из {len(all_books)})')

    def _on_search(self):
        # Debounce/simple immediate filter
        try:
            self.filter_and_show()
        except Exception:
            pass

    def sort_by_column(self, column: str):
        # Simple toggle sort on client-side data
        tree = self.view.book_list
        data = [tree.item(i, 'values') for i in tree.get_children('')]
        # find index of column
        col_index = {'id':0,'title':1,'author':2,'status':3,'reserved_by':4}.get(column, 0)
        # determine current order
        ascending = getattr(self, '_sort_asc', True)
        try:
            data.sort(key=lambda r: (r[col_index] or '').lower(), reverse=not ascending)
        except Exception:
            data.sort(key=lambda r: r[col_index], reverse=not ascending)
        # reinsert
        for item in tree.get_children(''):
            tree.delete(item)
        for row in data:
            # determine tag again
            status = (row[3] or '').lower()
            tag = 'available'
            if 'выдан' in status or 'выдана' in status:
                tag = 'issued'
            elif 'зарезерв' in status:
                tag = 'reserved'
            tree.insert('', tk.END, values=row, tags=(tag,))
        self._sort_asc = not ascending

    def _on_menu_action(self, action, book_id):
        # action: 'issue'|'return'|'reserve'|'delete'
        if action == 'issue':
            self.open_item_actions(book_id)
        elif action == 'return':
            self.perform_return(book_id)
        elif action == 'reserve':
            # open actions window to input name
            self.open_item_actions(book_id)
        elif action == 'delete':
            # show confirmation
            self.confirm_and_delete(book_id)

    def confirm_and_delete(self, book_id):
        if not book_id:
            return
        answer = messagebox.askyesno('Подтверждение удаления', f'Удалить книгу с ID {book_id}?')
        if answer:
            self.perform_delete(book_id)

    def open_item_actions(self, book_id):
        if not book_id:
            return
        actions_win = tk.Toplevel()
        actions_win.title(f'Действия с книгой ID {book_id}')
        actions_win.geometry('320x220')
        tk.Label(actions_win, text=f'Книга ID: {book_id}', font=("Segoe UI", 10, 'bold')).pack(pady=6)

        # Name entry for issue/reserve when needed
        tk.Label(actions_win, text='Имя (если нужно):').pack(pady=(6,0))
        name_entry = tk.Entry(actions_win)
        name_entry.pack(pady=6, padx=12, fill=tk.X)

        btn_frame = tk.Frame(actions_win)
        btn_frame.pack(fill=tk.X, padx=12, pady=6)

        tk.Button(btn_frame, text='Выдать', width=10, command=lambda: (self.perform_issue(book_id, name_entry.get()), actions_win.destroy())).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text='Вернуть', width=10, command=lambda: (self.perform_return(book_id), actions_win.destroy())).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text='Резервировать', width=12, command=lambda: (self.perform_reserve(book_id, name_entry.get()), actions_win.destroy())).pack(side=tk.LEFT, padx=4)

        tk.Button(actions_win, text='Удалить', fg='red', command=lambda: (self.perform_delete(book_id), actions_win.destroy())).pack(fill=tk.X, padx=12, pady=(8,2))
        tk.Button(actions_win, text='Отмена', command=actions_win.destroy).pack(fill=tk.X, padx=12)

    # Helper methods that operate directly with model (used by actions window)
    def perform_issue(self, book_id, name=""):
        def _work():
            try:
                ok = self.model.issue_book_by_id(book_id, name)
            except Exception:
                traceback.print_exc()
                ok = False

            def _finish():
                if ok:
                    self.view.set_status('Книга выдана')
                    self.load_books()
                else:
                    messagebox.showerror('Ошибка', 'Не удалось выдать книгу')
                    self.view.set_status('Ошибка при выдаче')
                try:
                    self.view.set_busy(False)
                except Exception:
                    pass

            self.view.root.after(0, _finish)

        try:
            self.view.set_busy(True, 'Выдача...')
        except Exception:
            pass
        try:
            self._executor.submit(_work)
        except Exception:
            threading.Thread(target=_work, daemon=True).start()

    def perform_return(self, book_id):
        def _work():
            try:
                ok = self.model.return_book_by_id(book_id)
            except Exception:
                traceback.print_exc()
                ok = False

            def _finish():
                if ok:
                    self.view.set_status('Книга возвращена')
                    self.load_books()
                else:
                    messagebox.showerror('Ошибка', 'Не удалось вернуть книгу')
                    self.view.set_status('Ошибка при возврате')
                try:
                    self.view.set_busy(False)
                except Exception:
                    pass

            self.view.root.after(0, _finish)

        try:
            self.view.set_busy(True, 'Возврат...')
        except Exception:
            pass
        try:
            self._executor.submit(_work)
        except Exception:
            threading.Thread(target=_work, daemon=True).start()

    def perform_reserve(self, book_id, name):
        def _work():
            try:
                ok = self.model.reserve_book_by_id(book_id, name)
            except Exception:
                traceback.print_exc()
                ok = False

            def _finish():
                if ok:
                    self.view.set_status('Книга зарезервирована')
                    self.load_books()
                else:
                    messagebox.showerror('Ошибка', 'Не удалось зарезервировать книгу')
                    self.view.set_status('Ошибка при резервировании')
                try:
                    self.view.set_busy(False)
                except Exception:
                    pass

            self.view.root.after(0, _finish)

        try:
            self.view.set_busy(True, 'Резервирование...')
        except Exception:
            pass
        try:
            self._executor.submit(_work)
        except Exception:
            threading.Thread(target=_work, daemon=True).start()

    def perform_delete(self, book_id):
        def _work():
            try:
                ok = self.model.delete_book_by_id(book_id)
            except Exception:
                traceback.print_exc()
                ok = False

            def _finish():
                if ok:
                    self.view.set_status('Книга удалена')
                    self.load_books()
                else:
                    messagebox.showerror('Ошибка', 'Не удалось удалить книгу')
                    self.view.set_status('Ошибка при удалении')
                try:
                    self.view.set_busy(False)
                except Exception:
                    pass

            self.view.root.after(0, _finish)

        try:
            self.view.set_busy(True, 'Удаление...')
        except Exception:
            pass
        try:
            self._executor.submit(_work)
        except Exception:
            threading.Thread(target=_work, daemon=True).start()

    def add_book(self):
        # Read current inputs and validate
        title = self.view.title_input.get().strip()
        author = self.view.author_input.get().strip()
        if not (title and author) or title == 'Название книги' or author == 'Автор':
            try:
                messagebox.showwarning('Ввод', 'Введите название и автора книги')
            except Exception:
                pass
            return

        # Save values for background work and immediately clear inputs so user can type next
        send_title = title
        send_author = author
        try:
            try:
                self.view.clear_new_book_inputs()
            except Exception:
                try:
                    self.view.suppress_placeholder_once(timeout_ms=700)
                except Exception:
                    pass
                try:
                    self.view.title_input.delete(0, tk.END)
                except Exception:
                    pass
                try:
                    self.view.author_input.delete(0, tk.END)
                except Exception:
                    pass
                try:
                    self.view.title_input.focus_set()
                except Exception:
                    pass
        except Exception:
            pass

        def _work():
            try:
                result = self.model.add_book(send_title, send_author)
            except Exception:
                traceback.print_exc()
                result = None

            def _finish():
                if result:
                    self.view.set_status('Книга добавлена')
                    self.load_books()
                else:
                    # restore inputs so user can retry
                    try:
                        self.view.title_input.delete(0, tk.END)
                        self.view.title_input.insert(0, send_title)
                        self.view.author_input.delete(0, tk.END)
                        self.view.author_input.insert(0, send_author)
                        self.view.title_input.focus_set()
                    except Exception:
                        pass
                    messagebox.showerror('Ошибка', 'Не удалось добавить книгу')
                    self.view.set_status('Ошибка при добавлении')
                try:
                    self.view.set_busy(False)
                except Exception:
                    pass

            self.view.root.after(0, _finish)

        try:
            self.view.set_busy(True, 'Добавление...')
        except Exception:
            pass
        try:
            self._executor.submit(_work)
        except Exception:
            threading.Thread(target=_work, daemon=True).start()

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
            # use async delete to avoid blocking UI
            self.perform_delete(book_id)
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
            self.perform_issue(book_id, name)
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
            self.perform_return(book_id)
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
            self.perform_reserve(book_id, name)
        window.destroy()
