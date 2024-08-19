from application.models import db, create_initial_data
from main import app

with app.app_context():
    print("==== DB File does not exist, Creating one =====")
    db.create_all()
    print("==== Creating Librarian and Common Categories =====")           
    create_initial_data(db)