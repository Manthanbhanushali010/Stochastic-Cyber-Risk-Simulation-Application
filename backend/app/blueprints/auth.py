"""
Authentication blueprint for user management and JWT token handling.

This module provides endpoints for user registration, login, logout,
and token refresh functionality with proper validation and security.
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt, verify_jwt_in_request
)
from marshmallow import Schema, fields, ValidationError, validates, validates_schema
import re
import structlog

from app import db
from app.models import User

logger = structlog.get_logger(__name__)

# Create the authentication blueprint
auth_bp = Blueprint('auth', __name__)


# Validation schemas using Marshmallow
class UserRegistrationSchema(Schema):
    """Schema for user registration validation."""
    
    email = fields.Email(required=True, error_messages={'required': 'Email is required'})
    username = fields.Str(required=True, validate=lambda x: len(x) >= 3, 
                         error_messages={'required': 'Username is required'})
    password = fields.Str(required=True, validate=lambda x: len(x) >= 8,
                         error_messages={'required': 'Password is required'})
    first_name = fields.Str(missing=None)
    last_name = fields.Str(missing=None)
    
    @validates('email')
    def validate_email_unique(self, value):
        """Validate email is unique."""
        existing_user = User.query.filter_by(email=value).first()
        if existing_user:
            raise ValidationError('Email already registered')
    
    @validates('username')
    def validate_username_unique(self, value):
        """Validate username is unique."""
        existing_user = User.query.filter_by(username=value).first()
        if existing_user:
            raise ValidationError('Username already taken')
    
    @validates('password')
    def validate_password_strength(self, value):
        """Validate password strength."""
        if len(value) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        
        # Check for at least one digit
        if not re.search(r'\d', value):
            raise ValidationError('Password must contain at least one digit')
        
        # Check for at least one letter
        if not re.search(r'[a-zA-Z]', value):
            raise ValidationError('Password must contain at least one letter')


class UserLoginSchema(Schema):
    """Schema for user login validation."""
    
    email = fields.Email(required=True, error_messages={'required': 'Email is required'})
    password = fields.Str(required=True, error_messages={'required': 'Password is required'})


class PasswordChangeSchema(Schema):
    """Schema for password change validation."""
    
    current_password = fields.Str(required=True, error_messages={'required': 'Current password is required'})
    new_password = fields.Str(required=True, validate=lambda x: len(x) >= 8,
                             error_messages={'required': 'New password is required'})
    
    @validates('new_password')
    def validate_password_strength(self, value):
        """Validate new password strength."""
        if len(value) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        
        if not re.search(r'\d', value):
            raise ValidationError('Password must contain at least one digit')
        
        if not re.search(r'[a-zA-Z]', value):
            raise ValidationError('Password must contain at least one letter')


# Initialize schemas
registration_schema = UserRegistrationSchema()
login_schema = UserLoginSchema()
password_change_schema = PasswordChangeSchema()


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user account.
    
    Expected JSON payload:
    {
        "email": "user@example.com",
        "username": "username",
        "password": "password123",
        "first_name": "John",  // optional
        "last_name": "Doe"     // optional
    }
    """
    try:
        # Validate request data
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate input using schema
        try:
            validated_data = registration_schema.load(json_data)
        except ValidationError as err:
            return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
        
        # Create new user
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            role='user'  # Default role
        )
        
        # Set password (will be hashed automatically)
        user.set_password(validated_data['password'])
        
        # Save to database
        db.session.add(user)
        db.session.commit()
        
        logger.info("New user registered", user_id=str(user.id), email=user.email)
        
        # Create tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error("Registration failed", error=str(e))
        return jsonify({'error': 'Registration failed', 'message': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT tokens.
    
    Expected JSON payload:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    try:
        # Validate request data
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate input using schema
        try:
            validated_data = login_schema.load(json_data)
        except ValidationError as err:
            return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
        
        # Find user by email
        user = User.query.filter_by(email=validated_data['email']).first()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if user account is active
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Verify password
        if not user.check_password(validated_data['password']):
            logger.warning("Failed login attempt", email=validated_data['email'])
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Update last login timestamp
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        logger.info("User logged in successfully", user_id=str(user.id), email=user.email)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        logger.error("Login failed", error=str(e))
        return jsonify({'error': 'Login failed', 'message': str(e)}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token.
    
    Requires valid refresh token in Authorization header.
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Verify user still exists and is active
        user = User.query.get(current_user_id)
        if not user or not user.is_active:
            return jsonify({'error': 'User account not found or inactive'}), 404
        
        # Create new access token
        new_access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': new_access_token
        }), 200
        
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        return jsonify({'error': 'Token refresh failed'}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user and blacklist current token.
    
    Requires valid access token in Authorization header.
    """
    try:
        # Get the JWT token ID (jti) to blacklist
        jti = get_jwt()['jti']
        
        # In a production application, you would add the jti to a Redis blacklist
        # For now, we'll just return success
        # TODO: Implement proper token blacklisting with Redis
        
        current_user_id = get_jwt_identity()
        logger.info("User logged out", user_id=current_user_id)
        
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        logger.error("Logout failed", error=str(e))
        return jsonify({'error': 'Logout failed'}), 500


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get current user profile information.
    
    Requires valid access token in Authorization header.
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error("Get profile failed", error=str(e))
        return jsonify({'error': 'Failed to retrieve profile'}), 500


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update current user profile information.
    
    Expected JSON payload:
    {
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        if 'first_name' in json_data:
            user.first_name = json_data['first_name']
        if 'last_name' in json_data:
            user.last_name = json_data['last_name']
        
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        logger.info("User profile updated", user_id=str(user.id))
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error("Profile update failed", error=str(e))
        return jsonify({'error': 'Profile update failed'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change user password.
    
    Expected JSON payload:
    {
        "current_password": "oldpassword",
        "new_password": "newpassword123"
    }
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate input using schema
        try:
            validated_data = password_change_schema.load(json_data)
        except ValidationError as err:
            return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
        
        # Verify current password
        if not user.check_password(validated_data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Set new password
        user.set_password(validated_data['new_password'])
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        logger.info("Password changed successfully", user_id=str(user.id))
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error("Password change failed", error=str(e))
        return jsonify({'error': 'Password change failed'}), 500


@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """
    Verify if the current access token is valid.
    
    Requires valid access token in Authorization header.
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'Invalid or inactive user'}), 401
        
        return jsonify({
            'valid': True,
            'user_id': current_user_id,
            'expires_at': get_jwt()['exp']
        }), 200
        
    except Exception as e:
        logger.error("Token verification failed", error=str(e))
        return jsonify({'error': 'Token verification failed'}), 500


# Error handlers for the auth blueprint
@auth_bp.errorhandler(ValidationError)
def handle_validation_error(e):
    """Handle Marshmallow validation errors."""
    return jsonify({'error': 'Validation failed', 'details': e.messages}), 400


@auth_bp.errorhandler(422)
def handle_unprocessable_entity(e):
    """Handle unprocessable entity errors."""
    return jsonify({'error': 'Unprocessable entity'}), 422 