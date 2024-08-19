from celery import shared_task
from flask import render_template_string
import flask_excel as excel
from jinja2 import Template
from sqlalchemy import func
from datetime import datetime, timedelta
from .models import db, Section, Book, User, IssuedBooks, ReturnedBooks, TokenBlockedList, RequestedBooks
# from application.models import db
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .utils import send_email
import smtplib

@shared_task(ignore_result=False)
def download_ebook(b_name):
    ebook = Book.query.filter_by(book_name=b_name).first()
    if ebook:  # Check if a book was found
        csv_output = excel.make_response_from_query_sets(
            [ebook], ["book_name", "authors", "content"], "csv"
        )
        filename = "ebooks2.csv"
        with open(filename, "wb") as f:
            f.write(csv_output.data)
        return filename
    else:
        raise ValueError(f"Book with name '{b_name}' not found")

@shared_task(ignore_result=False)
def librarian_triggered():
    all_data = []

    users = User.query.filter_by(role='Student').all()
    for user in users:
        returned_books = ReturnedBooks.query.filter_by(username=user.username).all()
        for book in returned_books:
            issued_book = IssuedBooks.query.filter_by(issue_id=book.issue_ID).first()
            if issued_book:
                all_data.append({
                    "username": user.username,
                    "book_name": book.book_name,
                    "return_date": book.return_date.strftime('%Y-%m-%d'),
                    "rating": book.rating
                })
            else:
                all_data.append({
                    "username": user.username,
                    "book_name": book.book_name,
                    "return_date": book.return_date.strftime('%Y-%m-%d'),
                    "rating": book.rating
                })
    csv_output = excel.make_response_from_records(
        all_data,
        columns=["username", "book_name", "return_date", "rating"],
        file_type="csv"
    )
    filename = "lib_report1.csv"
    with open(filename, 'wb') as f:
        f.write(csv_output.data)
    return filename

@shared_task(ignore_result=False)
def create_ebook_csv():
    ebooks = Book.query.with_entities(Book.book_name, Book.authors).all()
    # ebooks = Book.query.with_entities(Book.book_name, Book.authors, Book.avgRating).all()
    csv_output = excel.make_response_from_query_sets(ebooks, ["book_name", "authors"], "csv")
    filename = "ebooks1.csv"

    with open(filename, 'wb') as f:
        f.write(csv_output.data)
    return filename

@shared_task(ignore_result=True)
def send_daily_reminder():
    template = Template("""
    <p>Dear {{ username }},</p>
    <br />
    <p>We noticed you haven't logged in today.</p>
    <p>We know that these emails are super spam, but it's part of our assignment to email you every day.</p>
    <p>So log in, or we'll be back (tomorrow).</p>
    <p>Excited to see you soon!!</p>
    <br />
    <p>Best Regards,</p>
    <p>The eLibrary</p>
    <small>Read everyday!</small>
    """)
    
    users = User.query.all()
    for user in users:
        if user.role == 'Student':
            user_dict = user.to_dict()
            today = datetime.today().date()
            has_logged_in_today_query = (
                TokenBlockedList.query
                .filter_by(username=user.username)
                .filter(func.date(TokenBlockedList.create_at) == today)
            )
            has_logged_in_today = db.session.query(has_logged_in_today_query.exists()).scalar() 
            
            if not has_logged_in_today:
                address = user_dict["username"]
                subject = f"Please log in and explore our amazing eBooks collection, {user_dict['username'].capitalize()}!!"
                rendered_template = template.render(username=user_dict["username"])
                send_email(address, subject, rendered_template)
            else:
                print(f"User {user_dict['username']} has logged in today.")
    return 200

# @shared_task(ignore_result=True)
# def send_daily_reminder():
#     template = """
#     <p>
#         Dear {{ username }},
#     </p>
#     <br />
#     <p>
#         We noticed you haven't logged in today.
#     </p>
#     <p>
#         We know that these emails are super spam, but it's part of our assignment to email you every day.
#     </p>
#     <p>
#         So log in, or we'll be back (tomorrow).
#     </p>
#     <p>
#         Excited to see you soon!!
#     </p>
#     <br />
#     <p>
#         Best Regards,
#     </p>
#     <p>
#         The eLibrary
#     </p>
#         <small>Read everyday!</small>
#         """
#     users = User.query.all()
#     template = Template(template)

#     for user in users:
#         if user.role == 'Student':
#             user_dict = user.to_dict()
#             current_date = datetime.today()

#             most_recent_token_entry = (TokenBlockedList.query.filter_by(username=user.username)
#                                        .order_by(TokenBlockedList.create_at.desc()).first())

