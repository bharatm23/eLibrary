from flask import current_app as app, jsonify, request, render_template, send_file
from flask import make_response
from flask_jwt_extended import jwt_required, get_jwt
from .models import db, User, IssuedBooks, RequestedBooks, Book
import flask_excel as excel
from .tasks import create_ebook_csv, download_ebook, librarian_triggered
from celery.result import AsyncResult

@app.get('/download_csv')
def download_csv_librarian():
    # data = request.get_json()
    # b_name = data.get('b_name') 
    # task = download_ebook.delay(b_name) 
    task = librarian_triggered.delay()
    return jsonify({"task-id": task.id})

@app.get('/download_librarian_csv/<task_id>')
def librarian_csv(task_id):
    res = AsyncResult(task_id)
    filename = res.result
    if res.ready():
        return send_file(filename, as_attachment=True, mimetype='text/csv')

@app.post('/download_ebook')
def download_ebook_student():
    data = request.get_json()
    b_name = data.get('b_name') 

    task = download_ebook.delay(b_name) 
    return jsonify({"task-id": task.id})

@app.get('/download_ebook_student_csv/<task_id>')
def download_ebook_student_csv(task_id):
    res = AsyncResult(task_id)
    filename = res.result
    if res.ready():
        return send_file(filename, as_attachment=True, mimetype='text/csv')


# @app.get('/download_ebook')
# def download_ebook_student():
#     task = download_ebook.delay()
#     return jsonify({"task-id": task.id})

# @app.get('/download_ebook_student/<task_id>')
# def download_ebook_student_csv(task_id):
#     res = AsyncResult(task_id)
#     filename = res.result
#     if res.ready():
#         return send_file(filename, as_attachment=True, mimetype='text/csv')


@app.get('/download-csv')
def download_ebooks_csv():
    task = create_ebook_csv.delay()
    return jsonify({"task-id": task.id})

@app.get('/get_ebook_csv/<task_id>')
def get_ebook_csv(task_id):
    res = AsyncResult(task_id)
    filename = res.result
    if res.ready():
        return send_file(filename, as_attachment=True, mimetype='text/csv')
    #     file_content = res.get()  # Get file content
    #     return send_file(
    #         io.BytesIO(file_content),  # Create a file-like object from the content
    #         as_attachment=True, 
    #         mimetype='text/csv',
    #         download_name='ebooks.csv'  # Set the desired filename
    #     )
    # else:
    #     return jsonify({"status": res.status}), 202

@app.get('/')
def home():
    return render_template("index.html")

#WORKS
@app.get('/all-students')
@jwt_required()
def all_students():
    claims = get_jwt()
    if claims.get('is_staff') == True:
        users = User.query.all()
        if len(users) == 0:
            return jsonify({"message":"No users found."}), 404
        data = [user.to_dict() for user in users]
        return make_response(data, 200)
    return jsonify({"message":"User not authorized"}), 401

@app.post('/request-book')
@jwt_required()
def request_book():
    current_user = get_jwt()
    data = request.get_json()
    b_id = data.get('bookId')
    book_name = data.get('bookName')
    student_username = data.get('studentUsername')
    if not b_id or not book_name:
        return jsonify({"error": "Book ID and name must be provided"}), 400
    if not student_username:
        return jsonify({"error": "Student username must not be null"}), 400
    
    existing_request = RequestedBooks.query.filter_by(student_username=student_username, book_id=b_id).first()
    if existing_request:
        return jsonify({"message": "Book has already been requested."}), 400
    
    new_request = RequestedBooks(student_username=student_username, book_id=b_id)
    
    db.session.add(new_request)
    db.session.commit()

    return jsonify({
        "message": f"Your request for '{book_name}' has been sent to the librarian.",
        "student_username": student_username,
        "book_id": b_id
    }), 200

#====================END OF FILE====================#