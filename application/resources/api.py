import requests
from datetime import timedelta
import math
from flask_restful import Resource, Api
from datetime import datetime, date
from flask import make_response, jsonify, Blueprint, request, abort, session
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt
from ..models import db, Section, Book, User, RequestedBooks, IssuedBooks, ReturnedBooks
from ..instances import cache

# Caching - @cache.cached(timeout=50), cache.clear() <---- Implemented only in Sections. 

#-----------------------LIBRARIAN/GRAPHS API-----------------------#

reports_bp = Blueprint(
    'reports',
    __name__
)

@reports_bp.get("/usergraphs")
@jwt_required()
def user_graphs():
    claims = get_jwt()
    user = claims["sub"] #"<username>"
    returns = ReturnedBooks.query.filter_by(username = user).all() 
    userReturns = []
    for ret in returns:
        userRet = {}
        userRet["book_name"] = ret.book_name
        userRet["rating"] = ret.rating
        sectionID = Book.query.filter_by(book_name = ret.book_name).first().sectionID_link
        userRet["section_name"] = Section.query.filter_by(s_id = sectionID).first().name
        userReturns.append(userRet)
    return userReturns #book_name, rating, (section_name)


@reports_bp.get("/graphs")
@jwt_required()
def graphs():
    claims = get_jwt()
    if claims.get('is_staff') == True:
        books = Book.query.all()
        ebooks = [] # [{book1, section1, 2.5}, {book2, section2, 5.00} ...]
        for book in books:
            ebook = {}
            ebook["book_name"] = book.book_name
            ebook["avgRating"] = book.hybRating
            ebook["section_name"] = Section.query.filter_by(s_id = book.sectionID_link).first().name
            ebooks.append(ebook)
        
        users = User.query.filter(User.role=="Student").all()
        userReturns = [] # [{user1, book1, section1, 4.00, 2024-04-10}, ...]
        for user in users:
            retBooks = ReturnedBooks.query.all()
            for ret in retBooks:
                if ret.username == user.username:
                    userRet = {}
                    userRet["username"] = user.username
                    userRet["book_name"] = ret.book_name
                    section_id = Book.query.filter_by(book_name = ret.book_name).first().sectionID_link
                    userRet["section_name"] = Section.query.filter_by(s_id = section_id).first().name
                    userRet["rating"] = ret.rating
                    userRet["return_date"] = ret.return_date.date().isoformat()
                    userReturns.append(userRet)

        userRequests = [] # [{user1, book1, section1, status}, ...]
        for user in users:
            reqBooks = RequestedBooks.query.all()
            for req in reqBooks:
                if req.student_username == user.username:
                    userReq = {}
                    userReq["username"] = user.username
                    userReq["book_name"] = Book.query.filter_by(b_id = req.book_id).first().book_name
                    section_id = Book.query.filter_by(book_name = userReq["book_name"]).first().sectionID_link
                    userReq["section_name"] = Section.query.filter_by(s_id = section_id).first().name
                    userReq["status"] = req.status
                    userRequests.append(userReq)

        userIssues = [] # [{user1, book1, section1, 2024-04-10, daysLeft}, ...]
        for user in users:
            issBooks = IssuedBooks.query.all()
            for iss in issBooks:
                if iss.username == user.username:
                    userIss = {}
                    userIss["username"] = user.username
                    userIss["book_name"] = iss.book_name
                    section_id = Book.query.filter_by(book_name = iss.book_name).first().sectionID_link
                    userIss["section_name"] = Section.query.filter_by(s_id = section_id).first().name
                    userIss["issue_date"] = iss.issue_date.date().isoformat()
                    userIss["daysLeft"] = iss.daysLeft
                    userIssues.append(userIss)

        graph_data = []
        graph_data.append(ebooks)
        graph_data.append(userReturns)
        graph_data.append(userRequests)
        graph_data.append(userIssues)
        graph_data.append([user.to_dict() for user in users])
        return graph_data

    else:
        return jsonify({"message":"User not authorized"}), 401