#             if (most_recent_token_entry) and (TokenBlockedList.query.filter(TokenBlockedList.username==user.username)
#                                               .filter(func.date(most_recent_token_entry.create_at.date() == current_date.date()))): 
#                 print(f"User {user_dict['username']} has logged in today.")
#             else:
#                 address = user_dict["username"]
#                 subject = "Please log in and explore our amazing eBooks collection, " + user_dict["username"].capitalize() + "!!"
#                 rendered_template = template.render(username=user_dict["username"])
#                 send_email(address, subject, rendered_template)
#     return 200

# @shared_task(ignore_result=True)
# def send_daily_reminder():
#     template = """
#     <p>
#         Dear {{ username }},
#     </p>
#     <br />
#     <p>
#         We noticed you haven't logged in today.
#     </p>
#     <p>
#         We know that these emails are super spam, but it's part of our assignment to email you every day.
#     </p>
#     <p>
#         So log in, or we'll be back (tomorrow).
#     </p>
#     <p>
#         Excited to see you soon!!
#     </p>
#     <br />
#     <p>
#         Best Regards,
#     </p>
#     <p>
#         The eLibrary
#     </p>
#         <small>Read everyday!</small>
#         """
#     users = User.query.all()
#     template = Template(template)

#     for user in users:
#         if user.role == 'Student':
#             user_dict = user.to_dict()
#             current_date = datetime.today()

#             most_recent_token_entry = (TokenBlockedList.query.filter_by(username=user.username)
#                                        .order_by(TokenBlockedList.create_at.desc()).first())

#             if (most_recent_token_entry) and (TokenBlockedList.query.filter(TokenBlockedList.username==user.username)
#                                               .filter(func.date(most_recent_token_entry.create_at.date() == current_date.date()))): 
#                 print(f"User {user_dict['username']} has logged in today.")
#             else:
#                 address = user_dict["username"]
#                 subject = "Please log in and explore our amazing eBooks collection, " + user_dict["username"].capitalize() + "!!"
#                 rendered_template = template.render(username=user_dict["username"])
#                 send_email(address, subject, rendered_template)
#     return 200

@shared_task(ignore_result=False)
def send_daily_reminder_issued():
    template = """
    <p>
        Dear {{ username }},
    </p>
    <br />
    <p>
        We noticed you haven't subscribed to any ebooks today.
    </p>
    <p>
        Remember that reading a book daily won't keep a doctor away, but might make you smarter to talk to!
    </p>
    <p>
        We've even added a feature to download ebooks (for credits!).
    </p>
    <p>
        Excited to see you soon.
    </p>
    <br />
    <p>
        Best Regards,
    </p>
    <p>
        The eLibrary
    </p>
        <small>Read everyday!</small>
        """
    users = User.query.all()
    template = Template(template)

    for user in users:
        user_dict = user.to_dict()
        if user_dict["role"] == "Student":
            current_date = datetime.today()
            ebook_today = IssuedBooks.query.filter(IssuedBooks.username==user_dict["username"]).filter(func.date(IssuedBooks.issue_date) == current_date).count()
            if ebook_today == 0:
                address = user_dict["username"]
                subject = "Have you read today, " + user_dict["username"].capitalize() + "?!"
                rendered_template = template.render(username=user_dict["username"])
                send_email(address, subject, rendered_template)
            else:
                print(f"User {user_dict['username']} has been issued a book today.")
    return 200

