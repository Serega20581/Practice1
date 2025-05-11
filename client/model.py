import requests

class BookModel:
    BASE_URL = 'http://localhost:5000'  # Адрес сервера

    def get_books(self):
        response = requests.get(f'{self.BASE_URL}/books')
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def add_book(self, title, author):
        data = {'title': title, 'author': author}
        response = requests.post(f'{self.BASE_URL}/books', json=data)
        if response.status_code == 201:
            return response.json()  # Ожидается возврат {'id': ...}
        else:
            return None

    def issue_book_by_id(self, book_id, name=""):
        data = {"name": name} if name else {}
        response = requests.put(f'{self.BASE_URL}/books/issue/{book_id}', json=data)
        return response.status_code == 200

    def return_book_by_id(self, book_id):
        response = requests.put(f'{self.BASE_URL}/books/return/{book_id}')
        return response.status_code == 200

    def reserve_book_by_id(self, book_id, name):
        data = {"name": name}
        response = requests.put(f'{self.BASE_URL}/books/reserve/{book_id}', json=data)
        return response.status_code == 200

    def delete_book_by_id(self, book_id):
        response = requests.delete(f'{self.BASE_URL}/books/{book_id}')
        return response.status_code == 200
