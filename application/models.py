from datetime import datetime, date, timedelta
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import lorem

from flask_security import UserMixin, RoleMixin
from sqlalchemy.ext.hybrid import hybrid_property

db = SQLAlchemy()

class Section(db.Model):
    __tablename__ = "section"
    s_id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now())
    description = db.Column(db.String(100), nullable=False)
    bookID_link = db.relationship("Book", uselist=False, backref="genre")
    
    def to_dict(self):
        return {
            "s_id": self.s_id,
            "name": self.name,
            "date_created": self.date_created,
            "description": self.description,
            # "books": [book.book_name for book in self.bookID_link]
        }
    def __repr__(self) -> str:
        return self.name

class Book(db.Model):
    __tablename__ = "book"
    b_id = db.Column(db.Integer(), primary_key=True)
    book_name = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.String(200), nullable=False)
    authors = db.Column(db.String(100), nullable=False)
    avgRating = db.Column(db.Float())
    sectionID_link = db.Column(db.Integer(), db.ForeignKey('section.s_id'), nullable=False)
    
    #relation with user?
    requests = db.relationship('RequestedBooks', backref='book', lazy=True)
    issues = db.relationship('IssuedBooks', backref='book', lazy=True)
    returns = db.relationship('ReturnedBooks', backref='book', lazy=True)

    #HYBRID PROPERTY
    @hybrid_property
    def hybRating(self) -> float:
        count = 0
        returned = ReturnedBooks.query.filter_by(book_name = self.book_name).all()
        data = [bookReturn.rating for bookReturn in returned]
        slist = 0
        for i in data:
            slist += i
            count += 1
        if len(data) > 0:
            avg = slist/count
        else:
            avg = 0.0
        return ("%.2f" % round(avg, 2))

    def to_dict(self):        
        book = Book.query.filter_by(b_id=self.b_id).first()
        genre = Section.query.filter_by(s_id = self.sectionID_link).first()
        return {
            "b_id": self.b_id,
            "book_name": self.book_name,
            "sectionID_Link": book.sectionID_link,
            "content": self.content,
            "authors": self.authors,
            "avgRating":self.hybRating,
            "SectionName":genre.name
        }
    def __repr__(self) -> str:
        return self.book_name

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    fav_genre = db.Column(db.String(50), nullable=False)
    fav_book = db.Column(db.String(100), nullable=False)
    fav_author = db.Column(db.String(50), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "role": self.role,
            "fav_genre": self.fav_genre,
            "fav_book": self.fav_book,
            "fav_author": self.fav_author,
        }
    def __repr__(self) -> str:
        return self.username
    
    def password_hash(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)
    @classmethod
    def get_user_by_usrnm(cls, username):
        return cls.query.filter_by(username = username).first()
    def save_user(self):
        db.session.add(self)
        db.session.commit()
    def delete_user(self):
        db.session.delete(self)
        db.session.commit()

class TokenBlockedList(db.Model):
    # __tablename__ = "tokenblockedlist"
    
    id = db.Column(db.Integer(), primary_key=True)
    jti = db.Column(db.String(), nullable=False) #Unique identifier for each jwt
    username = db.Column(db.String(), nullable=False) #defined as 'sub' in jwt claims
    create_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now())

    def __repr__(self):
        return f"<Token {self.jti}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()

class RequestedBooks(db.Model):
    __tablename__ = "requestedbooks"

    request_id = db.Column(db.Integer(), primary_key=True)
    student_username = db.Column(db.String(), db.ForeignKey('user.username'), nullable=False) #Max 5 requests
    book_id = db.Column(db.Integer(), db.ForeignKey('book.b_id'), nullable=False)

    # request_date = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now()) #Add everywhere!! 

    status = db.Column(db.String(10), default='pending') #pending, requested, approved, declined(?)
    approved = db.Column(db.Boolean(), default=False) #Useful to check requested entries. 

    def to_dict(self):
        return {
            "request_id": self.request_id,
            "student_username": self.student_username,
            "book_id": self.book_id,
            "status": self.status,
            "approved": self.approved
        }
    
    def __repr__(self) -> str:
        return f"Request ID: {self.request_id}"

class IssuedBooks(db.Model):
    __tablename__ = "issuedbooks"

    issue_id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.Integer(), nullable=False)
    book_name = db.Column(db.String(50), db.ForeignKey('book.book_name'), nullable=False)
    issue_date = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now())
    daysLeft = db.Column(db.Integer())

    def to_dict(self):
        issue_date_string = self.issue_date.strftime("%Y-%m-%d %H:%M:%S.%f") 
        datetime_object = datetime.strptime(issue_date_string, "%Y-%m-%d %H:%M:%S.%f")
        issue_date_type = datetime_object.date()

        allowed_Date = issue_date_type + timedelta(days=7)
        # days_left = (allowed_Date - datetime.now().date()).days
        days_left = max(0, (allowed_Date - datetime.now().date()).days)
        return {
            "issue_id": self.issue_id,
            "username": self.username,
            "book_name": self.book_name,
            "issue_date": self.issue_date,
            # "daysLeft": str((allowed_Date - issue_date_type).days) + " days"
            # "daysLeft": f"{max(0, days_left)} days"
            "daysLeft": days_left
        }
    def __repr__(self) -> str:
        return self.issue_id
    
    @staticmethod
    def update_days_left():
        with db.session() as session:
            issued_books = session.query(IssuedBooks).all()
            for book in issued_books:
                allowed_date = book.issue_date + timedelta(days=7)
                book.daysLeft = max(0, (allowed_date.date() - datetime.now().date()).days)
                # if book.daysLeft == 0:

            session.commit()
    
class ReturnedBooks(db.Model): 
    __tablename__ = "returnedbooks"

    return_id = db.Column(db.Integer(), primary_key=True)
    issue_ID = db.Column(db.Integer(), db.ForeignKey('issuedbooks.issue_id'), nullable=False)
    return_date = db.Column(db.DateTime(timezone=True), default=datetime.now())
    book_name = db.Column(db.String(), db.ForeignKey('book.book_name'), nullable=False)
    username = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            "return_id": self.return_id,
            "issue_ID": self.issue_ID,
            "return_date": self.return_date,
            "book_name": self.book_name,
            "username": self.username,
            "rating": self.rating,
        }
    def __repr__(self) -> str:
        return self.return_id

def create_initial_data(db):
    '''create users'''
    librarian = User(
        username="Librarian",
        password=generate_password_hash("Lib"),
        role="Librarian",
        fav_author="Douglas Adams",
        fav_book="The Hitchhiker's Guide to the Galaxy",
        fav_genre="Sci-fi"

    )
    student1 = User(
        username="Student1",
        password=generate_password_hash("Stud1"),
        role="Student",
        fav_author="Douglas Adams",
        fav_book="The Restaurant at the End of the Universe",
        fav_genre="Thriller, Space"
    )

    '''create a section'''
    section = Section(
        name="Fiction",
        description="Books in this genre can be made up (fictional) in nature.",
        date_created=datetime.now(),
    )

    book = Book(
        book_name="Lorem",
        authors="Richard McClintock",
        sectionID_link=1,
        content=lorem.text()
    )

    db.session.add(section)
    db.session.commit()
    db.session.add(book)
    db.session.commit()
    db.session.add_all([librarian,student1])
    db.session.commit()    

#====================END OF FILE====================#