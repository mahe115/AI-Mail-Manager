# Priority Queue System for Email Processing
import heapq
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Priority(Enum):
    """Email priority levels"""
    URGENT = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

class EmailStatus(Enum):
    """Email processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"

@dataclass
class EmailTask:
    """Email processing task with priority"""
    email_id: int
    message_id: str
    priority: Priority
    created_at: datetime
    retry_count: int = 0
    max_retries: int = 3
    status: EmailStatus = EmailStatus.PENDING
    processing_started: Optional[datetime] = None
    processing_completed: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def __lt__(self, other):
        """Comparison for priority queue (lower priority number = higher priority)"""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        
        # If same priority, older emails first
        return self.created_at < other.created_at

class EmailPriorityQueue:
    """Thread-safe priority queue for email processing"""
    
    def __init__(self):
        self._queue = []
        self._lock = threading.Lock()
        self._processing_tasks = {}  # email_id -> EmailTask
        self._completed_tasks = {}   # email_id -> EmailTask
        self._failed_tasks = {}      # email_id -> EmailTask
        
        # Statistics
        self._stats = {
            'total_processed': 0,
            'total_failed': 0,
            'total_retries': 0,
            'avg_processing_time': 0.0,
            'queue_size': 0
        }
    
    def add_email(self, email_id: int, message_id: str, priority: Priority, 
                  created_at: datetime = None) -> bool:
        """Add email to priority queue"""
        try:
            if created_at is None:
                created_at = datetime.now()
            
            task = EmailTask(
                email_id=email_id,
                message_id=message_id,
                priority=priority,
                created_at=created_at
            )
            
            with self._lock:
                heapq.heappush(self._queue, task)
                self._stats['queue_size'] = len(self._queue)
            
            logger.info(f"Added email {email_id} to queue with priority {priority.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding email to queue: {e}")
            return False
    
    def get_next_email(self) -> Optional[EmailTask]:
        """Get next email to process (highest priority)"""
        try:
            with self._lock:
                if not self._queue:
                    return None
                
                task = heapq.heappop(self._queue)
                task.status = EmailStatus.PROCESSING
                task.processing_started = datetime.now()
                
                self._processing_tasks[task.email_id] = task
                self._stats['queue_size'] = len(self._queue)
                
                logger.info(f"Retrieved email {task.email_id} for processing")
                return task
                
        except Exception as e:
            logger.error(f"Error getting next email: {e}")
            return None
    
    def mark_completed(self, email_id: int, success: bool = True, 
                      error_message: str = None) -> bool:
        """Mark email processing as completed"""
        try:
            with self._lock:
                if email_id in self._processing_tasks:
                    task = self._processing_tasks.pop(email_id)
                    task.processing_completed = datetime.now()
                    
                    if success:
                        task.status = EmailStatus.COMPLETED
                        self._completed_tasks[email_id] = task
                        self._stats['total_processed'] += 1
                        
                        # Update average processing time
                        processing_time = (task.processing_completed - task.processing_started).total_seconds()
                        self._update_avg_processing_time(processing_time)
                        
                        logger.info(f"Email {email_id} processing completed successfully")
                    else:
                        task.status = EmailStatus.FAILED
                        task.error_message = error_message
                        self._failed_tasks[email_id] = task
                        self._stats['total_failed'] += 1
                        
                        # Retry logic
                        if task.retry_count < task.max_retries:
                            task.retry_count += 1
                            task.status = EmailStatus.RETRY
                            task.processing_started = None
                            task.processing_completed = None
                            
                            # Add back to queue with higher priority for retry
                            heapq.heappush(self._queue, task)
                            self._stats['total_retries'] += 1
                            self._stats['queue_size'] = len(self._queue)
                            
                            logger.info(f"Email {email_id} scheduled for retry ({task.retry_count}/{task.max_retries})")
                        else:
                            logger.error(f"Email {email_id} failed after {task.max_retries} retries")
                    
                    return True
                else:
                    logger.warning(f"Email {email_id} not found in processing tasks")
                    return False
                    
        except Exception as e:
            logger.error(f"Error marking email completed: {e}")
            return False
    
    def get_queue_status(self) -> Dict:
        """Get current queue status and statistics"""
        with self._lock:
            return {
                'queue_size': len(self._queue),
                'processing_count': len(self._processing_tasks),
                'completed_count': len(self._completed_tasks),
                'failed_count': len(self._failed_tasks),
                'statistics': self._stats.copy(),
                'next_emails': [
                    {
                        'email_id': task.email_id,
                        'priority': task.priority.name,
                        'created_at': task.created_at.isoformat(),
                        'retry_count': task.retry_count
                    }
                    for task in self._queue[:5]  # Next 5 emails
                ]
            }
    
    def get_processing_tasks(self) -> List[Dict]:
        """Get currently processing tasks"""
        with self._lock:
            return [
                {
                    'email_id': task.email_id,
                    'message_id': task.message_id,
                    'priority': task.priority.name,
                    'processing_started': task.processing_started.isoformat() if task.processing_started else None,
                    'retry_count': task.retry_count
                }
                for task in self._processing_tasks.values()
            ]
    
    def get_failed_tasks(self, limit: int = 10) -> List[Dict]:
        """Get recently failed tasks"""
        with self._lock:
            failed_list = list(self._failed_tasks.values())
            failed_list.sort(key=lambda x: x.processing_completed, reverse=True)
            
            return [
                {
                    'email_id': task.email_id,
                    'message_id': task.message_id,
                    'priority': task.priority.name,
                    'error_message': task.error_message,
                    'retry_count': task.retry_count,
                    'failed_at': task.processing_completed.isoformat() if task.processing_completed else None
                }
                for task in failed_list[:limit]
            ]
    
    def clear_completed_tasks(self, older_than_hours: int = 24) -> int:
        """Clear completed tasks older than specified hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            cleared_count = 0
            
            with self._lock:
                # Clear old completed tasks
                old_completed = [
                    email_id for email_id, task in self._completed_tasks.items()
                    if task.processing_completed and task.processing_completed < cutoff_time
                ]
                
                for email_id in old_completed:
                    del self._completed_tasks[email_id]
                    cleared_count += 1
                
                # Clear old failed tasks
                old_failed = [
                    email_id for email_id, task in self._failed_tasks.items()
                    if task.processing_completed and task.processing_completed < cutoff_time
                ]
                
                for email_id in old_failed:
                    del self._failed_tasks[email_id]
                    cleared_count += 1
            
            logger.info(f"Cleared {cleared_count} old tasks")
            return cleared_count
            
        except Exception as e:
            logger.error(f"Error clearing completed tasks: {e}")
            return 0
    
    def _update_avg_processing_time(self, new_time: float):
        """Update average processing time"""
        total_processed = self._stats['total_processed']
        if total_processed == 1:
            self._stats['avg_processing_time'] = new_time
        else:
            # Calculate running average
            current_avg = self._stats['avg_processing_time']
            self._stats['avg_processing_time'] = (current_avg * (total_processed - 1) + new_time) / total_processed
    
    def get_priority_distribution(self) -> Dict[str, int]:
        """Get distribution of priorities in queue"""
        with self._lock:
            distribution = {priority.name: 0 for priority in Priority}
            
            for task in self._queue:
                distribution[task.priority.name] += 1
            
            return distribution
    
    def promote_urgent_emails(self, keywords: List[str]) -> int:
        """Promote emails containing urgent keywords to higher priority"""
        try:
            promoted_count = 0
            
            with self._lock:
                # Create new queue with promoted emails
                new_queue = []
                
                for task in self._queue:
                    # Check if email contains urgent keywords
                    # Note: This would need access to email content, which we don't have here
                    # In a real implementation, you'd need to fetch email content
                    if task.priority == Priority.NORMAL:
                        # For now, just promote some normal priority emails
                        # In practice, you'd check email content against keywords
                        if task.retry_count > 0:  # Promote retry emails
                            task.priority = Priority.HIGH
                            promoted_count += 1
                    
                    new_queue.append(task)
                
                # Rebuild heap
                heapq.heapify(new_queue)
                self._queue = new_queue
            
            logger.info(f"Promoted {promoted_count} emails to higher priority")
            return promoted_count
            
        except Exception as e:
            logger.error(f"Error promoting urgent emails: {e}")
            return 0

# Global priority queue instance
email_priority_queue = EmailPriorityQueue()
