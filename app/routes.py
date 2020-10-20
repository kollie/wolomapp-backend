from flask import Flask, render_template, request, jsonify, url_for, flash, redirect, \
    session
from app.models import User
from app import app, db, oauth
from app.error import bad_request
from app.auth_decorator import login_required
from app.auth import token_auth, basic_auth


@app.route('/readHello')
def getRequestHello():
	return "Hi, I got your GET Request!"

#POST REQUEST
@app.route('/createHello', methods = ['POST'])
def postRequestHello():
	return "I see you sent a POST message :-)"
#UPDATE REQUEST
@app.route('/updateHello', methods = ['PUT'])
def updateRequestHello():
	return "Sending Hello on an PUT request!"

#DELETE REQUEST
@app.route('/deleteHello', methods = ['DELETE'])
def deleteRequestHello():
	return "Deleting your hard drive.....haha just kidding! I received a DELETE request!"