@reports_bp.get("/monthly_activity")
@jwt_required()
def monthly_graphs():
    # claims = get_jwt()
    # if claims.get('is_staff') == True:
    books = Book.query.all()
    ebooks = [] # [{book1, section1, 2.5}, {book2, section2, 5.00} ...]
    for book in books:
        ebook = {}
        ebook["book_name"] = book.book_name
        ebook["avgRating"] = book.hybRating
        ebook["section_name"] = Section.query.filter_by(s_id = book.sectionID_link).first().name
        ebooks.append(ebook)
    
    users = User.query.filter(User.role=="Student").all()
    userReturns = [] # [{user1, book1, section1, 4.00, 2024-04-10}, ...]
    for user in users:
        retBooks = ReturnedBooks.query.all()
        for ret in retBooks:
            if ret.username == user.username:
                userRet = {}
                userRet["username"] = user.username
                userRet["book_name"] = ret.book_name
                section_id = Book.query.filter_by(book_name = ret.book_name).first().sectionID_link
                userRet["section_name"] = Section.query.filter_by(s_id = section_id).first().name
                userRet["rating"] = ret.rating
                userRet["return_date"] = ret.return_date.date().isoformat()
                userReturns.append(userRet)

    userRequests = [] # [{user1, book1, section1, status}, ...]
    for user in users:
        reqBooks = RequestedBooks.query.all()
        for req in reqBooks:
            if req.student_username == user.username:
                userReq = {}
                userReq["username"] = user.username
                userReq["book_name"] = Book.query.filter_by(b_id = req.book_id).first().book_name
                section_id = Book.query.filter_by(book_name = userReq["book_name"]).first().sectionID_link
                userReq["section_name"] = Section.query.filter_by(s_id = section_id).first().name
                userReq["status"] = req.status
                userRequests.append(userReq)

    userIssues = [] # [{user1, book1, section1, 2024-04-10, daysLeft}, ...]
    for user in users:
        issBooks = IssuedBooks.query.all()
        for iss in issBooks:
            if iss.username == user.username:
                userIss = {}
                userIss["username"] = user.username
                userIss["book_name"] = iss.book_name
                section_id = Book.query.filter_by(book_name = iss.book_name).first().sectionID_link
                userIss["section_name"] = Section.query.filter_by(s_id = section_id).first().name
                userIss["issue_date"] = iss.issue_date.date().isoformat()
                userIss["daysLeft"] = iss.daysLeft
                userIssues.append(userIss)

    student_users = User.query.filter_by(role="Student").all()

    user_data = {}
    for user in student_users:
        user_data[user.username] = {
            "requested_books": [],
            "requested_sections": set(),
            "issued_books": [],
            "highest_rated_book": None,
            "highest_rating": 0,
            "lowest_rated_book": None,
            "lowest_rating": float('inf')  # Start with a very high value for comparison
        }

    for item in userReturns:
        user_name = item["username"]
        book_name = item["book_name"]
        section_name = item["section_name"]
        rating = item["rating"]

        # Update user_data with return information
        user_data[user_name]["returned_books"].append(book_name)

        if rating > user_data[user_name]["highest_rating"]:
            user_data[user_name]["highest_rated_book"] = book_name
            user_data[user_name]["highest_rating"] = rating

        if rating < user_data[user_name]["lowest_rating"]:
            user_data[user_name]["lowest_rated_book"] = book_name
            user_data[user_name]["lowest_rating"] = rating

    for item in userRequests:
        user_name = item["username"]
        book_name = item["book_name"]
        section_name = item["section_name"]
        status = item["status"]
        
        # Update user_data with request information
        if status in ['pending', 'requested', 'approved']:
            user_data[user_name]["requested_books"].append(book_name)
            user_data[user_name]["requested_sections"].add(section_name)

    for item in userIssues:
        user_name = item["username"]
        book_name = item["book_name"]
        issue_date_str = item["issue_date"]
        issue_date = datetime.fromisoformat(issue_date_str)
        days_left = item["daysLeft"]
        one_month_ago = datetime.now() - timedelta(days=30)

        # Update user_data with issue information if it's within the last month
        if issue_date >= one_month_ago and days_left == 0: 
            user_data[user_name]["issued_books"].append(book_name)

    return jsonify(user_data)
    # else:
    #     return jsonify({"message":"User not authorized"}), 401

# @reports_bp.post('/sendReport')
# @jwt_required()
# def send_Librarian_report():
#     username = request.json.get("username")
#     user = User.query.filter_by(username=username).first()
#     if not user:
#         return jsonify({"message":"User not found."}), 404
#     task = tasks.send_csv_report.delay(username)
#     return jsonify({"taskid": task.id}), 200

#-----------------------SEARCH API-----------------------#

search_bp = Blueprint(
    'search',
    __name__
)

@search_bp.route('/search', methods=['GET','POST'])
@jwt_required()
def search():
    if request.method == 'POST':
        args = request.get_json()
        searched_item = args["item"]
        if len(searched_item) == "":
            return jsonify({"message":"Cannot search for an empty string."}), 204
        sections = Section.query.order_by(Section.s_id.desc()).all()
        books = Book.query.order_by(Book.b_id.desc()).all()
        searched_section, searched_book = [], []
        for s in sections:
            if (searched_item in s.name) or (searched_item in s.description):
                searched_section.append(s)
        for b in books:
            if (searched_item in b.book_name) or (searched_item in b.authors):
                searched_book.append(b)
        if len(searched_section) > 0:
            data = [section.to_dict() for section in searched_section]
            session['search_results'] = data
            return make_response(data, 200)
        elif len(searched_book) > 0:
            data = [book.to_dict() for book in searched_book]
            session['search_results'] = data
            return make_response(data, 200)
        else:
            return jsonify({"message":"Searched item not available in database."}), 204
    
    elif request.method == 'GET':
        search_results = session.get('search_results')
        if search_results:
            return jsonify(search_results), 200
        else:
            return jsonify({"message": "No search results available."}), 204
        
    return jsonify({"message": "Method not allowed"}), 405

#-----------------------SECTIONS API-----------------------#

sections_bp = Blueprint(
    'sections',
    __name__
)

@sections_bp.get('/sections')
@jwt_required()
# @cache.cached(timeout=50)
def get_sections():
    sections = Section.query.order_by(Section.s_id.desc()).all()
    data = [section.to_dict() for section in sections]
    return make_response(data, 200)

@sections_bp.post('/sections')
@jwt_required()
def post_sections():
    claims = get_jwt()
    if claims.get('is_staff') == True:
        args = request.get_json()
        name = args.get("name", None)
        description = args.get("description", None)
        if name:
            ex_name = Section.query.filter_by(name=args['name']).first()
            if (len(args['name']) == 0):
                return jsonify({"message":"Section name cannot be empty."}), 404
            elif ex_name:
                return jsonify({"message":"Section with this name exists in the database. Choose another name."}), 409
        else:
            return jsonify({"message":"Section name is a mandatory field."}), 404
        if description:
            if (len(args['description']) == 0):
                return jsonify({"message":"Section description cannot be empty."}), 404
        else:
            return jsonify({"message":"Section description is a mandatory field."}), 404
        new_section = Section(
            name = args['name'],
            description = args['description'],
            date_created = datetime.now()
        )
        db.session.add(new_section)
        db.session.commit()
        # cache.clear()
        return make_response(new_section.to_dict(), 201)
    else:
        return jsonify({"message":"User not authorized"}), 401
    
@sections_bp.patch('/edit_sections/<int:id>')
@jwt_required()
def patch_sections(id):
    claims = get_jwt()
    if claims.get('is_staff') == True:
        args = request.get_json()
        edit_section = Section.query.filter_by(s_id=id).first()
        if not edit_section:
            return jsonify({"message":"Section with this ID does not exist."}), 404
        else:
            updated = False
            name = args.get("name")
            date_created = args.get("date_created", None)
            description = args.get("description")
            if name and (name != edit_section.name):
                    sname = Section.query.filter_by(name = args['name']).first()
                    if sname:
                        return jsonify({"message":"Section with this name exists in the database. Name must be unique."}), 204
                    else:
                        if len(name) > 0:
                            edit_section.name = args['name']
                            updated = True
                        else:
                            return jsonify({"message":"Section name cannot be empty."}), 400
            if date_created is not None:
                return jsonify({"message":"Date created cannot be edited."}), 404
            if description and (description != edit_section.description):
                if len(description) > 0:
                    edit_section.description = args['description']
                    updated = True
                else:
                    return jsonify({"message":"Section description cannot be empty."}), 404
            if updated:
                db.session.commit()
                # cache.clear()
                return jsonify({"message": "Section updated successfully."}), 200
            else:
                return jsonify({"message": "No updates were made. Please provide new values."}), 204
    else:
        return jsonify({"message":"User not authorized"}), 401

