# Flask API for AI-Powered Communication Assistant
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List
import logging

# Import our modules
from config import config
from database import db
from email_service import email_service
from ai_service import ai_service
from priority_queue import email_priority_queue, Priority
try:
    from rag_service import rag_service
    RAG_AVAILABLE = True
    print("✅ Full RAG service loaded successfully")
except ImportError as e:
    try:
        from rag_service_simple import simple_rag_service as rag_service
        RAG_AVAILABLE = True
        print("✅ Simple RAG service loaded (sentence-transformers not available)")
    except ImportError as e2:
        RAG_AVAILABLE = False
        rag_service = None
        print(f"⚠️  RAG service not available: {e2}")

try:
    from knowledge_base import knowledge_base_manager
    KNOWLEDGE_BASE_AVAILABLE = True
    print("✅ Knowledge base manager loaded successfully")
except ImportError as e:
    KNOWLEDGE_BASE_AVAILABLE = False
    knowledge_base_manager = None
    print(f"⚠️  Knowledge base manager not available: {e}")
except Exception as e:
    KNOWLEDGE_BASE_AVAILABLE = False
    knowledge_base_manager = None
    print(f"⚠️  Knowledge base manager error: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Flask application factory"""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for frontend communication
    
    # Configure Flask app
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    return app

app = create_app()

class EmailProcessor:
    """Background email processing service"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        
    def start(self):
        """Start background email processing"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._process_emails_loop, daemon=True)
            self.thread.start()
            logger.info("Email processor started")
    
    def stop(self):
        """Stop background email processing"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Email processor stopped")
    
    def _process_emails_loop(self):
        """Main processing loop"""
        while self.running:
            try:
                self._fetch_and_process_emails()
                time.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logger.error(f"Error in email processing loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _fetch_and_process_emails(self):
        """Fetch and process new emails"""
        try:
            # Fetch emails from Gmail
            logger.info("Fetching emails...")
            emails = email_service.fetch_emails(limit=20)
            
            processed_count = 0
            for email_data in emails:
                try:
                    # Check if email already exists
                    existing_emails = db.get_emails()
                    existing_message_ids = [e['message_id'] for e in existing_emails]
                    
                    if email_data['message_id'] not in existing_message_ids:
                        # Process with AI
                        ai_results = ai_service.process_email_complete(email_data)
                        
                        # Update email data with AI results
                        email_data.update({
                            'sentiment': ai_results['sentiment']['sentiment'],
                            'sentiment_score': ai_results['sentiment']['score'],
                        })
                        
                        # Insert into database
                        email_id = db.insert_email(email_data)
                        
                        # Generate and store response
                        response_data = {
                            'email_id': email_id,
                            'generated_response': ai_results['generated_response']['response'],
                            'confidence_score': ai_results['generated_response']['confidence']
                        }
                        db.insert_response(response_data)
                        
                        processed_count += 1
                        logger.info(f"Processed email: {email_data['subject'][:50]}...")
                        
                except Exception as e:
                    logger.error(f"Error processing individual email: {e}")
                    continue
            
            if processed_count > 0:
                logger.info(f"Processed {processed_count} new emails")
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")

# Global email processor
email_processor = EmailProcessor()

# API Routes
@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'AI Communication Assistant API'
    })

@app.route('/api/emails', methods=['GET'])
def get_emails():
    """Get emails with optional filtering"""
    try:
        # Get query parameters
        status = request.args.get('status')
        priority = request.args.get('priority') 
        limit = int(request.args.get('limit', 50))
        
        # Fetch emails from database
        emails = db.get_emails(status=status, priority=priority, limit=limit)
        
        return jsonify({
            'success': True,
            'data': emails,
            'count': len(emails)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/emails/<int:email_id>', methods=['GET'])
def get_email_details(email_id):
    """Get detailed email information"""
    try:
        emails = db.get_emails()
        email = next((e for e in emails if e['id'] == email_id), None)
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email not found'
            }), 404
        
        # Get associated responses
        responses = db.get_responses(email_id=email_id)
        
        return jsonify({
            'success': True,
            'data': {
                'email': email,
                'responses': responses
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/emails/<int:email_id>/status', methods=['PUT'])
def update_email_status(email_id):
    """Update email status"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['unread', 'read', 'resolved']:
            return jsonify({
                'success': False,
                'error': 'Invalid status'
            }), 400
        
        db.update_email_status(email_id, new_status)
        
        return jsonify({
            'success': True,
            'message': f'Email status updated to {new_status}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/responses', methods=['GET'])
def get_responses():
    """Get AI-generated responses"""
    try:
        email_id = request.args.get('email_id', type=int)
        responses = db.get_responses(email_id=email_id)
        
        return jsonify({
            'success': True,
            'data': responses
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/responses/<int:response_id>', methods=['PUT'])
def update_response(response_id):
    """Update response content and status"""
    try:
        data = request.get_json()
        edited_response = data.get('edited_response')
        status = data.get('status', 'draft')
        
        db.update_response_status(response_id, status, edited_response)
        
        return jsonify({
            'success': True,
            'message': 'Response updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/responses/<int:response_id>/send', methods=['POST'])
def send_response(response_id):
    """Send email response"""
    try:
        # Get response and email details
        responses = db.get_responses()
        response = next((r for r in responses if r['id'] == response_id), None)
        
        if not response:
            return jsonify({
                'success': False,
                'error': 'Response not found'
            }), 404
        
        # Get email details
        emails = db.get_emails()
        email = next((e for e in emails if e['id'] == response['email_id']), None)
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email not found'
            }), 404
        
        # Extract recipient email from sender
        recipient_email = email['sender'].split('<')[-1].strip('>')
        
        # Use edited response if available, otherwise use generated response
        response_text = response.get('edited_response') or response['generated_response']
        
        # Send email
        success = email_service.send_response(
            to_email=recipient_email,
            subject=email['subject'],
            body=response_text,
            original_message_id=email['message_id']
        )
        
        if success:
            # Update response status
            db.update_response_status(response_id, 'sent')
            
            # Update email status to resolved
            db.update_email_status(email['id'], 'resolved')
            
            return jsonify({
                'success': True,
                'message': 'Response sent successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send email'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data"""
    try:
        days = int(request.args.get('days', 7))
        analytics_data = db.get_analytics_data(days=days)
        
        # Add some real-time metrics
        urgent_count = db.get_urgent_emails_count()
        
        # Get all emails for additional stats
        all_emails = db.get_emails(limit=1000)
        total_emails = len(all_emails)
        unread_count = len([e for e in all_emails if e['status'] == 'unread'])
        resolved_count = len([e for e in all_emails if e['status'] == 'resolved'])
        
        # Calculate sentiment distribution
        sentiment_counts = {}
        for email in all_emails:
            sentiment = email.get('sentiment', 'neutral')
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        analytics_data.update({
            'summary_stats': {
                'total_emails': total_emails,
                'unread_emails': unread_count,
                'resolved_emails': resolved_count,
                'urgent_emails': urgent_count,
                'average_sentiment_score': sum(e.get('sentiment_score', 0) for e in all_emails) / max(1, len(all_emails))
            },
            'realtime_sentiment': sentiment_counts
        })
        
        return jsonify({
            'success': True,
            'data': analytics_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search', methods=['GET'])
def search_emails():
    """Search emails"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        results = db.search_emails(query)
        
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/process-emails', methods=['POST'])
def manual_process_emails():
    """Manually trigger email processing with improved fetching"""
    try:
        # Get parameters from request
        data = request.get_json() or {}
        limit = data.get('limit', 100)
        days_back = data.get('days_back', 7)
        
        # Use improved email fetching
        emails = email_service.fetch_emails(limit=limit, days_back=days_back)
        
        processed_count = 0
        ai_processed_count = 0
        
        for email_data in emails:
            # Check if email already exists
            existing_email = db.get_email_by_message_id(email_data['message_id'])
            
            if not existing_email:
                # Process with AI
                ai_analysis = ai_service.analyze_email(email_data)
                
                # Store in database
                email_id = db.add_email(
                    message_id=email_data['message_id'],
                    thread_id=email_data['thread_id'],
                    sender=email_data['sender'],
                    subject=email_data['subject'],
                    body=email_data['body'],
                    timestamp=email_data['timestamp'],
                    priority=ai_analysis['priority'],
                    sentiment=ai_analysis['sentiment'],
                    sentiment_score=ai_analysis['sentiment_score'],
                    key_emotions=ai_analysis['key_emotions'],
                    confidence=ai_analysis['confidence']
                )
                
                # Generate AI response
                response_data = ai_service.generate_response(email_data, ai_analysis)
                
                # Store response
                db.add_response(
                    email_id=email_id,
                    generated_response=response_data['response'],
                    confidence_score=response_data['confidence'],
                    context_considered=response_data['context_considered']
                )
                
                processed_count += 1
                ai_processed_count += 1
        
        return jsonify({
            'success': True,
            'data': {
                'processed_count': processed_count,
                'ai_processed_count': ai_processed_count,
                'total_emails_fetched': len(emails),
                'days_back': days_back,
                'limit': limit
            },
            'message': f'Processed {processed_count} new emails ({ai_processed_count} with AI analysis)'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/test-connection', methods=['GET'])
def test_connections():
    """Test email and AI service connections"""
    try:
        # Test email connection
        email_results = email_service.test_connection()
        
        # Test AI service (simple test)
        try:
            ai_test = ai_service.analyze_sentiment("This is a test message", "Test")
            ai_status = True
        except:
            ai_status = False
        
        return jsonify({
            'success': True,
            'data': {
                'email_imap': email_results['imap'],
                'email_smtp': email_results['smtp'],
                'ai_service': ai_status,
                'database': True  # If we got here, DB is working
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration (safe values only)"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'email_server': config.email.imap_server,
                'email_configured': bool(config.email.email and config.email.password),
                'openai_configured': bool(config.openai.api_key),
                'support_keywords': config.filters.support_keywords,
                'priority_keywords': config.filters.priority_keywords,
                'refresh_interval': config.streamlit.refresh_interval
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Knowledge Base API Endpoints
@app.route('/api/knowledge', methods=['GET'])
def get_knowledge_documents():
    """Get all knowledge base documents"""
    if not RAG_AVAILABLE or not rag_service:
        return jsonify({
            'success': False,
            'error': 'RAG service not available'
        }), 503
    
    try:
        documents = rag_service.get_all_documents()
        return jsonify({
            'success': True,
            'data': documents,
            'count': len(documents)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/knowledge', methods=['POST'])
def add_knowledge_document():
    """Add new knowledge base document"""
    if not RAG_AVAILABLE or not rag_service:
        return jsonify({
            'success': False,
            'error': 'RAG service not available'
        }), 503
    
    try:
        data = request.get_json()
        
        required_fields = ['title', 'content', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        doc_id = rag_service.add_document(
            title=data['title'],
            content=data['content'],
            category=data['category'],
            tags=data.get('tags', [])
        )
        
        if doc_id:
            return jsonify({
                'success': True,
                'data': {'document_id': doc_id},
                'message': 'Document added successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to add document'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/knowledge/<int:doc_id>', methods=['PUT'])
def update_knowledge_document(doc_id):
    """Update knowledge base document"""
    try:
        data = request.get_json()
        
        success = rag_service.update_document(
            doc_id=doc_id,
            title=data.get('title'),
            content=data.get('content'),
            category=data.get('category'),
            tags=data.get('tags')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Document updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update document'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/knowledge/<int:doc_id>', methods=['DELETE'])
def delete_knowledge_document(doc_id):
    """Delete knowledge base document"""
    try:
        success = rag_service.delete_document(doc_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Document deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete document'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/knowledge/search', methods=['GET'])
def search_knowledge():
    """Search knowledge base documents"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category')
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        results = knowledge_base_manager.search_documents(query, category, limit)
        
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/knowledge/stats', methods=['GET'])
def get_knowledge_stats():
    """Get knowledge base statistics"""
    try:
        stats = knowledge_base_manager.get_knowledge_statistics()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/knowledge/import', methods=['POST'])
def import_knowledge_documents():
    """Bulk import knowledge documents from directory"""
    try:
        data = request.get_json()
        
        directory_path = data.get('directory_path')
        category = data.get('category', 'Imported')
        
        if not directory_path:
            return jsonify({
                'success': False,
                'error': 'Directory path is required'
            }), 400
        
        results = knowledge_base_manager.bulk_import_from_directory(directory_path, category)
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Priority Queue API Endpoints
@app.route('/api/queue/status', methods=['GET'])
def get_queue_status():
    """Get priority queue status and statistics"""
    try:
        status = email_priority_queue.get_queue_status()
        
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/queue/processing', methods=['GET'])
def get_processing_tasks():
    """Get currently processing tasks"""
    try:
        tasks = email_priority_queue.get_processing_tasks()
        
        return jsonify({
            'success': True,
            'data': tasks
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/queue/failed', methods=['GET'])
def get_failed_tasks():
    """Get recently failed tasks"""
    try:
        limit = int(request.args.get('limit', 10))
        tasks = email_priority_queue.get_failed_tasks(limit)
        
        return jsonify({
            'success': True,
            'data': tasks
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/queue/clear', methods=['POST'])
def clear_completed_tasks():
    """Clear old completed tasks"""
    try:
        data = request.get_json() or {}
        older_than_hours = data.get('older_than_hours', 24)
        
        cleared_count = email_priority_queue.clear_completed_tasks(older_than_hours)
        
        return jsonify({
            'success': True,
            'data': {'cleared_count': cleared_count}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Validate configuration
    if not config.validate():
        logger.error("Configuration validation failed")
        exit(1)
    
    # Start email processor
    email_processor.start()
    
    try:
        # Run Flask app
        app.run(
            host=config.FLASK_HOST,
            port=config.FLASK_PORT,
            debug=config.FLASK_DEBUG
        )
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        email_processor.stop()