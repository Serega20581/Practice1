import os
os.environ['PGCLIENTENCODING'] = 'UTF8'

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime

app = Flask(__name__)
# Замените 'yourdbname' на имя вашей базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Определяем модель книги с добавленным полем reserved_by
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default="доступна")
    issued_date = db.Column(db.DateTime, nullable=True)
    reserved_by = db.Column(db.String(120), nullable=True)  # Имя, на которое зарезервирована книга

    def __repr__(self):
        return f'<Book {self.title}, {self.status}>'

with app.app_context():
    # Создаем таблицы, если их еще нет
    db.create_all()
    # Проверяем наличие столбца reserved_by в таблице books и, если его нет, добавляем его
    with db.engine.begin() as connection:
        result = connection.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name = 'books' AND column_name = 'reserved_by'")
        )
        if result.fetchone() is None:
            connection.execute(text("ALTER TABLE books ADD COLUMN reserved_by VARCHAR(120)"))

@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([
        {
            'id': b.id,
            'title': b.title,
            'author': b.author,
            'status': b.status,
            'reserved_by': b.reserved_by
        } for b in books
    ])

@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    new_book = Book(title=data.get('title'), author=data.get('author'))
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'id': new_book.id}), 201

@app.route('/books/issue/<int:book_id>', methods=['PUT'])
def issue_book(book_id):
    book = Book.query.get(book_id)
    if book:
        data = request.get_json() or {}
        if book.status == 'зарезервирована':
            # Если книга зарезервирована, проверяем, передано ли имя и совпадает ли оно с reserved_by
            if 'name' not in data or data['name'] != book.reserved_by:
                return jsonify({'error': 'Имя не совпадает с забронированным'}), 400
        if book.status in ['доступна', 'зарезервирована']:
            book.status = 'выдана'
            book.issued_date = datetime.utcnow()
            book.reserved_by = None  # Сбрасываем резервирование
            db.session.commit()
            return jsonify({'message': 'Книга выдана'}), 200
        else:
            return jsonify({'error': 'Книга не доступна для выдачи'}), 400
    return jsonify({'error': 'Книга не найдена'}), 404

@app.route('/books/return/<int:book_id>', methods=['PUT'])
def return_book(book_id):
    book = Book.query.get(book_id)
    if book:
        if book.status == 'выдана':
            book.status = 'доступна'
            book.issued_date = None
            db.session.commit()
            return jsonify({'message': 'Книга возвращена'}), 200
        else:
            return jsonify({'error': 'Книга не выдана'}), 400
    return jsonify({'error': 'Книга не найдена'}), 404

@app.route('/books/reserve/<int:book_id>', methods=['PUT'])
def reserve_book(book_id):
    book = Book.query.get(book_id)
    if book:
        data = request.get_json() or {}
        if 'name' not in data or not data['name']:
            return jsonify({'error': 'Необходимо указать имя для резервирования'}), 400
        if book.status != 'доступна':
            return jsonify({'error': 'Книга не доступна для резервирования'}), 400
        book.status = 'зарезервирована'
        book.reserved_by = data['name']
        db.session.commit()
        return jsonify({'message': 'Книга зарезервирована'}), 200
    return jsonify({'error': 'Книга не найдена'}), 404

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify({'message': 'Книга удалена'}), 200
    return jsonify({'error': 'Книга не найдена'}), 404

if __name__ == '__main__':
    app.run(debug=True)
