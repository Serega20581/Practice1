# Онлайн библиотека

Автор: Сергей Топтунов


REST API на Flask + десктопный GUI на Tkinter. Сервер хранит данные о книгах (SQLite по умолчанию, Postgres через `DATABASE_URL`), клиент обеспечивает поиск, фильтрацию и операции с книгами.


## Структура репозитория (ключевые файлы)
- `server/app.py`  Flask-приложение и модель `Book`.
- `server/requirments.txt`  зависимости сервера.
- `client/main.py`  точка входа GUI.
- `client/view.py`  представление (Tkinter/ttk, Treeview, поля ввода, кнопки).
- `client/controller.py`  логика клиента: загрузка, фильтрация, фоновые задачи, действия (issue/return/reserve/delete/add).
- `client/model.py`  HTTP-клиент (использует `requests.Session` с retry и pool).
- `Dockerfile`, `docker-compose.yml`  контейнеризация и развёртывание (Postgres + web).

## Технологии
- Backend: `Flask`, `Flask-SQLAlchemy`, `Flask-Migrate`.
- Client: `tkinter`, `ttk`, опционально `ttkbootstrap`.
- HTTP: `requests` с `Session` и `Retry`.
- Threads: `concurrent.futures.ThreadPoolExecutor` для фоновых задач.
- DB: SQLite локально, Postgres в Docker.

## Краткое описание API
- `GET /health`  проверка состояния (возвращает `{status: 'ok'}`).
- `GET /books`  получить список книг (JSON).
- `POST /books`  добавить книгу (payload `{title, author}`), возвращает `201` и `{'id': ...}`.
- `PUT /books/issue/<id>`  выдать книгу (опционально `{name}` когда книга зарезервирована).
- `PUT /books/return/<id>`  вернуть книгу.
- `PUT /books/reserve/<id>`  зарезервировать книгу (`{name}`).
- `DELETE /books/<id>`  удалить книгу.

## Как запустить локально (Windows / PowerShell)
1. Создайте venv и установите зависимости:
```powershell
Set-Location -Path 'C:\Users\Сергей\Desktop\OnlineLibrary'
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\server\requirments.txt
pip install -r .\client\requirements.txt
.\.venv\Scripts\python -m pip install Flask-Migrate
```
2. Запустите сервер (SQLite по умолчанию):
```powershell
.\.venv\Scripts\python.exe .\server\app.py
```
3. В другом окне запустите клиент:
```powershell
.\.venv\Scripts\python.exe .\client\main.py
```

## Запуск через Docker (Postgres + Gunicorn)
```powershell
docker-compose up --build
# После сборки сервер доступен по http://localhost:5000
```

## Особенности клиента (из текущей ветки)
- Поиск с дебаунсом (300 ms) и локальной фильтрацией по кэшу (`title`, `author`, `reserved_by`).
- Фоновые сетевые операции через `ThreadPoolExecutor`  UI не блокируется.
- `requests.Session` с retry и connection pool для стабильности.
- Отображение выбранного `ID`, контекстное меню, keyboard shortcuts (Delete), улучшенная UX при добавлении книги (поля готовы для следующего ввода).

## Тестирование
- В репозитории есть базовый тест `/health` под `pytest`.
```powershell
.\.venv\Scripts\pytest -q
```





