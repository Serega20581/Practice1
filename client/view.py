import tkinter as tk
from tkinter import ttk
from typing import Optional
try:
    import ttkbootstrap as tb
    _HAS_TTB = True
except Exception:
    _HAS_TTB = False

class MainView:
    def __init__(self, root, add_book_callback, delete_book_callback, issue_book_callback, return_book_callback, reserve_book_callback, on_item_double_click=None, on_refresh=None, on_sort=None):
        self.root = root
        self.root.title("Онлайн библиотека")
        self.root.geometry("800x600")

        # Theme and styles
        # If ttkbootstrap is available, use its style for a modern look
        self.bootstrap_style = None
        if _HAS_TTB:
            try:
                self.bootstrap_style = tb.Style()
            except Exception:
                self.bootstrap_style = None

        # Provide a `style` variable that points to the active style API
        # so downstream code can call `style.configure(...)` regardless
        # of whether ttkbootstrap is present.
        if getattr(self, 'bootstrap_style', None) is not None:
            style = self.bootstrap_style
        else:
            style = ttk.Style()
            try:
                style.theme_use('clam')
            except Exception:
                pass
        default_font = ("Segoe UI", 10)
        header_font = ("Segoe UI", 14, "bold")

        style.configure('Header.TLabel', font=header_font)
        style.configure('TButton', font=default_font, padding=6)
        style.configure('TEntry', padding=4)
        style.configure('Treeview', font=("Segoe UI", 10))

        # Header
        header_frame = ttk.Frame(root, padding=(12, 12))
        header_frame.pack(fill=tk.X)
        title_label = ttk.Label(header_frame, text="Онлайн библиотека", style='Header.TLabel')
        title_label.pack(side=tk.LEFT)

        # Theme selector (if ttkbootstrap available)
        if _HAS_TTB and getattr(self, 'bootstrap_style', None) is not None:
            try:
                themes = list(self.bootstrap_style.theme_names())
            except Exception:
                themes = ['litera', 'darkly']
            self.theme_select = ttk.Combobox(header_frame, values=themes, state='readonly', width=12)
            # set current theme
            try:
                current = self.bootstrap_style.theme_use()
            except Exception:
                current = themes[0] if themes else ''
            self.theme_select.set(current)
            self.theme_select.pack(side=tk.RIGHT)
            self.theme_select.bind('<<ComboboxSelected>>', lambda e: self._change_theme())

        # Search / controls row
        search_frame = ttk.Frame(root, padding=(12, 6))
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text='Поиск:').pack(side=tk.LEFT, padx=(0,6))
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,8))
        self.search_entry.bind('<KeyRelease>', lambda e: self._schedule_search())

        ttk.Label(search_frame, text='Статус:').pack(side=tk.LEFT, padx=(0,6))
        self.status_filter = ttk.Combobox(search_frame, values=['Все','доступна','выдана','зарезервирована'], state='readonly', width=16)
        self.status_filter.set('Все')
        self.status_filter.pack(side=tk.LEFT, padx=(0,8))
        self.status_filter.bind('<<ComboboxSelected>>', lambda e: self._schedule_search())

        self.refresh_button = ttk.Button(search_frame, text='Обновить', command=on_refresh)
        self.refresh_button.pack(side=tk.LEFT)

        # Main frame
        main_frame = ttk.Frame(root, padding=(12, 8))
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left: Treeview list of books
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        columns = ('id', 'title', 'author', 'status', 'reserved_by')
        self.book_list = ttk.Treeview(list_frame, columns=columns, show='headings', selectmode='browse')
        self.book_list.heading('title', text='Название')
        self.book_list.heading('author', text='Автор')
        self.book_list.heading('status', text='Статус')
        self.book_list.heading('reserved_by', text='Зарезервирована на')
        # hide id column but keep for reference
        self.book_list.heading('id', text='ID')
        self.book_list.column('id', width=0, stretch=False)
        self.book_list.column('title', width=320)
        self.book_list.column('author', width=140)
        self.book_list.column('status', width=100)
        self.book_list.column('reserved_by', width=160)

        vsb = ttk.Scrollbar(list_frame, orient='vertical', command=self.book_list.yview)
        self.book_list.configure(yscrollcommand=vsb.set)
        self.book_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # attach heading click for sorting
        self._on_sort = on_sort
        for col in columns:
            self.book_list.heading(col, command=lambda c=col: self._on_heading_click(c))

        # Right: controls
        control_frame = ttk.Frame(main_frame, width=280)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Input fields
        input_frame = ttk.LabelFrame(control_frame, text='Новая книга', padding=(8, 8))
        input_frame.pack(fill=tk.X, padx=8, pady=8)

        self.title_input = ttk.Entry(input_frame)
        self.title_input.insert(0, 'Название книги')
        self.title_input.pack(fill=tk.X, padx=6, pady=6)

        self.author_input = ttk.Entry(input_frame)
        self.author_input.insert(0, 'Автор')
        self.author_input.pack(fill=tk.X, padx=6, pady=(0,6))

        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, padx=8, pady=8)

        self.add_button = ttk.Button(button_frame, text="Добавить книгу", command=add_book_callback)
        self.add_button.pack(fill=tk.X, pady=4)

        # Allow adding by pressing Enter in title or author fields (convenience)
        try:
            self.title_input.bind('<Return>', lambda e: self.add_button.invoke())
            self.author_input.bind('<Return>', lambda e: self.add_button.invoke())
        except Exception:
            pass

        self.delete_button = ttk.Button(button_frame, text="Удалить книгу", command=delete_book_callback)
        self.delete_button.pack(fill=tk.X, pady=4)

        # Delete selected convenience button + selected id display
        self.selected_id_label = ttk.Label(control_frame, text='Выбран ID: —', font=("Segoe UI", 10))
        self.selected_id_label.pack(padx=8, pady=(4,2))

        # (duplicate delete button removed — use "Удалить книгу" which opens ID dialog)

        self.issue_button = ttk.Button(button_frame, text="Выдать книгу", command=issue_book_callback)
        self.issue_button.pack(fill=tk.X, pady=4)

        self.return_button = ttk.Button(button_frame, text="Вернуть книгу", command=return_book_callback)
        self.return_button.pack(fill=tk.X, pady=4)

        self.reserve_button = ttk.Button(button_frame, text="Резервировать книгу", command=reserve_book_callback)
        self.reserve_button.pack(fill=tk.X, pady=4)

        # Footer / status
        footer = ttk.Frame(root)
        footer.pack(fill=tk.X, padx=12, pady=(0,12))
        self.status_label = ttk.Label(footer, text='Готово', font=("Segoe UI", 9))
        self.status_label.pack(side=tk.LEFT)

        # Small UX: clear placeholder when focusing
        self._placeholders = {
            self.title_input: 'Название книги',
            self.author_input: 'Автор'
        }
        # temporary flag to suppress automatic placeholder restore (used after add)
        self._suppress_restore = False
        for entry, ph in self._placeholders.items():
            entry.bind('<FocusIn>', lambda e, ph=ph, w=entry: self._clear_placeholder(e, ph, w))
            entry.bind('<FocusOut>', lambda e, ph=ph, w=entry: self._restore_placeholder(e, ph, w))

        # Treeview double-click callback
        self._on_item_double_click = on_item_double_click
        if self._on_item_double_click:
            self.book_list.bind('<Double-1>', self._handle_double_click)

        # Selection change handling
        self._selection_callback = None
        self.book_list.bind('<<TreeviewSelect>>', self._handle_selection_change)

        # Tags/styles for statuses (background + foreground)
        try:
            self.book_list.tag_configure('available', background='#e8f5e9', foreground='#1b5e20')
            self.book_list.tag_configure('issued', background='#ffebee', foreground='#b71c1c')
            self.book_list.tag_configure('reserved', background='#fff3e0', foreground='#e65100')
        except Exception:
            # Older tkinter/ttk may ignore tag settings; ignore gracefully
            pass

        # Context menu for quick actions
        self._menu = tk.Menu(root, tearoff=0)
        self._menu.add_command(label='Выдать', command=lambda: self._menu_action('issue'))
        self._menu.add_command(label='Вернуть', command=lambda: self._menu_action('return'))
        self._menu.add_command(label='Резервировать', command=lambda: self._menu_action('reserve'))
        self._menu.add_separator()
        self._menu.add_command(label='Удалить', command=lambda: self._menu_action('delete'))

        # store callback bridge set by controller
        self._menu_callback = None

    # Selection helpers
    def _handle_selection_change(self, event):
        sel = self.book_list.selection()
        book_id = None
        if sel:
            vals = self.book_list.item(sel[0], 'values')
            if vals:
                book_id = vals[0]
        # update label
        self.set_selected_book_id(book_id)
        try:
            if self._selection_callback:
                self._selection_callback(book_id)
        except Exception:
            pass

    def set_selection_callback(self, cb):
        self._selection_callback = cb

    def get_selected_book_id(self):
        sel = self.book_list.selection()
        if not sel:
            return None
        vals = self.book_list.item(sel[0], 'values')
        return vals[0] if vals else None

    def set_selected_book_id(self, book_id):
        if book_id:
            self.selected_id_label.config(text=f'Выбран ID: {book_id}')
        else:
            self.selected_id_label.config(text='Выбран ID: —')

    def set_busy(self, busy: bool, text: str = None):
        """Set UI busy state: disable/enable controls and update status label.
        Call with True to disable controls while background work runs.
        """
        try:
            controls = [
                getattr(self, 'add_button', None),
                getattr(self, 'delete_button', None),
                getattr(self, 'issue_button', None),
                getattr(self, 'return_button', None),
                getattr(self, 'reserve_button', None),
                getattr(self, 'refresh_button', None),
            ]
            for c in controls:
                if c is None:
                    continue
                try:
                    if busy:
                        c.state(['disabled'])
                    else:
                        c.state(['!disabled'])
                except Exception:
                    try:
                        c.config(state='disabled' if busy else 'normal')
                    except Exception:
                        pass
            # also disable inputs
            try:
                if busy:
                    self.title_input.config(state='disabled')
                    self.author_input.config(state='disabled')
                else:
                    self.title_input.config(state='normal')
                    self.author_input.config(state='normal')
            except Exception:
                pass
            # status
            if text is not None:
                self.set_status(text)
            else:
                if busy:
                    self.set_status('Выполняется...')
                else:
                    self.set_status('Готово')
        except Exception:
            pass

        # Bind right-click
        self.book_list.bind('<Button-3>', self._show_context_menu)
        # Bind Delete key
        root.bind('<Delete>', self._on_delete_key)

    def _on_heading_click(self, column: str):
        # Normalize: 'id','title','author','status','reserved_by'
        if self._on_sort:
            self._on_sort(column)

    def _handle_double_click(self, event):
        item_id = self.book_list.identify_row(event.y)
        if not item_id:
            return
        values = self.book_list.item(item_id, 'values')
        # values layout: (id, title, author, status, reserved_by)
        try:
            book_id = values[0]
        except Exception:
            book_id = None
        if self._on_item_double_click:
            self._on_item_double_click(book_id)

    def _change_theme(self):
        if not getattr(self, 'bootstrap_style', None):
            return
        try:
            theme = self.theme_select.get()
            if theme:
                self.bootstrap_style.theme_use(theme)
        except Exception:
            pass

    def _show_context_menu(self, event):
        # select row under cursor
        item_id = self.book_list.identify_row(event.y)
        if item_id:
            self.book_list.selection_set(item_id)
            # store selected book id in menu for callback
            values = self.book_list.item(item_id, 'values')
            book_id = values[0] if values else None
            self._menu.book_id = book_id
            self._menu.post(event.x_root, event.y_root)

    def _menu_action(self, action):
        if self._menu_callback and hasattr(self._menu, 'book_id'):
            self._menu_callback(action, self._menu.book_id)

    def set_menu_callback(self, cb):
        self._menu_callback = cb

    def set_search_callback(self, cb):
        """Register a callback that will be called when search or status filter changes.
        The callback should accept no arguments (view will read the current values).
        """
        self._search_callback = cb

    def _schedule_search(self, delay_ms: int = 300):
        """Debounce search calls so controller isn't invoked on every keystroke.
        Call this from key handlers; it will call `_on_search` after `delay_ms`
        of inactivity.
        """
        try:
            # cancel previous scheduled call
            if getattr(self, '_search_after_id', None):
                self.root.after_cancel(self._search_after_id)
        except Exception:
            pass
        try:
            self._search_after_id = self.root.after(delay_ms, self._on_search)
        except Exception:
            # fallback to immediate call
            self._on_search()

    def _on_search(self):
        # Called after debounce timer or combobox selection
        try:
            if getattr(self, '_search_callback', None):
                self._search_callback()
        except Exception:
            pass

    def _on_delete_key(self, event):
        sel = self.book_list.selection()
        if sel:
            item_id = sel[0]
            values = self.book_list.item(item_id, 'values')
            book_id = values[0] if values else None
            if self._menu_callback:
                self._menu_callback('delete', book_id)

    def set_status(self, text: str):
        self.status_label.config(text=text)

    def _clear_placeholder(self, event, placeholder, widget):
        if widget.get() == placeholder:
            widget.delete(0, tk.END)

    def _restore_placeholder(self, event, placeholder, widget):
        # If suppression flag is set, skip restoring placeholders temporarily
        if getattr(self, '_suppress_restore', False):
            return
        if widget.get().strip() == '':
            widget.insert(0, placeholder)

    def suppress_placeholder_once(self, timeout_ms: int = 200):
        """Temporarily suppress placeholder restoration for `timeout_ms` milliseconds.
        Used after clearing fields so placeholders are not immediately re-inserted.
        """
        try:
            self._suppress_restore = True
            def _clear_flag():
                try:
                    self._suppress_restore = False
                except Exception:
                    pass
            self.root.after(timeout_ms, _clear_flag)
        except Exception:
            self._suppress_restore = False

    def clear_new_book_inputs(self):
        """Clear the 'Новая книга' inputs and focus the title field, suppressing placeholders briefly."""
        try:
            # Insert placeholders immediately so they are visible right after add
            try:
                self.title_input.delete(0, tk.END)
                self.title_input.insert(0, 'Название книги')
            except Exception:
                pass
            try:
                self.author_input.delete(0, tk.END)
                self.author_input.insert(0, 'Автор')
            except Exception:
                pass
            # move focus away so placeholders are visible (user can click into title to type)
            try:
                self.root.focus()
            except Exception:
                pass
        except Exception:
            pass
