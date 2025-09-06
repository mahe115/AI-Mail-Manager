# Email service for Gmail IMAP integration
import imaplib
import email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from datetime import datetime
from typing import List, Dict, Optional
import html2text
import re
import json
from config import config

class EmailService:
    """Handles Gmail IMAP and SMTP operations"""
    
    def __init__(self):
        self.imap_server = config.email.imap_server
        self.imap_port = config.email.imap_port
        self.smtp_server = config.email.smtp_server
        self.smtp_port = config.email.smtp_port
        self.email = config.email.email
        self.password = config.email.password
        self.html_parser = html2text.HTML2Text()
        self.html_parser.ignore_links = True
        
    def connect_imap(self) -> imaplib.IMAP4_SSL:
        """Establish IMAP connection"""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email, self.password)
            return mail
        except Exception as e:
            print(f"IMAP connection failed: {e}")
            raise
    
    def connect_smtp(self) -> smtplib.SMTP:
        """Establish SMTP connection"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            return server
        except Exception as e:
            print(f"SMTP connection failed: {e}")
            raise
    
    def decode_mime_header(self, header: str) -> str:
        """Decode MIME header"""
        if header is None:
            return ""
        
        decoded_parts = decode_header(header)
        decoded_string = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    decoded_string += part.decode(encoding)
                else:
                    decoded_string += part.decode('utf-8', errors='ignore')
            else:
                decoded_string += part
        
        return decoded_string
    
    def extract_email_body(self, msg: email.message.Message) -> str:
        """Extract plain text body from email message"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                if "attachment" not in content_disposition:
                    if content_type == "text/plain":
                        charset = part.get_content_charset()
                        if charset is None:
                            charset = 'utf-8'
                        try:
                            body += part.get_payload(decode=True).decode(charset, errors='ignore')
                        except:
                            body += str(part.get_payload())
                    elif content_type == "text/html":
                        charset = part.get_content_charset()
                        if charset is None:
                            charset = 'utf-8'
                        try:
                            html_content = part.get_payload(decode=True).decode(charset, errors='ignore')
                            body += self.html_parser.handle(html_content)
                        except:
                            body += str(part.get_payload())
        else:
            content_type = msg.get_content_type()
            charset = msg.get_content_charset()
            if charset is None:
                charset = 'utf-8'
            
            if content_type == "text/plain":
                try:
                    body = msg.get_payload(decode=True).decode(charset, errors='ignore')
                except:
                    body = str(msg.get_payload())
            elif content_type == "text/html":
                try:
                    html_content = msg.get_payload(decode=True).decode(charset, errors='ignore')
                    body = self.html_parser.handle(html_content)
                except:
                    body = str(msg.get_payload())
        
        # Clean up the body text
        body = re.sub(r'\s+', ' ', body).strip()
        return body
    
    def is_support_email(self, subject: str, body: str) -> bool:
        """Check if email is support-related based on keywords"""
        text_to_check = (subject + " " + body).lower()
        
        for keyword in config.filters.support_keywords:
            if keyword.lower() in text_to_check:
                return True
        
        return False
    
    def determine_priority(self, subject: str, body: str) -> str:
        """Determine email priority based on keywords"""
        text_to_check = (subject + " " + body).lower()
        
        for keyword in config.filters.priority_keywords:
            if keyword.lower() in text_to_check:
                return "urgent"
        
        return "normal"
    
    def extract_key_information(self, subject: str, body: str) -> Dict:
        """Extract key information from email content"""
        import re
        
        key_info = {
            'phone_numbers': [],
            'email_addresses': [],
            'urls': [],
            'order_numbers': [],
            'account_numbers': [],
            'keywords': []
        }
        
        # Extract phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        key_info['phone_numbers'] = re.findall(phone_pattern, body)
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        key_info['email_addresses'] = re.findall(email_pattern, body)
        
        # Extract URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        key_info['urls'] = re.findall(url_pattern, body)
        
        # Extract order/account numbers (common patterns)
        order_pattern = r'\b(?:order|account|ticket|case)[\s#:]*(\d+)\b'
        key_info['order_numbers'] = re.findall(order_pattern, body, re.IGNORECASE)
        
        # Extract important keywords
        important_keywords = ['urgent', 'asap', 'immediately', 'critical', 'broken', 'not working', 
                            'refund', 'cancel', 'billing', 'payment', 'login', 'password', 'access']
        text_lower = (subject + " " + body).lower()
        key_info['keywords'] = [kw for kw in important_keywords if kw in text_lower]
        
        return key_info
    
    def fetch_emails(self, mailbox: str = "INBOX", limit: int = 50, days_back: int = 7) -> List[Dict]:
        """Fetch emails from specified mailbox with improved date filtering"""
        mail = self.connect_imap()
        emails = []
        
        try:
            mail.select(mailbox)
            
            # Search for recent emails (last N days)
            from datetime import datetime, timedelta
            since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
            search_criteria = f'(SINCE "{since_date}")'
            
            # Also search for unread emails regardless of date
            result, message_ids = mail.search(None, search_criteria)
            
            if result == 'OK':
                email_ids = message_ids[0].split() if message_ids[0] else []
                
                # If no recent emails, get unread emails
                if not email_ids:
                    result, message_ids = mail.search(None, 'UNSEEN')
                    if result == 'OK':
                        email_ids = message_ids[0].split() if message_ids[0] else []
                
                # If still no emails, get all emails but limit to recent ones
                if not email_ids:
                    result, message_ids = mail.search(None, 'ALL')
                    if result == 'OK':
                        all_ids = message_ids[0].split() if message_ids[0] else []
                        email_ids = all_ids[-limit:]  # Get last N emails
                else:
                    # Sort by newest first and limit
                    email_ids = sorted(email_ids, key=int, reverse=True)[:limit]
                
                for email_id in email_ids:
                    try:
                        result, msg_data = mail.fetch(email_id, '(RFC822)')
                        
                        if result == 'OK':
                            email_message = email.message_from_bytes(msg_data[0][1])
                            
                            # Extract email information
                            subject = self.decode_mime_header(email_message.get('Subject', ''))
                            sender = self.decode_mime_header(email_message.get('From', ''))
                            recipients_to = self.decode_mime_header(email_message.get('To', ''))
                            recipients_cc = self.decode_mime_header(email_message.get('Cc', ''))
                            recipients_bcc = self.decode_mime_header(email_message.get('Bcc', ''))
                            date_str = email_message.get('Date', '')
                            message_id = email_message.get('Message-ID', '')
                            thread_id = email_message.get('References', '')
                            
                            # Parse date
                            try:
                                email_date = email.utils.parsedate_to_datetime(date_str)
                            except:
                                email_date = datetime.now()
                            
                            # Extract body
                            body = self.extract_email_body(email_message)
                            
                            # Extract additional metadata
                            email_size = len(str(email_message))
                            is_read = '\\Seen' in email_message.get('X-Gmail-Labels', '')
                            
                            # Extract sender domain and name
                            sender_domain = ""
                            sender_name = ""
                            if '<' in sender and '>' in sender:
                                sender_name = sender.split('<')[0].strip()
                                email_part = sender.split('<')[1].split('>')[0]
                                sender_domain = email_part.split('@')[1] if '@' in email_part else ""
                            elif '@' in sender:
                                sender_domain = sender.split('@')[1] if '@' in sender else ""
                                sender_name = sender.split('@')[0]
                            
                            # Check if it's a support email
                            if self.is_support_email(subject, body):
                                # Determine priority
                                priority = self.determine_priority(subject, body)
                                
                                # Extract key information
                                key_info = self.extract_key_information(subject, body)
                                
                                email_data = {
                                    'message_id': message_id,
                                    'thread_id': thread_id,
                                    'sender': sender,
                                    'sender_name': sender_name,
                                    'sender_domain': sender_domain,
                                    'recipients': {
                                        'to': recipients_to,
                                        'cc': recipients_cc,
                                        'bcc': recipients_bcc
                                    },
                                    'subject': subject,
                                    'body': body[:5000],  # Limit body length
                                    'body_preview': body[:200] + "..." if len(body) > 200 else body,
                                    'timestamp': email_date,
                                    'priority': priority,
                                    'is_read': is_read,
                                    'email_size': email_size,
                                    'key_information': key_info,
                                    'labels': [],  # Will be populated later
                                    'attachments': []  # Will be populated later
                                }
                                
                                emails.append(email_data)
                                
                    except Exception as e:
                        print(f"Error processing email {email_id}: {e}")
                        continue
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
        finally:
            mail.close()
            mail.logout()
        
        return emails
    
    def send_response(self, to_email: str, subject: str, body: str, 
                     original_message_id: str = None) -> bool:
        """Send email response"""
        try:
            server = self.connect_smtp()
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = f"Re: {subject}" if not subject.startswith('Re:') else subject
            
            # Add reference to original message
            if original_message_id:
                msg['In-Reply-To'] = original_message_id
                msg['References'] = original_message_id
            
            # Attach body
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def mark_as_read(self, message_id: str, mailbox: str = "INBOX") -> bool:
        """Mark email as read"""
        try:
            mail = self.connect_imap()
            mail.select(mailbox)
            
            # Search for the message
            result, msg_ids = mail.search(None, f'HEADER Message-ID "{message_id}"')
            
            if result == 'OK' and msg_ids[0]:
                email_id = msg_ids[0].split()[0]
                mail.store(email_id, '+FLAGS', '\\Seen')
            
            mail.close()
            mail.logout()
            return True
            
        except Exception as e:
            print(f"Error marking email as read: {e}")
            return False
    
    def get_mailbox_list(self) -> List[str]:
        """Get list of available mailboxes"""
        try:
            mail = self.connect_imap()
            result, mailboxes = mail.list()
            
            mailbox_names = []
            if result == 'OK':
                for mailbox in mailboxes:
                    # Extract mailbox name from IMAP response
                    parts = mailbox.decode().split('"')
                    if len(parts) >= 3:
                        mailbox_names.append(parts[-2])
            
            mail.logout()
            return mailbox_names
            
        except Exception as e:
            print(f"Error getting mailbox list: {e}")
            return ['INBOX']
    
    def test_connection(self) -> Dict[str, bool]:
        """Test both IMAP and SMTP connections"""
        results = {'imap': False, 'smtp': False}
        
        # Test IMAP
        try:
            mail = self.connect_imap()
            mail.logout()
            results['imap'] = True
        except:
            pass
        
        # Test SMTP
        try:
            server = self.connect_smtp()
            server.quit()
            results['smtp'] = True
        except:
            pass
        
        return results

# Global email service instance
email_service = EmailService()