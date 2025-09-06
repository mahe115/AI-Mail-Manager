#!/usr/bin/env python3
"""Test email connection with provided credentials"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from config import config
import imaplib

print("📧 Email Connection Test")
print("=" * 50)

try:
    # Test IMAP connection
    print(f"Connecting to {config.email.imap_server}:{config.email.imap_port}")
    print(f"Email: {config.email.email}")
    print(f"Password: {'*' * len(config.email.password)}")
    
    # Create IMAP connection
    mail = imaplib.IMAP4_SSL(config.email.imap_server, config.email.imap_port)
    
    # Login
    mail.login(config.email.email, config.email.password)
    print("✅ Email login successful!")
    
    # List mailboxes
    status, mailboxes = mail.list()
    print(f"📁 Found {len(mailboxes)} mailboxes")
    
    # Select INBOX
    mail.select('INBOX')
    status, messages = mail.search(None, 'ALL')
    message_count = len(messages[0].split())
    print(f"📬 Found {message_count} emails in INBOX")
    
    # Close connection
    mail.logout()
    print("✅ Email connection test passed!")
    
except Exception as e:
    print(f"❌ Email connection failed: {e}")
    print("\n🔧 Troubleshooting:")
    print("1. Make sure 2-Factor Authentication is enabled")
    print("2. Generate a new App Password from Google Account")
    print("3. Update the EMAIL_PASSWORD in .env file")
    print("4. Make sure IMAP is enabled in Gmail settings")
    print("5. Check if the App Password is correct")