@sections_bp.delete('/edit_sections/<int:id>')
@jwt_required()
def delete_section(id):
    claims = get_jwt()
    if claims.get('is_staff') == True:
        delete_section = Section.query.filter_by(s_id=id).first()
        if not delete_section:
            return jsonify({"message":"Section with this ID does not exist."}), 404
        books = Book.query.filter_by(sectionID_link = id).all()
        for book in books:
            #Changes to correct Librarian > Delete Section
            req = RequestedBooks.query.filter_by(book_id=book.b_id).all()
            for r in req:
                db.session.delete(r)   
            iss = IssuedBooks.query.filter_by(book_name=book.book_name).all()
            for i in iss:
                db.session.delete(i)   
            #Done 
            db.session.delete(book)
        db.session.delete(delete_section)
        db.session.commit()
        # cache.clear()
        return jsonify({"message":"Section deleted."}), 200
    else:
        return jsonify({"message":"User not authorized"}), 401

@sections_bp.get('/sections/<int:id>/books')
@jwt_required()
def section_books(id):
    claims = get_jwt()
    if claims.get('is_staff') == True:
        sectionID = Section.query.filter_by(s_id=id).first()
        if sectionID:
            # books = Book.query.order_by(Book.b_id.desc()).all()
            books = Book.query.filter_by(sectionID_link = id)
            # ordered_books = books.query.order_by(books.b_id.desc()).all()
            data = [book.to_dict() for book in books]
            # data = [book.to_dict() for book in ordered_books]
            return make_response(data, 200)
        return jsonify({"message":"Section with this ID does not exist"}), 404   
    return jsonify({"message":"User not authorized"}), 401

@sections_bp.get('/sectionsBooks/<int:id>')
@jwt_required()
def get_section_books(id):
    books = Book.query.filter_by(sectionID_link=id).all()
    return make_response([book.to_dict() for book in books], 200)


# @sections_bp.get('/sectionsBooks/<int:id>')
# @jwt_required()
# def sectionsBooks(id):
#     # claims = get_jwt()
#     # if claims.get('is_staff') == True:
#     sectionID = Section.query.filter_by(s_id=id).first()
#     if sectionID:
#         books = Book.query.filter_by(sectionID_link = id)
#         data = [book.to_dict() for book in books]
#         return make_response(data, 200)
#     return jsonify({"message":"Section with this ID does not exist"}), 404   
#     # return jsonify({"message":"User not authorized"}), 401
    
#-----------------------BOOKS API-----------------------#

books_bp = Blueprint(
    'books',
    __name__
)

@books_bp.get('/books')
# @jwt_required()
def get_books():
    books = Book.query.order_by(Book.b_id.desc()).all()
    books_data = []
    for book in books:
        genre = Section.query.filter_by(s_id = book.sectionID_link).first()
        book_dict = {
            'b_id': book.b_id,
            'book_name': book.book_name,
            'content': book.content,
            'authors': book.authors,
            'avgRating': book.hybRating,
            "SectionName":genre.name,
            'requests': [{
                'request_id': request.request_id,
                'student_username': request.student_username,
                'book_id': request.book_id,
                'status': request.status,
                'approved': request.approved
            } for request in book.requests],
            'issues': [{
                'issue_id': issue.issue_id,
                'username': issue.username,
                'book_name': issue.book_name,
                'issue_date': issue.issue_date,
                'daysLeft': issue.daysLeft
            } for issue in book.issues],
            'returns': [{
                'return_id': rturn.return_id,
                'issue_ID': rturn.issue_ID,
                'return_date': rturn.return_date,
                'book_name': rturn.book_name,
                'username': rturn.username,
                'rating': rturn.rating,
            } for rturn in book.returns]
        }
        books_data.append(book_dict)
    return make_response(books_data, 200)

@books_bp.post('/books') 
@jwt_required()
def post_books():
    claims = get_jwt()
    if claims.get('is_staff') == True:
        args = request.get_json()
        book_name = args.get("book_name", None)
        content = args.get("content", None)
        authors = args.get("authors", None)
        sectionID_link = args.get("sectionID_link", None)       
        if book_name:
            name = Book.query.filter_by(book_name=args['book_name']).first()
            if name:
                return jsonify({"message":"Book with this name already exists in database. Name must be unique"}), 409
            elif len(args['book_name']) == 0:
                return jsonify({"message":"book_name cannot be an empty string."}), 404
        else:
            return jsonify({"message":"book_name is required."}), 404
        if content:
            if len(args['content']) == 0:
                return jsonify({"message":"content cannot be an empty string."}), 404
        else:
            return jsonify({"message":"content is required."}), 404
        if authors:
            if len(args['authors']) == 0:
                return jsonify({"message":"authors cannot be an empty string."}), 404
        else:
            return jsonify({"message":"authors are required."}), 404
        if sectionID_link:
            sectionID = Section.query.filter_by(s_id = args["sectionID_link"]).first()
            if not sectionID:
                return jsonify({"message":"Section with this ID does not exist."}), 404
        else:
            return jsonify({"message":"sectionID_link is required."}), 404
        new_book = Book(
            book_name = args['book_name'],
            content = args['content'],
            authors = args['authors'],
            sectionID_link = args['sectionID_link']
        )
        db.session.add(new_book)
        db.session.commit()
        return make_response(new_book.to_dict(), 201)
    else:
        return jsonify({"message":"User not authorized"}), 401