@shared_task(ignore_result=False)
def send_monthly_report():
    template = """
    <!DOCTYPE html>
    <html lang="en">

    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
    <title>Analytics</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/vue-material-design-icons@5.2.0/styles.min.css">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorigin="anonymous">
            defer
        </script>
    </head>

    <body>
    <div class="container-fluid">
        <div class="row col-md-6 col-lg-8 m-auto m-0">
            <div class="row col-md-6 col-lg-8 m-auto mt-3 px-0 d-inline-flex justify-content-center">
                <div class="col-8 text-center d-flex align-items-end  justify-content-center ">
                    <mdicon name="basket" class="text-center text-primary mx-2" height="50" width="50" />
                    <span class="text-center mx-2" style="font-size:25px">eLibrary Systems</span>
                    <hr>
                </div>
            </div>
            <div class="row gy-4 row-cols-1 row-cols-md-2 row-cols-xl-3">
                <div class="col-md-12 col-xl-12">
                    <div>
                        <div>
                            <div>
                                <p>Dear {{ username }},</p>
                                <p>Thank you for being a patron of the ONLY elibrary on campus!</p>
                            </div>
                        </div>
                        {% if ebooks|length == 0 %}
                        <p>You haven't read and returned any books last month.</p>
                        <p>Log in now to request a book.</p>
                        <br />
                        <p>Best Regards,</p>
                        <p>System officer - eLibrary</p>
                        <small>Read everyday!</small>
                        {% else %}
                        <p>Below you can review your monthly activity report.</p>
                        <p>No. of books returned: <b>{{ ebooks|length }}</b></p>
                        <div class="table-responsive">
                            <table class="table">
                                <thead class="table-success">
                                    <tr>
                                        <th>Book Name</th>
                                        <th>Rating</th>
                                        <th>Return Date</th>
                                    </tr>
                                </thead>
                                {% for book in ebooks %}
                                <tbody>
                                    <tr>
                                        <td>{{ book.book_name }}</td>
                                        <td>{{ book.rating }}</td>
                                        <td>{{ book.return_date }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                        </div>
                        <br />
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>
    </body>

    </html>

    """
    users = User.query.filter_by(role="Student").all()
    template = Template(template)
    for user in users:
        user = user.to_dict()
        ebooks_returned = ReturnedBooks.query.filter_by(username = user["username"]).filter(func.date(ReturnedBooks.return_date) < datetime.now().date() - timedelta(days=30)).all()
        ebook_data = []
        for book in ebooks_returned:
            ebook_dict = {}
            ebook_dict["book_name"] = book.book_name
            ebook_dict["return_date"] = book.return_date.date().isoformat()
            ebook_dict["rating"] = book.avgRating
            # ebook_dict["rating"] = book.rating
            ebook_data.append(ebook_dict)
        SMTP_SERVER_HOST = "localhost"
        SMTP_SERVER_PORT = 1025
        SENDER_ADDRESS = "system@elibrary.com"
        SENDER_PASSWORD = ""
        msg = MIMEMultipart()
        msg["From"] = SENDER_ADDRESS
        msg["To"] = user["username"]+"@elibrary.com"
        msg["Subject"] = "User Monthly Report"
        rendered_template = template.render(username=user["username"], ebooks=ebook_data)
        msg.attach(MIMEText(rendered_template, "html"))

        s = smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT)
        s.login(SENDER_ADDRESS, SENDER_PASSWORD)
        s.send_message(msg)
        s.quit()
    return 200

