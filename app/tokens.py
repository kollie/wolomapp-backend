from flask import jsonify
from app import db, app
from app.auth import basic_auth, token_auth


@app.route('/api/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    data = basic_auth.current_user().get_token()
    db.session.commit()
    return jsonify(data)


@app.route('/api/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204

#curl -X GET -H "Authorization: Bearer 18yra2aIeQVqmzKcDk0cD8bfmJILpm4n" http://localhost:5000/api/users/30