@books_bp.patch('/edit_books/<int:id>')
@jwt_required()
def patch_books(id):
    claims = get_jwt()
    if claims.get('is_staff') == True:
        args = request.get_json()
        edit_book = Book.query.filter_by(b_id=id).first()
        if not edit_book:
            return jsonify({"message":"Book with this ID does not exist."}), 404
        else:
            updated = False
            book_name = args.get("book_name")
            content = args.get("content")
            authors = args.get("authors")
            sectionID_link = args.get("sectionID_link")
            avgRating = args.get("avgRating")
            if book_name and (book_name != edit_book.book_name):
                existing = Book.query.filter_by(book_name = book_name).first()
                if existing:
                    return jsonify({"message":"This name exists for another book. Book name must be unique."}), 409
                if len(book_name) > 0:
                    edit_book.book_name = book_name
                    updated = True
                else:
                    return jsonify({"message":"Book name cannot be empty."}), 400
            if content and content != edit_book.content:
                if len(content) > 0:
                    edit_book.content = content
                    updated = True
                else:
                    return jsonify({"message":"Book content cannot be empty."}), 400
            if authors and authors != edit_book.authors:
                if len(authors) > 0:
                    edit_book.authors = authors
                    updated = True
                else:
                    return jsonify({"message":"Book authors must be specified."}), 400
            if sectionID_link and sectionID_link != edit_book.sectionID_link:
                sectionID = Section.query.filter_by(s_id = args["sectionID_link"]).first()
                if not sectionID:
                    return jsonify({"message":"Section with this ID does not exist."}), 404
                if len(sectionID_link) > 0:
                    edit_book.sectionID_link = sectionID_link
                    updated = True
                else:
                    return jsonify({"message":"Book sectionID must be specified."}), 400
            if avgRating:
                return jsonify({"message":"Cannot edit average rating. It is calculated based on past ratings by students."}), 404
            if updated:
                db.session.commit()
                return jsonify({"message": "Book updated successfully."}), 200
            else:
                return jsonify({"message": "No updates were made. Please provide new values."}), 204
    else:
        return jsonify({"message":"User not authorized"}), 401
    
@books_bp.delete('/edit_books/<int:id>')
@jwt_required()
def delete_book(id):
    claims = get_jwt()
    if claims.get('is_staff') == True:
        delete_book = Book.query.filter_by(b_id = id).first()
        if not delete_book:
            return jsonify({"message":"Book with this ID does not exist."}), 404
        delete_request = RequestedBooks.query.filter_by(book_id = id).first()
        if delete_request:
            db.session.delete(delete_request)
            db.session.commit()
        delete_issue = IssuedBooks.query.filter_by(book_name = delete_book.book_name).first()
        if delete_issue:
            db.session.delete(delete_issue)
            db.session.commit()
        db.session.delete(delete_book)
        db.session.commit()
        return jsonify({"message":"Book, any user requests and any issues of this book are deleted."}), 200
    else:
        return jsonify({"message":"User not authorized"}), 401

#-----------------------User API-----------------------#

users_bp = Blueprint(
    'users',
    __name__
)

@users_bp.get('/userbooks')
@jwt_required()
def user_books():
    claims = get_jwt()
    username = claims["sub"]
    user_requests = len(RequestedBooks.query.filter_by(student_username = username).all())
    user_issued = len(IssuedBooks.query.filter_by(username = username).all())
    user_returned = len(ReturnedBooks.query.filter_by(username = username).all())
    
    return jsonify(
            {
                "message":"Books requested, issued and returned for current user.",
                "username" : username,
                "books_requested" : user_requests,
                "books_issued" : user_issued,
                "books_returned" : user_returned
            }
        ), 200

@users_bp.get('/userdetails/<uname>')
@jwt_required()
def user_details(uname):
    claims = get_jwt()
    if claims.get("sub") == uname:
        user = User.query.filter_by(username=uname).first()
        if not user:
            return jsonify({"message":"User with this username does not exist."}), 404
        else:
            return jsonify({
                "username" : uname,
                "fav_genre": user.fav_genre,
                "fav_book": user.fav_book,
                "fav_author": user.fav_author,
            }), 200
    else:
        return jsonify({"message":"Username does not match with logged in user."}), 404

@users_bp.patch('/editUser/<uname>')
@jwt_required()
def edit_user_details(uname):
    claims = get_jwt()
    if claims.get("sub") == uname:
        user = User.query.filter_by(username=uname).first()
        if not user:
            return jsonify({"message":"User with this username does not exist."}), 404
        else:
            args = request.get_json()
            fav_genre = args.get("fav_genre", None)
            fav_book = args.get("fav_book", None)
            fav_author = args.get("fav_author", None)
            up = False

            if fav_genre and (fav_genre != user.fav_genre):
                if len(fav_genre) > 0:
                    user.fav_genre = fav_genre
                    up = True
                else:
                    return jsonify({"message":"Your favorite genre cannot be an empty string."}), 404
            
            if fav_book and (fav_book != user.fav_book):
                if len(fav_book) > 0:
                    user.fav_book = fav_book
                    up = True
                else:
                    return jsonify({"message":"Your favorite book cannot be an empty string."}), 404
            
            if fav_author and (fav_author != user.fav_author):
                if len(fav_author) > 0:
                    user.fav_author = fav_author
                    up = True
                else:
                    return jsonify({"message":"Your favorite author's name cannot be an empty string."}), 404
            if up:
                db.session.commit()
                return make_response(user.to_dict(), 201)
            else:
                return jsonify({"message":"No updates were made. Please provide new values."}), 404
            
    else:
        return jsonify({"message":"Username does not match with logged in user!"}), 404


@users_bp.get('/users')
@jwt_required()
def get_users():
    claims = get_jwt()
    if claims.get('is_staff') == True:
        users = User.query.all()
        data = [user.to_dict() for user in users]
        return make_response(data, 200)
    return jsonify({"message":"User not authorized"}), 401