@shared_task(ignore_result=False)
def send_monthly_activity_report():
    #sending all user - User1: last_logout, books_requested, sections_prefer, books_issued, books_returned, high/low_book/ratings
    template = """
    <!DOCTYPE html>
    <html lang="en">

    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
    <title>User Activity Analytics</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/vue-material-design-icons@5.2.0/styles.min.css">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorigin="anonymous">
            defer
    </script>
    <style>
        .wider-container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .wide-table {
            width: 100%;
        }
    </style>
    </head>

    <body>
    <div class="container-fluid">
        <div class="row col-md-6 col-lg-8 m-auto m-0">
            <div class="row col-md-6 col-lg-8 m-auto mt-3 px-0 d-inline-flex justify-content-center">
                <div class="col-8 text-center d-flex align-items-end  justify-content-center ">
                    <mdicon name="basket" class="text-center text-primary mx-2" height="50" width="50" />
                    <span class="text-center mx-2" style="font-size:25px">eLibrary Systems</span>
                    <hr>
                </div>
            </div>
            <div class="row gy-4 row-cols-1 row-cols-md-2 row-cols-xl-3">
                <div class="col-md-12 col-xl-12">
                    <div>
                        <div>
                            <div>
                                <p>Dear Librarian,</p>
                                <p>Thank you for your continued assistance in bringing quality books to students!</p>
                            </div>
                        </div>
                        {% if user_data|length == 0 %}
                        <p>There are no students registered with the eLibrary currently. 
                        Our teams are working hard to enrol new users.</p>
                        <br />
                        {% else %}
                        <p>We currently have <b>{{ user_data|length }} students</b> registered in our system.</p>
                        <br>
                        <p>Below you can review each student's last month's activity.</p>
                        <div class="container-fluid wider-container"> 
                        <div class="table-responsive">
                            <table class="table wide-table">
                                <thead class="table-success">
                                    <tr>
                                        <th>Username</th>
                                        <th>Last Logout</th>
                                        <th>Books Requested</th>
                                        <th>Most Requested Section</th>
                                        <th>Books Issued</th>
                                        <th>Books Returned</th>
                                        <th>Highest Rated Book, rating</th>
                                        <th>Lowest Rated Book, rating</th>
                                    </tr>
                                </thead>
                                {% for username, data in user_data.items() %}
                                <tr>
                                <td>{{ username }}</td>
                                <td>{{ data.last_logout }}</td>  
                                <td>{{ data.books_requested | join(", ") }}</td>
                                <td>{{ data.sections_prefer|join(", ") }}</td>
                                <td>{{ data.books_issued|join(", ") }}</td>
                                <td>{{ data.books_returned|join(", ") }}</td>
                                <td>{{ data.books_highest|join(", ") }}</td>
                                <td>{{ data.books_lowest|join(", ") }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </div>
                        </div>
                        <br />
                        <p>Best Regards,</p>
                        <p>System officer - eLibrary</p>
                        <small>Read everyday!</small>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>
    </body>

    </html>

    """ 
    
    studentUsers = User.query.filter_by(role="Student").all()
    template = Template(template)
    user_data = {}
    for user in studentUsers:
        user_data[user.username] = {
            "last_logout": "Never logged in",
            "books_requested": ["NA"],
            "sections_prefer": ["NA"],
            "books_issued": ["NA"],
            "books_returned": ["NA"],
            "books_highest": ["NA"],
            "books_lowest": ["NA"]
        }
        most_recent_token_entry = (TokenBlockedList.query.filter_by(username=user.username)
                                   .order_by(TokenBlockedList.create_at.desc()).first())
        if most_recent_token_entry:
            user_data[user.username]["last_logout"] = most_recent_token_entry.create_at.date()
        
        books_requested = RequestedBooks.query.filter_by(student_username = user.username).all()
        book_requests=[]
        section_requests=[]
        for book_ids in books_requested:
            # books=[]
            # books.append(Book.query.filter_by(b_id = book_ids.book_id).first().book_name)
            book_requests.append(Book.query.filter_by(b_id = book_ids.book_id).first().book_name)
            
            # sections=[]
            section_id = Book.query.filter_by(b_id = book_ids.book_id).first().sectionID_link
            # sections.append(Section.query.filter_by(s_id = section_id).first().name)
            section_requests.append(Section.query.filter_by(s_id = section_id).first().name)
            
            # book_requests.append(books)
            # section_requests.append(sections)
        
        if len(book_requests) > 0:
            user_data[user.username]["books_requested"] = book_requests
        else:
            user_data[user.username]["books_requested"] = ['NA']
        if len(section_requests) > 0:
            user_data[user.username]["sections_prefer"] = section_requests
        else:
            user_data[user.username]["sections_prefer"] = ['NA']
        # user_data[user.username]["sections_prefer"] = section_requests

        books_iss = IssuedBooks.query.filter_by(username = user.username).all()
        books_issued=[]
        for book_names in books_iss:
            books_issued.append(book_names.book_name)
        # user_data[user.username]["books_issued"] = books_issued
        if len(books_issued) > 0:
            user_data[user.username]["books_issued"] = books_issued
        else:
            user_data[user.username]["books_issued"] = ['NA']
        
        books_ret = ReturnedBooks.query.filter_by(username = user.username).all()
        books_returned = []
        highest, lowest = {}, {}
        high_rat = -1
        low_rat = 6
        for book_ret in books_ret:
            if book_ret.rating > high_rat:
                highest[book_ret.book_name] = book_ret.rating
                high_rat = book_ret.rating
            
            if book_ret.rating < low_rat:
                lowest[book_ret.book_name] = book_ret.rating
                low_rat = book_ret.rating
            
            books_returned.append(book_ret.book_name)

        if len(books_returned) > 0:
            user_data[user.username]["books_returned"] = books_returned
        else:
            user_data[user.username]["books_returned"] = ['NA']
        for k,v in highest.items():
            user_data[user.username]["books_highest"] = [k +': ' + str(v)]
        for k,v in lowest.items():
            user_data[user.username]["books_lowest"] = [k +': ' + str(v)]
        
    rendered_template = template.render(user_data=user_data)
    # rendered_template = template.render(username=user_dict["username"])
    # rendered_template = render_template_string(template, studentUsers=studentUsers, user_data=user_data)
    SMTP_SERVER_HOST = "localhost"
    SMTP_SERVER_PORT = 1025
    SENDER_ADDRESS = "system@elibrary.com"
    SENDER_PASSWORD = ""
    msg = MIMEMultipart()
    msg["From"] = SENDER_ADDRESS
    msg["To"] = "librarian@elibrary.com"
    msg["Subject"] = "User Monthly Activity Report"
    msg.attach(MIMEText(rendered_template, "html"))

    s = smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT)
    s.login(SENDER_ADDRESS, SENDER_PASSWORD)
    s.send_message(msg)
    s.quit()

    return 200

#====================END OF FILE====================#