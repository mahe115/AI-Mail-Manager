# Knowledge Base Management for AI-Powered Communication Assistant
import os
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime

# Try to import RAG service with fallback
try:
    from rag_service import rag_service
    RAG_SERVICE_AVAILABLE = True
except ImportError:
    try:
        from rag_service_simple import simple_rag_service as rag_service
        RAG_SERVICE_AVAILABLE = True
        print("Using simple RAG service for knowledge base")
    except ImportError:
        RAG_SERVICE_AVAILABLE = False
        rag_service = None
        print("RAG service not available for knowledge base")

logger = logging.getLogger(__name__)

class KnowledgeBaseManager:
    """Manages knowledge base operations and document processing"""
    
    def __init__(self):
        self.rag_service = rag_service if RAG_SERVICE_AVAILABLE else None
        self.knowledge_dir = "knowledge_base"
        self.supported_formats = ['.txt', '.md', '.json']
        self.init_knowledge_directory()
    
    def init_knowledge_directory(self):
        """Initialize knowledge base directory structure"""
        directories = [
            self.knowledge_dir,
            os.path.join(self.knowledge_dir, "faqs"),
            os.path.join(self.knowledge_dir, "policies"),
            os.path.join(self.knowledge_dir, "procedures"),
            os.path.join(self.knowledge_dir, "templates")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            
            # Create .gitkeep files to maintain directory structure
            gitkeep_path = os.path.join(directory, ".gitkeep")
            if not os.path.exists(gitkeep_path):
                with open(gitkeep_path, 'w') as f:
                    f.write("# This file keeps the directory in git\n")
    
    def add_document_from_file(self, file_path: str, category: str, 
                              title: str = None, tags: List[str] = None) -> int:
        """Add document from file to knowledge base"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use filename as title if not provided
            if not title:
                title = os.path.basename(file_path).split('.')[0]
            
            # Add to RAG service
            doc_id = self.rag_service.add_document(
                title=title,
                content=content,
                category=category,
                tags=tags or []
            )
            
            logger.info(f"Added document from file: {file_path}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding document from file: {e}")
            return None
    
    def add_document_from_text(self, title: str, content: str, category: str, 
                              tags: List[str] = None) -> int:
        """Add document from text content to knowledge base"""
        try:
            doc_id = self.rag_service.add_document(
                title=title,
                content=content,
                category=category,
                tags=tags or []
            )
            
            logger.info(f"Added document: {title}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding document from text: {e}")
            return None
    
    def bulk_import_from_directory(self, directory_path: str, category: str) -> Dict:
        """Bulk import documents from a directory"""
        results = {
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            if not os.path.exists(directory_path):
                raise FileNotFoundError(f"Directory not found: {directory_path}")
            
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                
                # Skip directories and non-supported files
                if os.path.isdir(file_path):
                    continue
                
                if not any(filename.lower().endswith(fmt) for fmt in self.supported_formats):
                    continue
                
                try:
                    doc_id = self.add_document_from_file(
                        file_path=file_path,
                        category=category,
                        tags=[category.lower(), filename.split('.')[0].lower()]
                    )
                    
                    if doc_id:
                        results['successful'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Failed to add: {filename}")
                        
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Error with {filename}: {str(e)}")
            
            logger.info(f"Bulk import completed: {results['successful']} successful, {results['failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk import: {e}")
            results['errors'].append(f"Bulk import error: {str(e)}")
            return results
    
    def export_document(self, doc_id: int, export_path: str) -> bool:
        """Export a document to file"""
        try:
            documents = self.rag_service.get_all_documents()
            document = next((doc for doc in documents if doc['id'] == doc_id), None)
            
            if not document:
                raise ValueError(f"Document with ID {doc_id} not found")
            
            # Create export content
            export_content = f"# {document['title']}\n\n"
            export_content += f"**Category:** {document['category']}\n"
            export_content += f"**Tags:** {', '.join(document['tags'])}\n"
            export_content += f"**Created:** {document['created_at']}\n"
            export_content += f"**Updated:** {document['updated_at']}\n\n"
            export_content += "---\n\n"
            export_content += document['content']
            
            # Write to file
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(export_content)
            
            logger.info(f"Exported document {doc_id} to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting document: {e}")
            return False
    
    def export_all_documents(self, export_dir: str) -> Dict:
        """Export all documents to a directory"""
        results = {
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            os.makedirs(export_dir, exist_ok=True)
            documents = self.rag_service.get_all_documents()
            
            for document in documents:
                try:
                    # Create filename from title
                    safe_title = "".join(c for c in document['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    filename = f"{safe_title}.md"
                    export_path = os.path.join(export_dir, filename)
                    
                    if self.export_document(document['id'], export_path):
                        results['successful'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Failed to export: {document['title']}")
                        
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Error exporting {document['title']}: {str(e)}")
            
            logger.info(f"Export completed: {results['successful']} successful, {results['failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk export: {e}")
            results['errors'].append(f"Bulk export error: {str(e)}")
            return results
    
    def search_documents(self, query: str, category: str = None, limit: int = 10) -> List[Dict]:
        """Search documents in knowledge base"""
        try:
            # Get all documents
            all_documents = self.rag_service.get_all_documents()
            
            # Filter by category if specified
            if category:
                all_documents = [doc for doc in all_documents if doc['category'].lower() == category.lower()]
            
            # Use RAG service to find relevant documents
            relevant_knowledge = self.rag_service.retrieve_relevant_knowledge(query, top_k=limit)
            
            # Map back to full documents
            relevant_docs = []
            for knowledge in relevant_knowledge:
                doc = next((d for d in all_documents if d['id'] == knowledge['document_id']), None)
                if doc:
                    doc['similarity_score'] = knowledge['similarity']
                    relevant_docs.append(doc)
            
            return relevant_docs
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_knowledge_statistics(self) -> Dict:
        """Get knowledge base statistics"""
        try:
            documents = self.rag_service.get_all_documents()
            
            # Count by category
            category_counts = {}
            total_documents = len(documents)
            
            for doc in documents:
                category = doc['category']
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Calculate average content length
            avg_content_length = sum(len(doc['content']) for doc in documents) / max(1, total_documents)
            
            return {
                'total_documents': total_documents,
                'category_distribution': category_counts,
                'average_content_length': avg_content_length,
                'last_updated': max(doc['updated_at'] for doc in documents) if documents else None
            }
            
        except Exception as e:
            logger.error(f"Error getting knowledge statistics: {e}")
            return {
                'total_documents': 0,
                'category_distribution': {},
                'average_content_length': 0,
                'last_updated': None
            }
    
    def create_faq_template(self, question: str, answer: str, category: str = "FAQ") -> int:
        """Create a FAQ document from question and answer"""
        try:
            content = f"**Question:** {question}\n\n**Answer:** {answer}"
            tags = ["faq", "question", "answer", category.lower()]
            
            doc_id = self.rag_service.add_document(
                title=f"FAQ: {question[:50]}...",
                content=content,
                category=category,
                tags=tags
            )
            
            logger.info(f"Created FAQ: {question[:30]}...")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error creating FAQ: {e}")
            return None
    
    def create_policy_template(self, title: str, content: str, tags: List[str] = None) -> int:
        """Create a policy document"""
        try:
            default_tags = ["policy", "guidelines", "rules"]
            if tags:
                default_tags.extend(tags)
            
            doc_id = self.rag_service.add_document(
                title=title,
                content=content,
                category="Policy",
                tags=default_tags
            )
            
            logger.info(f"Created policy: {title}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error creating policy: {e}")
            return None
    
    def validate_document_content(self, content: str) -> Dict:
        """Validate document content quality"""
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'suggestions': []
        }
        
        try:
            # Check content length
            if len(content) < 50:
                validation_results['warnings'].append("Content is very short (less than 50 characters)")
            elif len(content) > 10000:
                validation_results['warnings'].append("Content is very long (more than 10,000 characters)")
            
            # Check for basic structure
            if not any(char in content for char in ['.', '!', '?']):
                validation_results['warnings'].append("Content may lack proper sentence structure")
            
            # Check for common issues
            if content.count('\n') < 2 and len(content) > 200:
                validation_results['suggestions'].append("Consider adding line breaks for better readability")
            
            # Check for placeholder text
            placeholder_indicators = ['TODO', 'FIXME', 'PLACEHOLDER', 'INSERT', 'REPLACE']
            for indicator in placeholder_indicators:
                if indicator in content.upper():
                    validation_results['warnings'].append(f"Content contains placeholder text: {indicator}")
            
            # Overall validation
            if validation_results['errors']:
                validation_results['is_valid'] = False
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating content: {e}")
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Validation error: {str(e)}")
            return validation_results

# Global knowledge base manager instance
knowledge_base_manager = KnowledgeBaseManager()

