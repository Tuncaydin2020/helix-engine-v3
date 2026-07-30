"""
HELIX Authentication Service
"""

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from backend.database import db, UserModel

class AuthService:
    """Service for user authentication."""
    
    @staticmethod
    def register_user(username: str, email: str, password: str):
        """Register a new user."""
        # Check if user already exists
        existing_user = UserModel.query.filter(
            (UserModel.username == username) | (UserModel.email == email)
        ).first()
        
        if existing_user:
            return None, "Username or email already exists"
        
        # Create new user
        user = UserModel(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()
        
        return user, None
    
    @staticmethod
    def login_user(username: str, password: str):
        """Login a user."""
        user = UserModel.query.filter_by(username=username).first()
        
        if not user:
            return None, "User not found"
        
        if not check_password_hash(user.password_hash, password):
            return None, "Invalid password"
        
        login_user(user, remember=True)
        return user, None
    
    @staticmethod
    def logout_user():
        """Logout the current user."""
        logout_user()
    
    @staticmethod
    def get_current_user():
        """Get the current logged-in user."""
        return current_user


