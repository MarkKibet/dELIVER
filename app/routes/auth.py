from flask import Blueprint, request, jsonify, current_app
from flask_mail import Mail, Message
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from models import User, db
from app import mail  # Import the already-initialized mail object
from app.schemas.user_schema import (
    UserRegisterSchema,
    UserLoginSchema,
    PasswordResetRequestSchema,
    PasswordResetSchema,
    UserBaseSchema
)
from app.services.auth_service import generate_token, verify_token, blacklist_token
from app.services.email_service import send_password_reset_email
from app.utils.decorators import token_required, validate_json
from app.utils.helpers import generate_verification_token

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
@validate_json(UserRegisterSchema)
def register(validated_data):
    # Check if user already exists
    if User.query.filter_by(email=validated_data['email']).first():
        return jsonify({'message': 'User already exists with this email'}), 409

    # Hash the password before saving
    hashed_password = generate_password_hash(validated_data['password'])

    # Create new user
    new_user = User(
        username=validated_data['username'],
        email=validated_data['email'],
        password_hash=hashed_password
    )

    
    db.session.add(new_user)
    db.session.commit()
   

    return jsonify({
        'message': 'User registered successfully. Please check your email to verify your account.',
        'user_id': new_user.id
    }), 201



@auth_bp.route('/login', methods=['POST'])
@validate_json(UserLoginSchema)
def login(validated_data):
    
    user = User.query.filter_by(email=validated_data['email']).first()

    
    if not user or not user.check_password(validated_data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401

    # Check if user account is active
    if not user.is_active:
        return jsonify({'message': 'Please verify your email before logging in'}), 401

    # Generate JWT token
    token = generate_token(user.id)

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': UserBaseSchema().dump(user)
    }), 200

@auth_bp.route('/password-reset', methods=['POST'])
@validate_json(PasswordResetRequestSchema)
def request_password_reset(validated_data):
    # Find user by email
    user = User.query.filter_by(email=validated_data['email']).first()


    if not user:
        return jsonify({'message': 'If your email is registered, you will receive a password reset link'}), 200

    # Generate reset token
    token = generate_verification_token()
    user.verification_token = token
    user.token_expiry = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()

    # Send password reset email
    send_password_reset_email(user.email, token)

    return jsonify({'message': 'If your email is registered, you will receive a password reset link'}), 200

@auth_bp.route('/password-reset/<token>', methods=['POST'])
@validate_json(PasswordResetSchema)
def reset_password(token, validated_data):
    # Find user with this token
    user = User.query.filter_by(verification_token=token).first()

    if not user:
        return jsonify({'message': 'Invalid or expired token'}), 400

    # Check if token is expired
    if user.token_expiry < datetime.utcnow():
        return jsonify({'message': 'Password reset link has expired'}), 400

    # Update password
    user.set_password(validated_data['password'])
    user.verification_token = None
    user.token_expiry = None
    db.session.commit()

    return jsonify({'message': 'Password updated successfully'}), 200
