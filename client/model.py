import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BookModel:
    BASE_URL = 'http://localhost:5000'  # Адрес сервера

    def __init__(self, timeout: int = 5):
        # session with retries and connection pooling
        self.timeout = timeout
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.3, status_forcelist=(500, 502, 503, 504))
        adapter = HTTPAdapter(max_retries=retries, pool_maxsize=10)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def get_books(self):
        try:
            resp = self.session.get(f'{self.BASE_URL}/books', timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return []

    def add_book(self, title, author):
        data = {'title': title, 'author': author}
        try:
            resp = self.session.post(f'{self.BASE_URL}/books', json=data, timeout=self.timeout)
            if resp.status_code == 201:
                return resp.json()
        except Exception:
            pass
        return None

    def issue_book_by_id(self, book_id, name=""):
        data = {"name": name} if name else {}
        try:
            resp = self.session.put(f'{self.BASE_URL}/books/issue/{book_id}', json=data, timeout=self.timeout)
            return resp.status_code == 200
        except Exception:
            return False

    def return_book_by_id(self, book_id):
        try:
            resp = self.session.put(f'{self.BASE_URL}/books/return/{book_id}', timeout=self.timeout)
            return resp.status_code == 200
        except Exception:
            return False

    def reserve_book_by_id(self, book_id, name):
        data = {"name": name}
        try:
            resp = self.session.put(f'{self.BASE_URL}/books/reserve/{book_id}', json=data, timeout=self.timeout)
            return resp.status_code == 200
        except Exception:
            return False

    def delete_book_by_id(self, book_id):
        try:
            resp = self.session.delete(f'{self.BASE_URL}/books/{book_id}', timeout=self.timeout)
            return resp.status_code == 200
        except Exception:
            return False
