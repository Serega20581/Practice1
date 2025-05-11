import tkinter as tk

class MainView:
    def __init__(self, root, add_book_callback, delete_book_callback, issue_book_callback, return_book_callback, reserve_book_callback):
        self.root = root
        self.root.title("Управление библиотекой")
        self.root.geometry("600x500")
        
        # Заголовок
        header_frame = tk.Frame(root)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        title_label = tk.Label(header_frame, text="Управление библиотекой", font=("Helvetica", 16, "bold"))
        title_label.pack()

        # Фрейм для списка книг с прокруткой
        list_frame = tk.Frame(root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.book_list = tk.Listbox(list_frame, font=("Helvetica", 12))
        self.book_list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.book_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.book_list.yview)

        # Фрейм для ввода данных о книге
        input_frame = tk.Frame(root)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        self.title_input = tk.Entry(input_frame, font=("Helvetica", 12))
        self.title_input.insert(0, "Название книги")
        self.title_input.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.author_input = tk.Entry(input_frame, font=("Helvetica", 12))
        self.author_input.insert(0, "Автор")
        self.author_input.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)

        # Фрейм для кнопок
        button_frame = tk.Frame(root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        self.add_button = tk.Button(button_frame, text="Добавить книгу", command=add_book_callback, font=("Helvetica", 12))
        self.add_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.delete_button = tk.Button(button_frame, text="Удалить книгу", command=delete_book_callback, font=("Helvetica", 12))
        self.delete_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.issue_button = tk.Button(button_frame, text="Выдать книгу", command=issue_book_callback, font=("Helvetica", 12))
        self.issue_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.return_button = tk.Button(button_frame, text="Вернуть книгу", command=return_book_callback, font=("Helvetica", 12))
        self.return_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.reserve_button = tk.Button(button_frame, text="Резервировать книгу", command=reserve_book_callback, font=("Helvetica", 12))
        self.reserve_button.grid(row=0, column=4, padx=5, pady=5, sticky="ew")
