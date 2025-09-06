# Configuration settings for AI-Powered Communication Assistant
import os
from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class EmailConfig:
    """Email server configuration"""
    imap_server: str = "imap.gmail.com"
    imap_port: int = 993
    smtp_server: str = "smtp.gmail.com" 
    smtp_port: int = 587
    email: str = os.getenv("EMAIL_ADDRESS", "")
    password: str = os.getenv("EMAIL_PASSWORD", "")
    
@dataclass
class OpenAIConfig:
    """OpenAI API configuration"""
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = "gpt-3.5-turbo"  # Changed to more widely available model
    max_tokens: int = 300  # Increased for better responses
    temperature: float = 0.7
    
@dataclass
class DatabaseConfig:
    """Database configuration"""
    db_path: str = "database/emails.db"
    backup_interval: int = 24  # hours
    
@dataclass
class FilterConfig:
    """Email filtering configuration"""
    support_keywords: List[str] = None
    priority_keywords: List[str] = None
    
    def __post_init__(self):
        if self.support_keywords is None:
            self.support_keywords = [
                "support", "help", "query", "request", "issue", 
                "problem", "urgent", "asap", "immediately", "critical"
            ]
        if self.priority_keywords is None:
            self.priority_keywords = [
                "urgent", "critical", "asap", "immediately", "emergency",
                "cannot access", "not working", "down", "broken", "error"
            ]

@dataclass  
class StreamlitConfig:
    """Streamlit dashboard configuration"""
    page_title: str = "AI Communication Assistant"
    page_icon: str = "📧"
    layout: str = "wide"
    refresh_interval: int = 30  # seconds
    
class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.email = EmailConfig()
        self.openai = OpenAIConfig()
        self.database = DatabaseConfig()
        self.filters = FilterConfig()
        self.streamlit = StreamlitConfig()
        
        # Flask settings
        self.FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
        self.FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
        self.FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
        
        # Streamlit settings
        self.STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
        
    def validate(self) -> bool:
        """Validate critical configuration"""
        errors = []
        
        if not self.email.email:
            errors.append("EMAIL_ADDRESS is required")
        if not self.email.password:
            errors.append("EMAIL_PASSWORD is required")  
        if not self.openai.api_key:
            errors.append("OPENAI_API_KEY is required")
            
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        return True

# Global configuration instance
config = Config()