@users_bp.post('/users')
@jwt_required()
def post_users():
    claims = get_jwt()
    if claims.get('is_staff') == True:
        args = request.get_json()
        username = args.get("username", None)
        password = args.get("password", None)
        fav_genre = args.get("fav_genre", None)
        fav_book = args.get("fav_book", None)
        fav_author = args.get("fav_author", None)

        if username:
            if User.query.filter_by(username=args['username']).first():
                return jsonify({"message":"This username exists in the database. Choose another."}), 409
            elif len(args['username']) == 0:
                return jsonify({"message":"username cannot be an empty string."}), 404
        else:
            return jsonify({"message":"username is required."}), 404
        if password:
            if len(args['password']) == 0:
                return jsonify({"message":"password cannot be an empty string."}), 404
        else:
            return jsonify({"message":"password is required."}), 404
        
        if fav_genre:
            if len(args['fav_genre']) == 0:
                return jsonify({"message":"Your favorite genre cannot be an empty string."}), 404
        else:
            return jsonify({"message":"Please enter your favorite genre."}), 404
        
        if fav_book:
            if len(args['fav_book']) == 0:
                return jsonify({"message":"Your favorite book cannot be an empty string."}), 404
        else:
            return jsonify({"message":"Please enter your favorite book."}), 404
        
        if fav_author:
            if len(args['fav_author']) == 0:
                return jsonify({"message":"Your favorite author's name cannot be an empty string."}), 404
        else:
            return jsonify({"message":"Please enter your favorite author's name."}), 404
        
        new_user = User(
            username = args['username'],
            password = generate_password_hash(args['password']),
            role = "Student",
            fav_genre = args['fav_genre'],
            fav_book = args.get['fav_book'],
            fav_author = args.get['fav_author']
        )
        db.session.add(new_user)
        db.session.commit()
        return make_response(new_user.to_dict(), 201)
    else:
        return jsonify({"message":"User not authorized"}), 401
    
@users_bp.patch('/edit_users/<int:id>')
@jwt_required()
def patch_users(id):
    if id == 1:
        return jsonify({"message":"Cannot edit user with this ID."}), 404
    claims = get_jwt()
    if claims.get('is_staff') == True:
        args = request.get_json()
        edit_user = User.query.filter_by(id=id).first()
        if not edit_user:
            return jsonify({"message":"User with this ID does not exist."}), 404
        else:
            updated = False
            username = args.get("username", None)
            password = args.get("password", None)
            role = args.get("role", None)
            if username:
                    uname = User.query.filter_by(username = args['username']).first()
                    if uname:
                        return jsonify({"message":"User with this username exists in the database. Username must be unique."}), 404
                    elif username == edit_user.username:
                        return jsonify({"message":"Username is same as suggested edit. Consider alternative username."}), 409
                    else:
                        updated = True
                        edit_user.username = args['username']
            if password:
                    if len(args['password']) > 0:
                        updated = True
                        edit_user.password = generate_password_hash(args['password'])
                    else:
                        return jsonify({"message":"User password is required and must atleast be a character."}), 404
            if role:
                updated = True
                edit_user.role = "Student"
            if updated:
                db.session.commit()
                return make_response(edit_user.to_dict(), 201)
            else:
               return jsonify({"message": "No updates were made. Please provide new values."}), 204 
    else:
        return jsonify({"message":"User not authorized"}), 401

@users_bp.delete('/edit_users/<int:id>')
@jwt_required()
def delete_users(id):
    if id == 1:
        return jsonify({"message":"Cannot delete user with this ID."}), 404
    claims = get_jwt()
    if claims.get('is_staff') == True:
        delete_user = User.query.filter_by(id = id).first()
        if not delete_user:
            return jsonify({"message":"User with this ID does not exist."}), 404
        db.session.delete(delete_user)
        db.session.commit()
        return jsonify({"message":"User deleted."}), 200
    else:
        return jsonify({"message":"User not authorized"}), 401
    
#-----------------------RequestedBooks API-----------------------#

requestedBooks_bp = Blueprint(
    'requestedbooks',
    __name__
)

@requestedBooks_bp.get('/requestedbooks')
@jwt_required()
# @cache.cached(timeout=50)
def get_requestedbooks():
    requestedBks = RequestedBooks.query.all()
    data = [requestBk.to_dict() for requestBk in requestedBks]
    return make_response(data, 200)

@requestedBooks_bp.post('/requestedbooks')
@jwt_required()
def post_requestedbooks():
    args = request.get_json()
    approved = args.get("approved", None)
    requested = RequestedBooks.query.all()
    if (args['student_username']) and (len(args['student_username']) > 0):
        check_name = User.query.filter_by(username = args['student_username']).first()
        if not check_name:
            return jsonify({"message":"Username must exist in the database."}), 409
        current_student_request = len(RequestedBooks.query.filter_by(student_username = args['student_username']).all())
        if current_student_request >= 5:
            return jsonify({"message":"Current student has already requested 5 ebooks. Please return an ebook to request for more."}), 403
    else:
        return jsonify({"message":"Username field cannot be empty."}), 404                                                                         
    if args['book_id'] and (len(str(args['book_id'])) > 0):
        id = Book.query.filter_by(b_id = args['book_id']).first()
        if not id:
            return jsonify({"message":"Book with this id not in database."}), 409
    else:
        return jsonify({"message":"Book id is required."}), 404
    if args['approved'] == True:
        bID = Book.query.filter_by(b_id = args["book_id"]).first()
        requested_book_name = bID.book_name
        issued = IssuedBooks.query.all()
        for issue in issued:
            if (issue.book_name == requested_book_name) and (issue.username == args["student_username"]):
                requested = RequestedBooks.query.all()
                for already_requested in requested:
                    if ((already_requested.approved == bool(False)) and 
                        (already_requested.student_username == args['student_username']) and 
                        (already_requested.book_id == args['book_id'])):
                        return jsonify({"message": "Duplicate : Entry already exists in requested table as approval denied."}), 409
                return jsonify({"message": "User has a copy of this book in My Books."}), 409
        date_header = request.headers.get('date')
        new_issue = IssuedBooks(
            username = args['student_username'],
            book_name = requested_book_name,
            issue_date = date_header,
            # daysLeft = 1
            daysLeft = 7
        )
        db.session.add(new_issue)
        db.session.commit()
        for r in requested:
            if ((r.student_username == args['student_username']) and 
                (r.book_id == args['book_id']) and (r.approved == bool(False))):
                db.session.delete(r)
                db.session.commit()
        return jsonify({"message": "Book request updated successfully and added to issued books table."}), 200
    else: #args['approved'] = False
        #Check for entry duplication
        requested = RequestedBooks.query.all()
        for r in requested:
            if ((r.student_username == args['student_username']) and 
                (r.book_id == args['book_id']) and (r.approved == bool(False)) and (r.status == args['status'])):
                return jsonify({"message":"This entry already exists in the database. Recheck details."}), 409
        new_requested_book = RequestedBooks(
                                student_username = args['student_username'], 
                                book_id = args['book_id'],
                                status = "requested", 
                                approved = bool(False))
        db.session.add(new_requested_book)
        db.session.commit()
        return jsonify({
                        'request_id': new_requested_book.request_id,
                        'student_username': new_requested_book.student_username,
                        'book_id': new_requested_book.book_id,
                        'status': new_requested_book.status,
                        'approved': new_requested_book.approved
                        }), 201
    
