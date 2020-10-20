from flask import jsonify, request, url_for, abort, session
from app import db, app
from app.models import User, Issues
from app.auth import token_auth
from app.error import bad_request
from flask_login import current_user
from datetime import datetime
import uuid
import base64
import boto3
import json

BUCKET = app.config['S3_BUCKET']
s3URL = app.config['S3URL']

s3_resource = boto3.resource(
    "s3",
    aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
)


def upload_file(file_name, bucket):
    object_name = file_name
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket, object_name)
    return response


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/api/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())


@app.route('/api/users', methods=['GET'])
@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'get_users')
    return jsonify(data)


@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('get_user', id=user.id)
    return response


@app.route('/api/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    data['picture'] = convert_and_save(data['picture'])
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())



@app.route('/api/issues', methods=['POST'])
@token_auth.login_required
def create_isses():
    data = request.get_json() or {}
    if 'user_id' not in data:
        return bad_request('must include user id field')
    if User.query.filter_by(id=data['user_id']).first() is None:
        return bad_request('invalid user id')
    data['picture'] = convert_and_save(data['picture'])
    issue = Issues()
    issue.from_dict(data, new_issue=True)
    db.session.add(issue)
    db.session.commit()
    response = jsonify(issue.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('get_issue', id=issue.id)
    return response


def convert_and_save(b64_string):
    unique_filename = str(uuid.uuid4())
    filename = unique_filename + '.jpg'
    with open(filename, "wb") as fh:
        fh.write(base64.decodebytes(b64_string.encode()))
        upload_file(filename, BUCKET)
    return filename


@app.route('/api/issues', methods=['GET'])
@token_auth.login_required
def get_issues():
    issues = [issue.to_dict() for issue in Issues.query.order_by(Issues.timestamp.desc()).all()]
    return jsonify(issues)

@app.route('/api/issues/<int:id>', methods=['GET'])
@token_auth.login_required
def get_issue(id):
    issues = [issue.to_dict() for issue in Issues.query.filter_by(user_id=id).all()]
    return jsonify(issue=issues)

