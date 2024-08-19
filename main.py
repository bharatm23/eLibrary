from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import flask_excel as excel

from celery.schedules import crontab
from application.tasks import send_daily_reminder, send_monthly_report, send_daily_reminder_issued, send_monthly_activity_report
from application.models import IssuedBooks

from application.models import db, User, TokenBlockedList
from application.config import DevelopmentConfig
from application.resources.api import (reports_bp, search_bp, sections_bp, books_bp, users_bp, 
                                       requestedBooks_bp, issuedBooks_bp, returnedBooks_bp)
from application.worker import celery_init_app
from application.instances import cache

from application.resources.auth import auth_bp
from application.jwt import jwt

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    CORS(app)
    db.init_app(app)
    excel.init_excel(app)
    jwt.init_app(app)
    cache.init_app(app)
    with app.app_context():
        IssuedBooks.update_days_left()
        import application.views
        app.register_blueprint(sections_bp, url_prefix='/api')
        app.register_blueprint(books_bp, url_prefix='/api')
        app.register_blueprint(users_bp, url_prefix='/api')
        app.register_blueprint(requestedBooks_bp, url_prefix='/api')
        app.register_blueprint(issuedBooks_bp, url_prefix='/api')
        app.register_blueprint(returnedBooks_bp, url_prefix='/api')
        app.register_blueprint(search_bp, url_prefix='/api')
        app.register_blueprint(reports_bp, url_prefix='/api')
        app.register_blueprint(auth_bp,url_prefix='/auth')
    return app

#additional claims
@jwt.additional_claims_loader
def make_additional_claims(identity):
    if identity == "Librarian":
        return {"is_staff" : True}
    return {"is_staff": False}

#WHICH USER
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_headers, jwt_data):
    identity = jwt_data['sub']
    return User.query.filter_by(username = identity).one_or_none()


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    return jsonify({"message": "Token has expired.", "error": "token_expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": "Signature verification failed", "error": "invalid_token"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"message": "Request does not contain valid token", "error": "authorization_header"}), 401

#Blocked users
@jwt.token_in_blocklist_loader
def token_blocklist_callback(jwt_header,jwt_data):
    jti = jwt_data['jti']
    token = db.session.query(TokenBlockedList).filter(TokenBlockedList.jti == jti).scalar()
    return token is not None

app = create_app()
celery_app = celery_init_app(app)

@celery_app.on_after_configure.connect
def send_email(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=19, minute=10),
        send_daily_reminder.s(),
        name='send daily reminder email'
    )
    sender.add_periodic_task(
        crontab(hour=19, minute=48),
        send_daily_reminder_issued.s(),
        name='send daily issued reminder email'
    )
    sender.add_periodic_task(
        crontab(hour=10, minute=00, day_of_month=1),
        # crontab(minute='15', hour='50', day_of_month='1'),
        send_monthly_report.s(),
        name='send monthly reminder email'
    )
    sender.add_periodic_task(
        crontab(hour=18, minute=19),
        # crontab(minute='15', hour='50', day_of_month='1'),
        send_monthly_activity_report.s(),
        name='User monthly activity report'
    )

if __name__ == '__main__':
    app.run(debug=True)