@requestedBooks_bp.patch('/edit_requestedbooks/<int:id>')
@jwt_required()
def patch_requestedbooks(id): #student_username, book_id, status, approved
    claims = get_jwt()
    if claims.get('is_staff') == True:
        args = request.get_json()
        edit_requestbook = RequestedBooks.query.filter_by(request_id = id).first()
        if not edit_requestbook:
            return jsonify({"message":"Book request with this ID does not exist."}), 404
        else:
            updated = False
            student_username = args.get("student_username")
            book_id = args.get("book_id")
            status = args.get("status") #approved, declined
            if student_username and (student_username != edit_requestbook.student_username):
                check_name = User.query.filter_by(username = args["student_username"]).first()
                if not check_name:
                    return jsonify({"message":"Username does not exist."}), 404
                if len(student_username) > 0:
                    current_student_request = len(RequestedBooks.query.filter_by(student_username = args['student_username']).all())
                    if current_student_request >= 5:
                        return jsonify({"message":"Current student has already requested 5 ebooks. Please return an ebook to request for more."}), 403
                    edit_requestbook.student_username = student_username
                    updated = True
                else:
                    return jsonify({"message":"Student username cannot be empty."}), 400
            if book_id and (book_id != edit_requestbook.book_id):
                bk_id = Book.query.filter_by(b_id = args["book_id"]).first()
                if not bk_id:
                    return jsonify({"message":"Book with this ID does not exist."}), 404
                #Book_id cannot be empty, else above 404 will invoke
                edit_requestbook.book_id = book_id
                updated = True
            if status and (status != edit_requestbook.status): #status was requested earlier, now approved/denied
                if len(status) > 0:
                    if status == "approved":
                        approved = True
                        updated = True
                    elif status == "declined":
                        approved = False
                        updated = True
                    else:
                        pass
                else:
                    # updated = False
                    return jsonify({"message":"Status cannot be an empty string."}), 400
            if updated:
                # if args.get("approved") == True:
                if approved == True:
                    #Check if book is already issued and....
                    bID = Book.query.filter_by(b_id = edit_requestbook.book_id).first()
                    requested_book_name = bID.book_name
                    issued = IssuedBooks.query.all()
                    for issue in issued: #This is not possible, if bk is issued already, it cannot be in req table
                        if (issue.book_name == requested_book_name) and (issue.username == edit_requestbook.student_username):
                            #Book is issued and not approved
                            db.session.delete(edit_requestbook)
                            db.session.commit()
                            return jsonify({"message": "User has a copy of this book in My Books."}), 204
                    #Book is not issued. Need to remove from RequestedBooks and add to IssuedBooks
                    date_header = request.headers.get('date')
                    new_issue = IssuedBooks(
                        username = student_username,
                        book_name = requested_book_name,
                        issue_date = date_header,
                        # daysLeft = 1
                        daysLeft = 7
                    )
                    db.session.delete(edit_requestbook)
                    db.session.commit()
                    db.session.add(new_issue)
                    db.session.commit()
                    return jsonify({"message": "Book request updated successfully. Book added to issued books table."}), 200
                else:
                    #Book request "declined" by Librarian
                    edit_requestbook.status = "declined" #Shouldn't be needed!
                    db.session.delete(edit_requestbook)
                    db.session.commit()
                    return jsonify({"message": "Book request denied and removed from the requested books table"}), 204
            else:
                return jsonify({"message": "No updates were made. Please provide new values."}), 204
    return jsonify({"message":"User not authorized"}), 401

@requestedBooks_bp.delete('/edit_requestedbooks/<int:id>')
@jwt_required()
def delete_requestedbooks(id):
    claims = get_jwt()
    if claims.get('is_staff') == True:
        delete_request = RequestedBooks.query.filter_by(request_id = id).first()
        if not delete_request:
            return jsonify({"message":"No books request made with this ID."}), 404
        db.session.delete(delete_request)
        db.session.commit()
        return jsonify({"message":"Book request with this ID is deleted."}), 200
    else:
        return jsonify({"message":"User not authorized"}), 401
    
#-----------------------IssuedBooks API-----------------------#

issuedBooks_bp = Blueprint(
    'issuedbooks',
    __name__
)

@issuedBooks_bp.get('/issuedbooks')
@jwt_required()
def get_issuedbooks():
    issuedBks = IssuedBooks.query.all()
    data = [issuedBk.to_dict() for issuedBk in issuedBks]
    return make_response(data, 200)

