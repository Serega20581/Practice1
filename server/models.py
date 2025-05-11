from database import db

class Book(db.Model):
    __tablename__ = 'books'  # Имя таблицы
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default="доступна")
    issued_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Book {self.title}, {self.status}>'
