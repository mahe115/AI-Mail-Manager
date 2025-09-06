# RAG (Retrieval-Augmented Generation) Service for AI-Powered Communication Assistant
import os
import json
import openai
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import sqlite3
import numpy as np
import logging
from config import config

# Try to import sentence transformers with fallback
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    print("✅ SentenceTransformers import successful")
except ImportError as e:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print(f"⚠️  SentenceTransformers not available - using fallback embedding: {e}")
except Exception as e:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print(f"⚠️  SentenceTransformers import error - using fallback embedding: {e}")

# Try to import sklearn with fallback
try:
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  Scikit-learn not available - using fallback similarity")

logger = logging.getLogger(__name__)

class RAGService:
    """Retrieval-Augmented Generation service for enhanced AI responses"""
    
    def __init__(self):
        try:
            if hasattr(openai, 'OpenAI'):
                # Initialize with explicit proxy settings to avoid the error
                self.openai_client = openai.OpenAI(
                    api_key=config.openai.api_key,
                    timeout=30.0,
                    http_client=None  # Disable any automatic proxy detection
                )
                print("✅ RAG OpenAI client initialized successfully")
            else:
                openai.api_key = config.openai.api_key
                self.openai_client = None
                print("✅ RAG OpenAI client initialized (legacy mode)")
        except Exception as e:
            print(f"⚠️  RAG OpenAI client initialization failed: {e}")
            # Try with minimal configuration
            try:
                self.openai_client = openai.OpenAI(api_key=config.openai.api_key)
                print("✅ RAG OpenAI client initialized with minimal config")
            except Exception as e2:
                print(f"⚠️  RAG OpenAI client fallback failed: {e2}")
                self.openai_client = None
        
        self.model = config.openai.model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ SentenceTransformer loaded successfully")
            except Exception as e:
                print(f"⚠️  Could not load SentenceTransformer: {e} - using fallback embedding")
                self.embedding_model = None
        else:
            print("⚠️  SentenceTransformer not available - using fallback embedding")
            self.embedding_model = None
        self.knowledge_db_path = "database/knowledge.db"
        self.embeddings_cache = {}
        self.init_knowledge_database()
    
    def init_knowledge_database(self):
        """Initialize knowledge base database"""
        os.makedirs(os.path.dirname(self.knowledge_db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        # Knowledge documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                tags TEXT,  -- JSON array
                embedding BLOB,  -- Serialized numpy array
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Document chunks table for better retrieval
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                embedding BLOB,
                FOREIGN KEY (document_id) REFERENCES knowledge_documents (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize with default knowledge if empty
        self._initialize_default_knowledge()
    
    def _initialize_default_knowledge(self):
        """Initialize with default FAQ and knowledge"""
        if self.get_document_count() == 0:
            default_knowledge = [
                {
                    "title": "Account Access Issues",
                    "content": "If you're having trouble accessing your account, please try resetting your password using the 'Forgot Password' link on the login page. If the issue persists, contact our support team with your account email address.",
                    "category": "Account Support",
                    "tags": ["account", "login", "password", "access"]
                },
                {
                    "title": "Billing Questions",
                    "content": "For billing inquiries, please check your account dashboard for recent transactions. If you have questions about charges or need to update payment methods, our billing team can assist you within 24 hours.",
                    "category": "Billing",
                    "tags": ["billing", "payment", "charges", "invoice"]
                },
                {
                    "title": "Technical Support",
                    "content": "For technical issues, please provide detailed information about the problem, including error messages, browser type, and steps to reproduce the issue. Our technical team will investigate and provide a solution.",
                    "category": "Technical",
                    "tags": ["technical", "error", "bug", "issue", "support"]
                },
                {
                    "title": "Feature Requests",
                    "content": "We welcome feature requests and suggestions. Please describe the feature you'd like to see, how it would benefit you, and any specific requirements. Our product team reviews all requests.",
                    "category": "Product",
                    "tags": ["feature", "request", "suggestion", "improvement"]
                },
                {
                    "title": "Refund Policy",
                    "content": "Refunds are processed within 5-7 business days for eligible requests. To request a refund, please contact our support team with your order number and reason for the refund request.",
                    "category": "Billing",
                    "tags": ["refund", "money", "return", "policy"]
                }
            ]
            
            for knowledge in default_knowledge:
                self.add_document(
                    title=knowledge["title"],
                    content=knowledge["content"],
                    category=knowledge["category"],
                    tags=knowledge["tags"]
                )
    
    def add_document(self, title: str, content: str, category: str, tags: List[str] = None) -> int:
        """Add a new document to the knowledge base"""
        try:
            # Generate embedding for the content
            embedding = self._generate_embedding(content)
            
            # Store in database
            conn = sqlite3.connect(self.knowledge_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO knowledge_documents (title, content, category, tags, embedding)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                title,
                content,
                category,
                json.dumps(tags or []),
                embedding.tobytes()
            ))
            
            document_id = cursor.lastrowid
            
            # Create chunks for better retrieval
            self._create_document_chunks(document_id, content, embedding)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Added document: {title}")
            return document_id
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return None
    
    def _create_document_chunks(self, document_id: int, content: str, full_embedding: np.ndarray):
        """Create smaller chunks of the document for better retrieval"""
        # Split content into sentences
        sentences = content.split('. ')
        chunk_size = 3  # 3 sentences per chunk
        
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        for i in range(0, len(sentences), chunk_size):
            chunk_text = '. '.join(sentences[i:i+chunk_size])
            if not chunk_text.endswith('.'):
                chunk_text += '.'
            
            # Generate embedding for chunk
            chunk_embedding = self._generate_embedding(chunk_text)
            
            cursor.execute('''
                INSERT INTO document_chunks (document_id, chunk_text, chunk_index, embedding)
                VALUES (?, ?, ?, ?)
            ''', (document_id, chunk_text, i // chunk_size, chunk_embedding.tobytes()))
        
        conn.commit()
        conn.close()
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text using sentence transformers"""
        try:
            if self.embedding_model is None:
                # Fallback to simple hash-based embedding
                import hashlib
                hash_obj = hashlib.md5(text.encode())
                hash_bytes = hash_obj.digest()
                # Convert to numpy array
                embedding = np.frombuffer(hash_bytes, dtype=np.uint8).astype(np.float32)
                # Pad or truncate to 384 dimensions
                if len(embedding) < 384:
                    embedding = np.pad(embedding, (0, 384 - len(embedding)), 'constant')
                else:
                    embedding = embedding[:384]
                return embedding
            
            embedding = self.embedding_model.encode(text)
            return embedding.astype(np.float32)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return np.zeros(384, dtype=np.float32)  # Default embedding size
    
    def retrieve_relevant_knowledge(self, query: str, top_k: int = 3) -> List[Dict]:
        """Retrieve relevant knowledge based on query"""
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Search in document chunks
            conn = sqlite3.connect(self.knowledge_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT dc.chunk_text, dc.document_id, kd.title, kd.category, kd.tags
                FROM document_chunks dc
                JOIN knowledge_documents kd ON dc.document_id = kd.id
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                return []
            
            # Calculate similarities
            similarities = []
            for chunk_text, doc_id, title, category, tags in results:
                # Get chunk embedding (simplified - in production, store these)
                chunk_embedding = self._generate_embedding(chunk_text)
                
                if SKLEARN_AVAILABLE:
                    similarity = cosine_similarity(
                        query_embedding.reshape(1, -1),
                        chunk_embedding.reshape(1, -1)
                    )[0][0]
                else:
                    # Fallback similarity calculation
                    similarity = np.dot(query_embedding, chunk_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
                    )
                
                similarities.append({
                    'text': chunk_text,
                    'document_id': doc_id,
                    'title': title,
                    'category': category,
                    'tags': json.loads(tags) if tags else [],
                    'similarity': similarity
                })
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error retrieving knowledge: {e}")
            return []
    
    def generate_rag_response(self, email_data: Dict, retrieved_knowledge: List[Dict] = None) -> Dict:
        """Generate response using RAG with retrieved knowledge"""
        try:
            if not retrieved_knowledge:
                retrieved_knowledge = self.retrieve_relevant_knowledge(
                    f"{email_data.get('subject', '')} {email_data.get('body', '')}"
                )
            
            # Build context from retrieved knowledge
            context = ""
            if retrieved_knowledge:
                context = "Relevant Knowledge Base Information:\n"
                for i, knowledge in enumerate(retrieved_knowledge, 1):
                    context += f"{i}. {knowledge['title']} ({knowledge['category']}): {knowledge['text']}\n"
                context += "\n"
            
            # Enhanced prompt with RAG context
            prompt = f"""
            You are a professional customer support representative. Generate an appropriate email response using the provided knowledge base information.
            
            Original Email:
            From: {email_data.get('sender', 'Unknown')}
            Subject: {email_data.get('subject', 'No subject')}
            Content: {email_data.get('body', '')}
            
            Email Analysis:
            - Sentiment: {email_data.get('sentiment', 'neutral')}
            - Priority: {email_data.get('priority', 'normal')}
            - Key emotions: {', '.join(email_data.get('key_emotions', []))}
            
            {context}
            
            Instructions:
            1. Use the knowledge base information above to provide accurate, helpful responses
            2. If the knowledge base contains relevant information, reference it appropriately
            3. Maintain a professional and empathetic tone
            4. If the customer seems frustrated, acknowledge their feelings
            5. For urgent issues, prioritize quick resolution
            6. Provide specific next steps when possible
            7. Keep the response concise but complete (200-300 words)
            8. End with an offer to help further
            
            Generate a professional email response:
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional customer support representative who writes empathetic and helpful email responses using provided knowledge base information."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=config.openai.max_tokens,
                temperature=config.openai.temperature
            )
            
            generated_response = response.choices[0].message.content.strip()
            
            # Calculate confidence based on knowledge retrieval
            knowledge_confidence = max([k['similarity'] for k in retrieved_knowledge]) if retrieved_knowledge else 0.0
            base_confidence = email_data.get('confidence', 0.8)
            response_confidence = min(0.95, base_confidence + (knowledge_confidence * 0.2))
            
            return {
                'response': generated_response,
                'confidence': response_confidence,
                'generated_at': datetime.now().isoformat(),
                'model_used': self.model,
                'knowledge_used': len(retrieved_knowledge),
                'knowledge_sources': [k['title'] for k in retrieved_knowledge],
                'context_considered': {
                    'sentiment': email_data.get('sentiment', 'neutral'),
                    'priority': email_data.get('priority', 'normal'),
                    'emotions': email_data.get('key_emotions', [])
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {e}")
            return {
                'response': self._generate_fallback_response(email_data),
                'confidence': 0.3,
                'generated_at': datetime.now().isoformat(),
                'model_used': 'fallback',
                'error': str(e)
            }
    
    def _generate_fallback_response(self, email_data: Dict) -> str:
        """Generate fallback response when RAG fails"""
        sender_name = email_data.get('sender', 'Customer').split('<')[0].strip()
        if not sender_name or '@' in sender_name:
            sender_name = "Customer"
        
        return f"""Dear {sender_name},

Thank you for contacting our support team. We have received your message and appreciate you taking the time to contact us.

Our team will review your inquiry and get back to you with a detailed response within 24 hours. We're committed to providing you with the best possible assistance.

If you have any urgent concerns in the meantime, please don't hesitate to contact us.

Best regards,
Support Team"""
    
    def get_document_count(self) -> int:
        """Get total number of documents in knowledge base"""
        try:
            conn = sqlite3.connect(self.knowledge_db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM knowledge_documents')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents from knowledge base"""
        try:
            conn = sqlite3.connect(self.knowledge_db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, content, category, tags, created_at, updated_at
                FROM knowledge_documents
                ORDER BY updated_at DESC
            ''')
            
            documents = []
            for row in cursor.fetchall():
                documents.append({
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'category': row[3],
                    'tags': json.loads(row[4]) if row[4] else [],
                    'created_at': row[5],
                    'updated_at': row[6]
                })
            
            conn.close()
            return documents
            
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            return []
    
    def update_document(self, doc_id: int, title: str = None, content: str = None, 
                       category: str = None, tags: List[str] = None) -> bool:
        """Update an existing document"""
        try:
            conn = sqlite3.connect(self.knowledge_db_path)
            cursor = conn.cursor()
            
            # Build update query dynamically
            updates = []
            params = []
            
            if title is not None:
                updates.append("title = ?")
                params.append(title)
            
            if content is not None:
                updates.append("content = ?")
                params.append(content)
                # Regenerate embedding for updated content
                embedding = self._generate_embedding(content)
                updates.append("embedding = ?")
                params.append(embedding.tobytes())
            
            if category is not None:
                updates.append("category = ?")
                params.append(category)
            
            if tags is not None:
                updates.append("tags = ?")
                params.append(json.dumps(tags))
            
            if not updates:
                return False
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(doc_id)
            
            query = f"UPDATE knowledge_documents SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            
            # Update chunks if content changed
            if content is not None:
                cursor.execute('DELETE FROM document_chunks WHERE document_id = ?', (doc_id,))
                self._create_document_chunks(doc_id, content, self._generate_embedding(content))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated document ID: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return False
    
    def delete_document(self, doc_id: int) -> bool:
        """Delete a document from knowledge base"""
        try:
            conn = sqlite3.connect(self.knowledge_db_path)
            cursor = conn.cursor()
            
            # Delete chunks first (foreign key constraint)
            cursor.execute('DELETE FROM document_chunks WHERE document_id = ?', (doc_id,))
            
            # Delete document
            cursor.execute('DELETE FROM knowledge_documents WHERE id = ?', (doc_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Deleted document ID: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False

# Global RAG service instance
rag_service = RAGService()