@issuedBooks_bp.post('/issuedbooks')
@jwt_required()
def post_issuedbooks():
    claims = get_jwt()
    if claims.get('is_staff') == True:
        args = request.get_json()
        if args['username']:
            check_name = User.query.filter_by(username = args['username']).first()
            if not check_name:
                return jsonify({"message":"Username must exist in the database."}), 409
        else:
            return jsonify({"message":"Username field cannot be empty."}), 404
        if args['book_name']:
            name = Book.query.filter_by(book_name = args['book_name']).first()
            if not name:
                return jsonify({"message":"Book with this name must exist in the database."}), 409
        else:
            return jsonify({"message":"Book name is required."}), 404
        if args['issue_date']:
            today = datetime.today()
            if datetime.strptime(args['issue_date'], "%Y-%m-%d") > today:
                return jsonify({"message":"Issue date cannot be in the future."}), 404
            #User can access a book for only 7 days
            currentDate = datetime.now().date()
            allowed_Date = currentDate - timedelta(days=7)
            issued_DATE = datetime.strptime(args['issue_date'], "%Y-%m-%d").date()
            if issued_DATE < allowed_Date:
                issue_date = allowed_Date
            else:
                issue_date = datetime.strptime(args['issue_date'], "%Y-%m-%d")
        else:
            return jsonify({"message":"Book issue date is required."}), 404
        if (args['daysLeft']>=0) and (args['daysLeft']<8):
            days = args['daysLeft']
        else:
            days = 7
        new_Issue = IssuedBooks(
            username = args['username'],
            book_name = args['book_name'],
            issue_date = issue_date,
            daysLeft = days
        )
        #Avoid entry duplication
        issues = IssuedBooks.query.all()
        for i in issues:
            if new_Issue.username == i.username and new_Issue.book_name == i.book_name and new_Issue.issue_date == i.issue_date:
                return jsonify({"message":"This entry already exists in the database. Recheck details."}), 409
        db.session.add(new_Issue)
        db.session.commit()
        if issued_DATE < allowed_Date:
            return jsonify({"message":"issue_date provided was less than 7 days from today. It has been corrected to 7 ago days from today."}), 201
        else:
            return make_response(new_Issue.to_dict(), 201)        
    else:
        return jsonify({"message":"User not authorized"}), 401

@issuedBooks_bp.patch('/edit_issuedbooks/<int:id>')
@jwt_required()
def patch_issuedbooks(id):
    claims = get_jwt()
    if claims.get('is_staff') == True:
        args = request.get_json()
        edit_issue = IssuedBooks.query.filter_by(issue_id = id).first()
        if not edit_issue:
            return jsonify({"message":"No book issued with this ID."}), 404
        else:
            updated = False
            username = args.get("username", None)
            book_name = args.get("book_name", None)
            issue_date = args.get("issue_date", None)
            daysLeft = args.get("daysLeft", None)
            
            if username and username != edit_issue.username:
                uname = User.query.filter_by(username = args['username']).first()
                if uname:
                    updated = True
                    edit_issue.username = args['username']
                else:
                    return jsonify({"message":"Username does not exist."}), 404
            if book_name and book_name != edit_issue.book_name:
                book = Book.query.filter_by(book_name = args['book_name']).first()
                if book:
                    updated = True
                    edit_issue.book_name = args['book_name']
                else:
                    return jsonify({"message":"Book does not exist in database."}), 404   
            if issue_date and issue_date != edit_issue.issue_date:
                today = datetime.today()
                if datetime.strptime(args['issue_date'], "%Y-%m-%d") > today:
                    return jsonify({"message":"Issue date cannot be in the future."}), 404
                else:
                    updated = True
                    edit_issue.issue_date = datetime.strptime(args['issue_date'], "%Y-%m-%d")
            if daysLeft and daysLeft != edit_issue.daysLeft:
                if (int(daysLeft) >= 8) or (int(daysLeft) < 0):
                    return jsonify({"message":"Days left to read a book must be an integer between 0 to 7 days."})
                updated = True
                edit_issue.daysLeft = int(args['daysLeft'])
            if updated:
                db.session.commit()
                return make_response(edit_issue.to_dict(), 201)
            else:
                return jsonify({"message":"No updates were made. Please provide new values."}), 204        
    else:
        return jsonify({"message":"User not authorized"}), 401
    
# @issuedBooks_bp.patch('/edit_issuedbooks/<int:id>')
# @jwt_required()
# def patch_issuedbooks(id):
#     claims = get_jwt()
#     if claims.get('is_staff') == True:
#         args = request.get_json()
#         edit_issue = IssuedBooks.query.filter_by(issue_id = id).first()
#         if not edit_issue:
#             return jsonify({"message":"No book issued with this ID."}), 404
#         else:
#             updated = False
#             username = args.get("username", None)
#             book_name = args.get("book_name", None)
#             issue_date = args.get("issue_date", None)
#             daysLeft = args.get("daysLeft", None)
#             if username or book_name or issue_date or daysLeft:
#                 if username:
#                         uname = User.query.filter_by(username = args['username']).first()
#                         if uname:
#                             edit_issue.username = args['username']
#                         else:
#                             return jsonify({"message":"Username does not exist."}), 404
#                 elif book_name:
#                         book = Book.query.filter_by(book_name = args['book_name']).first()
#                         if book:
#                             edit_issue.book_name = args['book_name']
#                         else:
#                             return jsonify({"message":"Book does not exist in database."}), 404   
#                 elif issue_date:
#                     today = datetime.today()
#                     if datetime.strptime(args['issue_date'], "%Y-%m-%d") > today:
#                         return jsonify({"message":"Issue date cannot be in the future."}), 404
#                     else:
#                         edit_issue.issue_date = datetime.strptime(args['issue_date'], "%Y-%m-%d")
#                 elif daysLeft:
#                     if (int(daysLeft) >= 8) or (int(daysLeft) < 0):
#                         return jsonify({"message":"Days left to read a book must be an integer between 0 to 7 days."})
#                     edit_issue.daysLeft = int(args['daysLeft'])
#                 db.session.commit()
#             else:
#                 return jsonify({"message":"No data provided."}), 204
#             # db.session.commit()
#             return make_response(edit_issue.to_dict(), 201)
#     else:
#         return jsonify({"message":"User not authorized"}), 401

