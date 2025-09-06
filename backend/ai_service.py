# AI service for sentiment analysis and response generation using OpenAI
import openai
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from config import config

class AIService:
    """Handles OpenAI API integration for email AI processing"""
    
    def __init__(self):
        try:
            # Try different OpenAI client initialization methods
            if hasattr(openai, 'OpenAI'):
                # Initialize with explicit proxy settings to avoid the error
                self.openai_client = openai.OpenAI(
                    api_key=config.openai.api_key,
                    timeout=30.0,
                    http_client=None  # Disable any automatic proxy detection
                )
                print("✅ OpenAI client initialized successfully")
            else:
                # Fallback for older versions
                openai.api_key = config.openai.api_key
                self.openai_client = None
                print("✅ OpenAI client initialized (legacy mode)")
        except Exception as e:
            print(f"⚠️  OpenAI client initialization failed: {e}")
            # Try with minimal configuration
            try:
                self.openai_client = openai.OpenAI(api_key=config.openai.api_key)
                print("✅ OpenAI client initialized with minimal config")
            except Exception as e2:
                print(f"⚠️  OpenAI client fallback failed: {e2}")
                self.openai_client = None
        
        self.model = config.openai.model
        self.max_tokens = config.openai.max_tokens
        self.temperature = config.openai.temperature
    
    def analyze_sentiment(self, email_content: str, subject: str = "") -> Dict[str, any]:
        """Analyze email sentiment using OpenAI"""
        try:
            prompt = f"""
            Analyze the sentiment of this email and provide a detailed assessment:
            
            Subject: {subject}
            Content: {email_content}
            
            Please provide your analysis in the following JSON format:
            {{
                "sentiment": "positive|negative|neutral",
                "score": -1.0 to 1.0,
                "confidence": 0.0 to 1.0,
                "key_emotions": ["frustrated", "urgent", "polite"],
                "reasoning": "Brief explanation of the sentiment analysis"
            }}
            """
            
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert at analyzing email sentiment and emotions. Respond only with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.3
                )
            else:
                # Fallback for older OpenAI versions
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert at analyzing email sentiment and emotions. Respond only with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.3
                )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                result = json.loads(result_text)
                
                # Validate and set defaults
                result['sentiment'] = result.get('sentiment', 'neutral').lower()
                result['score'] = max(-1.0, min(1.0, float(result.get('score', 0.0))))
                result['confidence'] = max(0.0, min(1.0, float(result.get('confidence', 0.8))))
                result['key_emotions'] = result.get('key_emotions', [])
                result['reasoning'] = result.get('reasoning', 'No reasoning provided')
                
                return result
                
            except json.JSONDecodeError:
                # Fallback parsing if JSON is malformed
                return self._fallback_sentiment_analysis(result_text)
            
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'key_emotions': [],
                'reasoning': f'Error: {str(e)}'
            }
    
    def _fallback_sentiment_analysis(self, text: str) -> Dict[str, any]:
        """Fallback sentiment analysis using keyword matching"""
        positive_keywords = ['thank', 'appreciate', 'great', 'excellent', 'good', 'pleased', 'satisfied']
        negative_keywords = ['urgent', 'critical', 'problem', 'issue', 'error', 'frustrated', 'angry', 'broken']
        
        text_lower = text.lower()
        positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
        
        if negative_count > positive_count:
            return {
                'sentiment': 'negative',
                'score': -0.6,
                'confidence': 0.5,
                'key_emotions': ['concerned'],
                'reasoning': 'Fallback analysis based on keywords'
            }
        elif positive_count > negative_count:
            return {
                'sentiment': 'positive', 
                'score': 0.6,
                'confidence': 0.5,
                'key_emotions': ['satisfied'],
                'reasoning': 'Fallback analysis based on keywords'
            }
        else:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.3,
                'key_emotions': [],
                'reasoning': 'Fallback analysis - no clear sentiment'
            }
    
    def generate_response(self, email_data: Dict, context: str = "", use_rag: bool = True) -> Dict[str, any]:
        """Generate appropriate response using OpenAI with optional RAG enhancement"""
        try:
            if use_rag and RAG_AVAILABLE:
                # Use RAG service for enhanced response generation
                return rag_service.generate_rag_response(email_data)
            else:
                # Use original method without RAG
                return self._generate_basic_response(email_data, context)
                
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                'response': self._generate_fallback_response(email_data),
                'confidence': 0.3,
                'generated_at': datetime.now().isoformat(),
                'model_used': 'fallback',
                'error': str(e)
            }
    
    def _generate_basic_response(self, email_data: Dict, context: str = "") -> Dict[str, any]:
        """Generate basic response without RAG (original method)"""
        try:
            # Extract sentiment information for context
            sentiment = email_data.get('sentiment', 'neutral')
            key_emotions = email_data.get('key_emotions', [])
            priority = email_data.get('priority', 'normal')
            
            # Build context-aware prompt
            prompt = f"""
            You are a professional customer support representative. Generate an appropriate email response based on the following:
            
            Original Email:
            From: {email_data.get('sender', 'Unknown')}
            Subject: {email_data.get('subject', 'No subject')}
            Content: {email_data.get('body', '')}
            
            Email Analysis:
            - Sentiment: {sentiment}
            - Priority: {priority}
            - Key emotions detected: {', '.join(key_emotions) if key_emotions else 'None'}
            
            Additional Context: {context}
            
            Instructions:
            1. Acknowledge the customer's concern empathetically
            2. Be professional yet friendly
            3. If the customer seems frustrated, acknowledge their feelings
            4. For urgent issues, prioritize quick resolution
            5. Provide helpful information or next steps
            6. Keep the response concise but complete
            7. End with an offer to help further
            
            Generate a professional email response (200-300 words maximum):
            """
            
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a professional customer support representative who writes empathetic and helpful email responses."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
            else:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a professional customer support representative who writes empathetic and helpful email responses."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
            
            generated_response = response.choices[0].message.content.strip()
            
            # Calculate confidence based on sentiment analysis confidence
            base_confidence = email_data.get('confidence', 0.8)
            response_confidence = min(0.95, base_confidence + 0.1)
            
            return {
                'response': generated_response,
                'confidence': response_confidence,
                'generated_at': datetime.now().isoformat(),
                'model_used': self.model,
                'context_considered': {
                    'sentiment': sentiment,
                    'priority': priority,
                    'emotions': key_emotions
                }
            }
            
        except Exception as e:
            print(f"Error generating basic response: {e}")
            return {
                'response': self._generate_fallback_response(email_data),
                'confidence': 0.3,
                'generated_at': datetime.now().isoformat(),
                'model_used': 'fallback',
                'error': str(e)
            }
    
    def _generate_fallback_response(self, email_data: Dict) -> str:
        """Generate a basic fallback response"""
        sender_name = email_data.get('sender', 'Customer').split('<')[0].strip()
        if not sender_name or '@' in sender_name:
            sender_name = "Customer"
            
        priority = email_data.get('priority', 'normal')
        
        if priority == 'urgent':
            return f"""Dear {sender_name},

Thank you for contacting our support team. I understand this is an urgent matter and I want to assure you that we're taking your concern seriously.

We have received your message and our team is working to address your issue as quickly as possible. We'll provide you with an update within the next few hours.

In the meantime, if you have any additional information that might help us resolve this faster, please don't hesitate to reply to this email.

Thank you for your patience.

Best regards,
Support Team"""
        else:
            return f"""Dear {sender_name},

Thank you for reaching out to our support team. We have received your message and appreciate you taking the time to contact us.

Our team will review your inquiry and get back to you with a detailed response within 24 hours. We're committed to providing you with the best possible assistance.

If you have any urgent concerns in the meantime, please don't hesitate to contact us.

Best regards,
Support Team"""
    
    def categorize_email(self, email_content: str, subject: str = "") -> Dict[str, any]:
        """Categorize email into support categories"""
        try:
            prompt = f"""
            Categorize this customer support email into one of the following categories:
            
            Categories:
            - Technical Issue
            - Billing Question
            - Account Access
            - Feature Request
            - General Inquiry
            - Complaint
            - Compliment
            - Other
            
            Email Subject: {subject}
            Email Content: {email_content}
            
            Respond with JSON format:
            {{
                "category": "category name",
                "subcategory": "more specific classification",
                "confidence": 0.0 to 1.0,
                "keywords": ["relevant", "keywords", "found"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at categorizing customer support emails. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.2
            )
            
            result_text = response.choices[0].message.content.strip()
            
            try:
                result = json.loads(result_text)
                result['confidence'] = max(0.0, min(1.0, float(result.get('confidence', 0.8))))
                return result
            except json.JSONDecodeError:
                return {
                    'category': 'General Inquiry',
                    'subcategory': 'Uncategorized',
                    'confidence': 0.3,
                    'keywords': []
                }
                
        except Exception as e:
            print(f"Error in email categorization: {e}")
            return {
                'category': 'General Inquiry',
                'subcategory': 'Error',
                'confidence': 0.0,
                'keywords': []
            }
    
    def extract_key_information(self, email_content: str) -> Dict[str, any]:
        """Extract key information from email using OpenAI"""
        try:
            prompt = f"""
            Extract key information from this customer support email:
            
            Email Content: {email_content}
            
            Please extract and return in JSON format:
            {{
                "customer_name": "name if mentioned",
                "contact_info": "phone/email if provided",
                "product_mentioned": "product or service mentioned",
                "issue_summary": "brief summary of the main issue",
                "requested_action": "what the customer wants",
                "deadline_mentioned": "any time constraints mentioned",
                "account_info": "account numbers or IDs mentioned"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured information from emails. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            try:
                return json.loads(result_text)
            except json.JSONDecodeError:
                return {
                    'customer_name': '',
                    'contact_info': '',
                    'product_mentioned': '',
                    'issue_summary': 'Unable to extract',
                    'requested_action': '',
                    'deadline_mentioned': '',
                    'account_info': ''
                }
                
        except Exception as e:
            print(f"Error extracting key information: {e}")
            return {
                'error': str(e)
            }
    
    def process_email_complete(self, email_data: Dict) -> Dict[str, any]:
        """Complete AI processing of an email"""
        # Perform sentiment analysis
        sentiment_result = self.analyze_sentiment(
            email_data['body'], 
            email_data.get('subject', '')
        )
        
        # Add sentiment data to email
        email_data.update({
            'sentiment': sentiment_result['sentiment'],
            'sentiment_score': sentiment_result['score'],
            'confidence': sentiment_result['confidence'],
            'key_emotions': sentiment_result['key_emotions']
        })
        
        # Categorize email
        category_result = self.categorize_email(
            email_data['body'],
            email_data.get('subject', '')
        )
        
        # Extract key information
        key_info = self.extract_key_information(email_data['body'])
        
        # Generate response
        response_result = self.generate_response(email_data)
        
        return {
            'sentiment': sentiment_result,
            'category': category_result,
            'key_information': key_info,
            'generated_response': response_result,
            'processing_completed_at': datetime.now().isoformat()
        }
    
    def analyze_email(self, email_data: Dict) -> Dict[str, any]:
        """Complete email analysis including sentiment, priority, and categorization"""
        try:
            # Perform sentiment analysis
            sentiment_result = self.analyze_sentiment(
                email_data['body'], 
                email_data.get('subject', '')
            )
            
            # Determine priority based on content and sentiment
            priority = self.determine_priority(email_data)
            
            # Categorize email
            category_result = self.categorize_email(
                email_data['body'],
                email_data.get('subject', '')
            )
            
            # Extract key information
            key_info = self.extract_key_information(email_data['body'])
            
            return {
                'sentiment': sentiment_result['sentiment'],
                'sentiment_score': sentiment_result['score'],
                'confidence': sentiment_result['confidence'],
                'key_emotions': sentiment_result['key_emotions'],
                'priority': priority,
                'category': category_result['category'],
                'subcategory': category_result['subcategory'],
                'key_information': key_info,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error in email analysis: {e}")
            return {
                'sentiment': 'neutral',
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'key_emotions': [],
                'priority': 'normal',
                'category': 'General Inquiry',
                'subcategory': 'Error',
                'key_information': {},
                'error': str(e)
            }
    
    def determine_priority(self, email_data: Dict) -> str:
        """Determine email priority based on content analysis"""
        try:
            subject = email_data.get('subject', '').lower()
            body = email_data.get('body', '').lower()
            text_to_analyze = f"{subject} {body}"
            
            # High priority keywords
            urgent_keywords = [
                'urgent', 'critical', 'asap', 'immediately', 'emergency',
                'cannot access', 'not working', 'down', 'broken', 'error',
                'hacked', 'security', 'breach', 'fraud', 'stolen'
            ]
            
            # Medium priority keywords
            important_keywords = [
                'help', 'support', 'issue', 'problem', 'question',
                'billing', 'payment', 'refund', 'cancel', 'upgrade'
            ]
            
            # Check for urgent keywords
            for keyword in urgent_keywords:
                if keyword in text_to_analyze:
                    return 'urgent'
            
            # Check for important keywords
            for keyword in important_keywords:
                if keyword in text_to_analyze:
                    return 'normal'
            
            # Default to low priority
            return 'low'
            
        except Exception as e:
            print(f"Error determining priority: {e}")
            return 'normal'

# Global AI service instance
ai_service = AIService()