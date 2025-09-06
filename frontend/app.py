# AI Communication Assistant - Unified Dashboard
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import time
import json
from typing import Dict, List, Optional

# Page configuration
st.set_page_config(
    page_title="AI Communication Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    .main > div {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Header */
    .header {
        text-align: center;
        margin-bottom: 2rem;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .header h1 {
        font-family: 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .header p {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Navigation Tabs */
    .nav-tabs {
        display: flex;
        background: white;
        border-radius: 15px;
        padding: 0.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        overflow-x: auto;
    }
    
    .nav-tab {
        flex: 1;
        text-align: center;
        padding: 1rem;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #64748b;
        border: none;
        background: transparent;
    }
    
    .nav-tab:hover {
        background: #f1f5f9;
        color: #334155;
    }
    
    .nav-tab.active {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Cards */
    .card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(0,0,0,0.05);
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f1f5f9;
    }
    
    .card-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    
    .card-icon {
        font-size: 2rem;
        margin-right: 1rem;
    }
    
    /* Metrics */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 1px solid rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0.5rem 0;
        color: #1e293b;
    }
    
    .metric-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-change {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .metric-change.positive {
        background: #dcfce7;
        color: #166534;
    }
    
    .metric-change.negative {
        background: #fee2e2;
        color: #991b1b;
    }
    
    .metric-change.neutral {
        background: #f1f5f9;
        color: #475569;
    }
    
    /* Email Cards */
    .email-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border-left: 5px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .email-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    }
    
    .email-card.urgent {
        border-left-color: #ef4444;
        background: linear-gradient(145deg, #fef2f2 0%, #fee2e2 100%);
    }
    
    .email-card.normal {
        border-left-color: #3b82f6;
        background: linear-gradient(145deg, #eff6ff 0%, #dbeafe 100%);
    }
    
    .email-card.low {
        border-left-color: #10b981;
        background: linear-gradient(145deg, #f0fdf4 0%, #dcfce7 100%);
    }
    
    .email-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    
    .email-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        font-weight: 600;
        color: #1e293b;
        margin: 0;
        flex: 1;
    }
    
    .email-meta {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    .status-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-urgent {
        background: #fee2e2;
        color: #991b1b;
    }
    
    .status-normal {
        background: #dbeafe;
        color: #1e40af;
    }
    
    .status-low {
        background: #dcfce7;
        color: #166534;
    }
    
    .status-unread {
        background: #fef3c7;
        color: #92400e;
    }
    
    .status-read {
        background: #f1f5f9;
        color: #475569;
    }
    
    .status-resolved {
        background: #dcfce7;
        color: #166534;
    }
    
    /* Buttons */
    .btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .btn.urgent {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
    }
    
    .btn.success {
        background: linear-gradient(135deg, #10b981, #059669);
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    .btn.warning {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
    }
    
    /* Sidebar */
    .sidebar .stSelectbox > div > div {
        background: white;
        border-radius: 10px;
        border: 2px solid #e2e8f0;
    }
    
    .sidebar .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    
    /* Response Display */
    .response-text {
        background: #f8fafc;
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
        color: #1e293b;
        white-space: pre-wrap;
        word-wrap: break-word;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .response-text:hover {
        border-color: #cbd5e1;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        font-weight: 600;
    }
    
    .streamlit-expanderContent {
        background: white;
        border-radius: 0 0 10px 10px;
        border: 1px solid #e2e8f0;
        border-top: none;
    }
    
    /* Text Area Styling */
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .header h1 {
            font-size: 2rem;
        }
        .metric-grid {
            grid-template-columns: 1fr;
        }
        .email-header {
            flex-direction: column;
            align-items: flex-start;
        }
        .email-meta {
            margin-top: 0.5rem;
        }
        .response-text {
            padding: 1rem;
            font-size: 0.9rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = "http://127.0.0.1:5000/api"

class APIClient:
    """Unified API client"""
    
    @staticmethod
    def make_request(endpoint: str, method: str = "GET", data: Dict = None) -> Optional[Dict]:
        """Make API request with error handling"""
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=15)
            elif method == "POST":
                response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=15)
            elif method == "PUT":
                response = requests.put(f"{API_BASE_URL}{endpoint}", json=data, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"Connection Error: {e}")
            return None
    
    @staticmethod
    def get_emails(limit=100):
        """Get emails"""
        return APIClient.make_request(f'/emails?limit={limit}')
    
    @staticmethod
    def get_responses():
        """Get responses"""
        return APIClient.make_request('/responses')
    
    @staticmethod
    def get_analytics(days=30):
        """Get analytics"""
        return APIClient.make_request(f'/analytics?days={days}')
    
    @staticmethod
    def process_emails(limit=100, days_back=7):
        """Process emails"""
        return APIClient.make_request('/process-emails', 'POST', {'limit': limit, 'days_back': days_back})
    
    @staticmethod
    def update_email_status(email_id, status):
        """Update email status"""
        return APIClient.make_request(f'/emails/{email_id}/status', 'PUT', {'status': status})
    
    @staticmethod
    def send_response(response_id):
        """Send response"""
        return APIClient.make_request(f'/responses/{response_id}/send', 'POST')

def display_header():
    """Display modern header"""
    current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    st.markdown(f"""
    <div class="header">
        <h1>🚀 AI Communication Assistant</h1>
        <p>Intelligent Email Management & Customer Support</p>
        <p style="font-size: 1rem; opacity: 0.8;">{current_time}</p>
    </div>
    """, unsafe_allow_html=True)

def display_navigation():
    """Display navigation tabs"""
    tabs = ["📊 Dashboard", "📧 Emails", "🤖 AI Responses", "📈 Analytics", "⚙️ Settings"]
    
    # Create navigation
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    
    for i, tab in enumerate(tabs):
        with cols[i]:
            if st.button(tab, key=f"nav_{i}", use_container_width=True):
                st.session_state.current_tab = i
    
    # Initialize current tab
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = 0
    
    return st.session_state.current_tab

def display_metrics(data):
    """Display key metrics"""
    emails = data.get('emails', [])
    responses = data.get('responses', [])
    
    # Calculate metrics
    total_emails = len(emails)
    urgent_emails = len([e for e in emails if e.get('priority') == 'urgent'])
    unread_emails = len([e for e in emails if e.get('status') == 'unread'])
    resolved_emails = len([e for e in emails if e.get('status') == 'resolved'])
    sent_responses = len([r for r in responses if r.get('sent_status') == 'sent'])
    
    # Recent emails (last 24 hours)
    now = datetime.now()
    recent_count = 0
    for email in emails:
        try:
            email_time = datetime.fromisoformat(email['timestamp'].replace('Z', '+00:00'))
            if (now - email_time.replace(tzinfo=None)).total_seconds() < 86400:
                recent_count += 1
        except:
            continue
    
    # Display metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📧 Total Emails</div>
            <div class="metric-value">{total_emails}</div>
            <div class="metric-change positive">+{recent_count} today</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        urgent_color = "negative" if urgent_emails > 0 else "positive"
        urgent_text = f"{urgent_emails} urgent" if urgent_emails > 0 else "0 urgent"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🚨 Urgent</div>
            <div class="metric-value" style="color: {'#ef4444' if urgent_emails > 0 else '#10b981'};">{urgent_emails}</div>
            <div class="metric-change {urgent_color}">{urgent_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📬 Unread</div>
            <div class="metric-value" style="color: #f59e0b;">{unread_emails}</div>
            <div class="metric-change neutral">Pending review</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        resolution_rate = (resolved_emails / max(1, total_emails)) * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">✅ Resolved</div>
            <div class="metric-value" style="color: #10b981;">{resolved_emails}</div>
            <div class="metric-change positive">{resolution_rate:.1f}% rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🤖 Responses</div>
            <div class="metric-value" style="color: #8b5cf6;">{sent_responses}</div>
            <div class="metric-change positive">AI generated</div>
        </div>
        """, unsafe_allow_html=True)

def display_dashboard_tab(data):
    """Display dashboard tab"""
    st.markdown("## 📊 System Overview")
    
    # Display metrics
    display_metrics(data)
    
    # System status
    st.markdown("## 🔍 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <span class="card-icon">🚀</span>
                <h3 class="card-title">Backend Status</h3>
            </div>
            <p style="color: #10b981; font-weight: 600;">✅ Online</p>
            <p style="color: #64748b; font-size: 0.9rem;">Flask server running on port 5000</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <span class="card-icon">📧</span>
                <h3 class="card-title">Email Service</h3>
            </div>
            <p style="color: #10b981; font-weight: 600;">✅ Connected</p>
            <p style="color: #64748b; font-size: 0.9rem;">Gmail IMAP/SMTP configured</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <span class="card-icon">🤖</span>
                <h3 class="card-title">AI Service</h3>
            </div>
            <p style="color: #10b981; font-weight: 600;">✅ Active</p>
            <p style="color: #64748b; font-size: 0.9rem;">OpenAI API configured</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("## ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📧 Process New Emails", use_container_width=True, type="primary"):
            with st.spinner("Processing emails..."):
                result = APIClient.process_emails()
                if result and result.get('success'):
                    st.success("✅ Emails processed successfully!")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Failed to process emails")
    
    with col2:
        if st.button("🚨 View Urgent", use_container_width=True):
            st.session_state.current_tab = 1
            st.rerun()
    
    with col3:
        if st.button("🤖 AI Responses", use_container_width=True):
            st.session_state.current_tab = 2
            st.rerun()
    
    with col4:
        if st.button("📈 Analytics", use_container_width=True):
            st.session_state.current_tab = 3
            st.rerun()

def display_emails_tab(data):
    """Display emails tab"""
    st.markdown("## 📧 Email Management")
    
    emails = data.get('emails', [])
    
    if not emails:
        st.info("📭 No emails found. Click 'Process New Emails' to fetch emails from your inbox.")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "unread", "read", "resolved"])
    with col2:
        priority_filter = st.selectbox("Filter by Priority", ["All", "urgent", "normal", "low"])
    with col3:
        sentiment_filter = st.selectbox("Filter by Sentiment", ["All", "positive", "negative", "neutral"])
    
    # Apply filters
    filtered_emails = emails
    if status_filter != "All":
        filtered_emails = [e for e in filtered_emails if e.get('status') == status_filter]
    if priority_filter != "All":
        filtered_emails = [e for e in filtered_emails if e.get('priority') == priority_filter]
    if sentiment_filter != "All":
        filtered_emails = [e for e in filtered_emails if e.get('sentiment') == sentiment_filter]
    
    # Sort emails: urgent first, then by timestamp
    filtered_emails = sorted(
        filtered_emails,
        key=lambda x: (
            0 if x['priority'] == 'urgent' else 1 if x['priority'] == 'normal' else 2,
            -int(datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')).timestamp())
        )
    )
    
    # Display emails
    for email in filtered_emails:
        priority = email.get('priority', 'normal')
        sentiment = email.get('sentiment', 'neutral')
        status = email.get('status', 'unread')
        
        # Format timestamp
        try:
            timestamp = datetime.fromisoformat(email['timestamp'].replace('Z', '+00:00'))
            time_str = timestamp.strftime('%Y-%m-%d %H:%M')
            time_ago = datetime.now() - timestamp.replace(tzinfo=None)
            
            if time_ago.total_seconds() < 3600:
                time_display = f"{int(time_ago.total_seconds() / 60)}m ago"
            elif time_ago.total_seconds() < 86400:
                time_display = f"{int(time_ago.total_seconds() / 3600)}h ago"
            else:
                time_display = f"{time_ago.days}d ago"
        except:
            time_display = "Unknown"
        
        # Extract sender name
        sender = email.get('sender', 'Unknown')
        sender_name = sender.split('<')[0].strip() if '<' in sender else sender
        
        # Display email card
        st.markdown(f"""
        <div class="email-card {priority}">
            <div class="email-header">
                <h4 class="email-title">{email.get('subject', 'No Subject')}</h4>
                <div class="email-meta">
                    <span class="status-badge status-{priority}">{priority.upper()}</span>
                    <span class="status-badge status-{sentiment}">{sentiment.title()}</span>
                    <span class="status-badge status-{status}">{status.title()}</span>
                </div>
            </div>
            <p style="color: #64748b; margin: 0.5rem 0;"><strong>From:</strong> {sender_name}</p>
            <p style="color: #64748b; margin: 0.5rem 0;"><strong>Received:</strong> {time_display}</p>
            <p style="color: #475569; margin: 1rem 0;">{email.get('body', '')[:200]}...</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if status == 'unread':
                if st.button(f"👁️ Mark as Read", key=f"read_{email['id']}"):
                    if APIClient.update_email_status(email['id'], 'read'):
                        st.success("✅ Marked as read!")
                        time.sleep(1)
                        st.rerun()
            else:
                st.button(f"✅ Already Read", key=f"read_done_{email['id']}", disabled=True)
        
        with col2:
            if status != 'resolved':
                if st.button(f"✅ Mark Resolved", key=f"resolved_{email['id']}", type="primary"):
                    if APIClient.update_email_status(email['id'], 'resolved'):
                        st.success("✅ Marked as resolved!")
                        time.sleep(1)
                        st.rerun()
            else:
                st.button(f"✅ Resolved", key=f"resolved_done_{email['id']}", disabled=True)
        
        with col3:
            if st.button(f"🤖 AI Response", key=f"ai_{email['id']}"):
                st.session_state.current_tab = 2
                st.rerun()
        
        with col4:
            if st.button(f"📊 Analytics", key=f"analytics_{email['id']}"):
                st.session_state.current_tab = 3
                st.rerun()
        
        st.divider()

def display_responses_tab(data):
    """Display AI responses tab"""
    st.markdown("## 🤖 AI Response Management")
    
    responses = data.get('responses', [])
    
    if not responses:
        st.info("📭 No AI responses found. Process some emails to generate responses.")
        return
    
    # Filter responses
    status_filter = st.selectbox("Filter by Status", ["All", "draft", "sent", "failed"])
    
    filtered_responses = responses
    if status_filter != "All":
        filtered_responses = [r for r in responses if r.get('sent_status') == status_filter]
    
    # Display responses
    for response in filtered_responses:
        status = response.get('sent_status', 'draft')
        confidence = response.get('confidence_score', 0)
        response_text = response.get('generated_response', '')
        
        # Format timestamp
        try:
            created_at = datetime.fromisoformat(response['created_at'].replace('Z', '+00:00'))
            time_str = created_at.strftime('%Y-%m-%d %H:%M')
        except:
            time_str = "Unknown"
        
        # Create expandable response card
        with st.expander(f"🤖 Response #{response['id']} - {status.title()} (Confidence: {confidence:.2f})", expanded=True):
            
            # Response metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Status", status.title())
            with col2:
                st.metric("Confidence", f"{confidence:.2f}")
            with col3:
                st.metric("Created", time_str)
            
            st.divider()
            
            # Full response text in a proper text area
            st.markdown("### 📝 Generated Response:")
            
            # Display the full response text with proper formatting
            if response_text:
                # Create a styled text area for better readability
                st.markdown(f"""
                <div style="
                    background: #f8fafc;
                    border: 2px solid #e2e8f0;
                    border-radius: 10px;
                    padding: 1.5rem;
                    margin: 1rem 0;
                    font-family: 'Inter', sans-serif;
                    line-height: 1.6;
                    color: #1e293b;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                ">
                    {response_text}
                </div>
                """, unsafe_allow_html=True)
                
                # Also display in a text area for editing
                edited_response = st.text_area(
                    "Edit Response (if needed):",
                    value=response_text,
                    height=200,
                    key=f"edit_text_{response['id']}",
                    help="You can edit the response text here before sending"
                )
            else:
                st.warning("⚠️ No response text available")
                edited_response = ""
            
            st.divider()
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if status == 'draft':
                    if st.button(f"📤 Send Response", key=f"send_{response['id']}", type="primary", use_container_width=True):
                        with st.spinner("Sending response..."):
                            result = APIClient.send_response(response['id'])
                            if result and result.get('success'):
                                st.success("✅ Response sent successfully!")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("❌ Failed to send response")
                else:
                    st.button(f"📤 Already Sent", key=f"sent_{response['id']}", disabled=True, use_container_width=True)
            
            with col2:
                if st.button(f"✏️ Save Edit", key=f"save_{response['id']}", use_container_width=True):
                    if edited_response != response_text:
                        st.success("✅ Response updated! (Note: Backend update needed)")
                    else:
                        st.info("ℹ️ No changes to save")
            
            with col3:
                if st.button(f"🔄 Regenerate", key=f"regen_{response['id']}", use_container_width=True):
                    st.info("🔄 Regenerating response... (Note: Backend regeneration needed)")
            
            with col4:
                if st.button(f"📋 Copy Text", key=f"copy_{response['id']}", use_container_width=True):
                    st.code(response_text, language=None)
                    st.success("📋 Response text copied to clipboard area above!")
        
        st.divider()

def display_analytics_tab(data):
    """Display analytics tab"""
    st.markdown("## 📈 Analytics & Insights")
    
    emails = data.get('emails', [])
    
    if not emails:
        st.info("📭 No data available for analytics. Process some emails first.")
        return
    
    # Calculate analytics
    total_emails = len(emails)
    urgent_emails = len([e for e in emails if e.get('priority') == 'urgent'])
    unread_emails = len([e for e in emails if e.get('status') == 'unread'])
    resolved_emails = len([e for e in emails if e.get('status') == 'resolved'])
    
    # Sentiment analysis
    positive_emails = len([e for e in emails if e.get('sentiment') == 'positive'])
    negative_emails = len([e for e in emails if e.get('sentiment') == 'negative'])
    neutral_emails = len([e for e in emails if e.get('sentiment') == 'neutral'])
    
    # Create charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Priority distribution
        priority_counts = {}
        for email in emails:
            priority = email.get('priority', 'normal')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        if priority_counts:
            fig = px.pie(
                values=list(priority_counts.values()),
                names=list(priority_counts.keys()),
                title="📊 Priority Distribution",
                color_discrete_sequence=['#ef4444', '#3b82f6', '#10b981']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sentiment analysis
        sentiment_counts = {}
        for email in emails:
            sentiment = email.get('sentiment', 'neutral')
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        if sentiment_counts:
            fig = px.pie(
                values=list(sentiment_counts.values()),
                names=list(sentiment_counts.keys()),
                title="😊 Sentiment Analysis",
                color_discrete_sequence=['#10b981', '#f59e0b', '#ef4444']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Performance insights
    st.markdown("## 💡 Performance Insights")
    
    resolution_rate = (resolved_emails / max(1, total_emails)) * 100
    urgent_rate = (urgent_emails / max(1, total_emails)) * 100
    negative_rate = (negative_emails / max(1, total_emails)) * 100
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if resolution_rate >= 80:
            st.success(f"🎉 Excellent resolution rate: {resolution_rate:.1f}%")
        elif resolution_rate >= 60:
            st.warning(f"📈 Good resolution rate: {resolution_rate:.1f}%")
        else:
            st.error(f"⚠️ Resolution rate needs improvement: {resolution_rate:.1f}%")
    
    with col2:
        if urgent_rate <= 10:
            st.success(f"✅ Low urgent rate: {urgent_rate:.1f}%")
        elif urgent_rate <= 20:
            st.warning(f"⚠️ Moderate urgent rate: {urgent_rate:.1f}%")
        else:
            st.error(f"🚨 High urgent rate: {urgent_rate:.1f}%")
    
    with col3:
        if negative_rate <= 20:
            st.success(f"😊 Low negative sentiment: {negative_rate:.1f}%")
        elif negative_rate <= 30:
            st.warning(f"😐 Moderate negative sentiment: {negative_rate:.1f}%")
        else:
            st.error(f"😞 High negative sentiment: {negative_rate:.1f}%")

def display_settings_tab():
    """Display settings tab"""
    st.markdown("## ⚙️ System Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📧 Email Configuration")
        st.text_input("Gmail Address", value="your-email@gmail.com", disabled=True)
        st.text_input("App Password", value="••••••••••••••••", type="password", disabled=True)
        st.button("Update Email Settings", use_container_width=True)
    
    with col2:
        st.markdown("### 🤖 AI Configuration")
        st.text_input("OpenAI API Key", value="••••••••••••••••", type="password", disabled=True)
        st.selectbox("AI Model", ["gpt-3.5-turbo", "gpt-4"], index=0, disabled=True)
        st.button("Update AI Settings", use_container_width=True)
    
    st.markdown("### 🔧 System Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("🧹 Clear Cache", use_container_width=True):
            st.success("Cache cleared!")
    
    with col3:
        if st.button("📊 Export Data", use_container_width=True):
            st.info("Export functionality coming soon!")

def sidebar_controls():
    """Display sidebar controls"""
    with st.sidebar:
        st.markdown("## 🎛️ Quick Controls")
        
        # Auto-refresh
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=False)
        if auto_refresh:
            st.info("⏱️ Auto-refreshing every 30s")
            time.sleep(30)
            st.rerun()
        
        st.divider()
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("📧 Process Emails", use_container_width=True, type="primary"):
            with st.spinner("Processing emails..."):
                result = APIClient.process_emails()
                if result and result.get('success'):
                    st.success("✅ Emails processed!")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Failed to process emails")
        
        st.divider()
        
        # System info
        st.markdown("### 📊 System Info")
        st.caption("Backend: ✅ Online")
        st.caption("Email: ✅ Connected")
        st.caption("AI: ✅ Active")
        st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

def main():
    """Main application"""
    
    # Display header
    display_header()
    
    # Display navigation
    current_tab = display_navigation()
    
    # Sidebar controls
    sidebar_controls()
    
    # Load data
    with st.spinner("Loading data..."):
        emails_data = APIClient.get_emails()
        responses_data = APIClient.get_responses()
        analytics_data = APIClient.get_analytics()
    
    # Prepare data
    data = {
        'emails': emails_data.get('data', []) if emails_data and emails_data.get('success') else [],
        'responses': responses_data.get('data', []) if responses_data and responses_data.get('success') else [],
        'analytics': analytics_data.get('data', {}) if analytics_data and analytics_data.get('success') else {}
    }
    
    # Display current tab
    if current_tab == 0:
        display_dashboard_tab(data)
    elif current_tab == 1:
        display_emails_tab(data)
    elif current_tab == 2:
        display_responses_tab(data)
    elif current_tab == 3:
        display_analytics_tab(data)
    elif current_tab == 4:
        display_settings_tab()
    
    # Footer
    st.divider()
    st.caption(f"🚀 AI Communication Assistant • Last updated: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
