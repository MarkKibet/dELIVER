from functools import wraps
from flask import request, jsonify
from app.services.auth_service import verify_token
from models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'message': 'Token is invalid or expired'}), 401
        current_user = User.query.get(user_id)
        return f(current_user, *args, **kwargs)
    return decorated

def validate_json(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            errors = schema().validate(data)
            if errors:
                return jsonify(errors), 400
            return f(data, *args, **kwargs)
        return decorated_function
    return decorator