@issuedBooks_bp.delete('/edit_issuedbooks/<int:id>')
@jwt_required()
def delete_issuedbooks(id):
    claims = get_jwt()
    if claims.get('is_staff') == True:
        delete_issue = IssuedBooks.query.filter_by(issue_id = id).first()
        if not delete_issue:
            return jsonify({"message":"No books issued with this ID."}), 404
        db.session.delete(delete_issue)
        db.session.commit()
        return jsonify({"message":"Book issue deleted."}), 200
    else:
        return jsonify({"message":"User not authorized"}), 401

#-----------------------ReturnedBooks API-----------------------#
    
returnedBooks_bp = Blueprint(
    'returnedbooks',
    __name__
)

@returnedBooks_bp.get('/returnedbooks')
@jwt_required()
def get_returnbooks():
    returnbks = ReturnedBooks.query.all()
    data = [returnbk.to_dict() for returnbk in returnbks]
    return make_response(data, 200)

@returnedBooks_bp.post('/returnedbooks')
@jwt_required()
def post_returnbooks():
    args = request.get_json()
    if args['issue_ID']:
        # pass
        returned = ReturnedBooks.query.filter_by(issue_ID = args['issue_ID']).first()
        if returned:
            pass
        else:
            issued = IssuedBooks.query.filter_by(issue_id = args['issue_ID']).first()
            if not issued:
                return jsonify({"message":"No book issued with this id."}), 409
    else:
        return jsonify({"message":"Issue ID is required and should be linked to an issued book."}), 404
    if args['return_date']:
        today = datetime.today()
        if datetime.strptime(args['return_date'], "%Y-%m-%d") > today:
            return jsonify({"message":"Return date cannot be in the future"}), 400
        return_date = datetime.strptime(args['return_date'], "%Y-%m-%d")
    else:
        date_header = request.headers.get('date')
        # return_date = date_header
        try:
            parsed_date = datetime.strptime(date_header, "%Y-%m-%d")
            return_date = parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            return_date = date_header
    if args['book_name']:
        return_book = Book.query.filter_by(book_name = args['book_name']).first()
        if not return_book:
            return jsonify({"message":"No book issued with this name."}), 409
    else:
        return jsonify({"message":"Book name is required and should be in Books table."}), 404
    if args['username']:
        usr = User.query.filter_by(username = args['username']).first()
        if not usr:
            return jsonify({"message":"Username does not exist in the username."}), 409
    else:
        return jsonify({"message":"Username is required and should be in Users table."}), 404
    if args['rating']:
        if args['rating'] < 1:
            rating = 1
        elif args['rating'] > 5.001:
            rating = 5
        else:
            rating = args['rating']
    else:
        return jsonify({"message":"Book rating by user is required."}), 404
    new_Return = ReturnedBooks(
        issue_ID = args['issue_ID'],
        return_date = return_date,
        book_name = args['book_name'],
        username = args['username'],
        rating = rating
    )
    db.session.add(new_Return)
    db.session.commit()
    #Remove returned book from issued table
    remove_issued_book = IssuedBooks.query.filter_by(issue_id = args['issue_ID']).first()
    db.session.delete(remove_issued_book)
    db.session.commit()
    return make_response(new_Return.to_dict(), 201) 

@returnedBooks_bp.patch('/edit_returnedbooks/<int:id>')
@jwt_required()
def patch_returnbooks(id):
    claims = get_jwt()
    if claims.get('is_staff') == True:
        args = request.get_json()
        edit_return = ReturnedBooks.query.filter_by(return_id = id).first()
        if not edit_return:
            return jsonify({"message":"No book returned with this ID."}), 404
        else:
            updated = False
            issue_ID = args.get("issue_ID", None)
            return_date = args.get("return_date", None)
            book_name = args.get("book_name", None)
            username = args.get("username", None)
            rating = args.get("rating", None)
            issued = IssuedBooks.query.filter_by(issue_id = edit_return.issue_ID).first()
            if issue_ID and issue_ID != edit_return.issue_ID:
                issuedbooks = IssuedBooks.query.filter_by(issue_id = args['issue_ID']).first()
                if issuedbooks:
                    updated = True
                    edit_return.issue_ID = args['issue_ID']
                else:
                    return jsonify({"message":"No book issued with this ID."}), 404
            if return_date and return_date != edit_return.return_date:
                today = datetime.today()
                if datetime.strptime(args['return_date'], "%Y-%m-%d") > today:
                    return jsonify({"message":"Return date cannot be in the future."}), 404
                else:
                    updated = True
                    edit_return.return_date = datetime.strptime(args['return_date'], "%Y-%m-%d")
            if (book_name) and (book_name != edit_return.book_name) and (len(book_name) > 0):
                    if Book.query.filter_by(book_name = book_name).first(): 
                        updated = True
                        edit_return.book_name = issued.book_name 
                    else:
                        return jsonify({"message":"Book with this name does not exist in the system."}), 404
            if (username) and (username != edit_return.username) and (len(username) > 0):
                    if User.query.filter_by(username = username).first():
                        updated = True
                        edit_return.username = issued.username 
                    else:
                        return jsonify({"message":"Username does not exist in the system."}), 404
            if (rating) and (rating != edit_return.rating) and (type(rating) == int):
                updated = True
                if args['rating'] < 1:
                    edit_return.rating = 1
                elif args['rating'] > 5.001:
                    edit_return.rating = 5
                else:
                    edit_return.rating = args['rating']
            if updated:
                db.session.commit()
                return make_response(edit_return.to_dict(), 201)
            else:
                return jsonify({"message":"No updates were made. Please provide new values."}), 404    
    else:
        return jsonify({"message":"User not authorized"}), 401

@returnedBooks_bp.delete('/edit_returnedbooks/<int:id>')
@jwt_required()
def delete_returnbooks(id):
    if id == 1:
        return jsonify({"message":"Cannot delete user with this ID."}), 404
    claims = get_jwt()
    if claims.get('is_staff') == True:
        delete_return = ReturnedBooks.query.filter_by(return_id = id).first()
        if not delete_return:
            return jsonify({"message":"No books returned with this ID."}), 404
        db.session.delete(delete_return)
        db.session.commit()
        return jsonify({"message":"Book return deleted."}), 200
    else:
        return jsonify({"message":"User not authorized"}), 401
    
#====================END OF FILE====================#