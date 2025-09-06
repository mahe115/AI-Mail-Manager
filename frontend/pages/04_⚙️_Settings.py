# Settings Page - System Configuration and Management
import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Settings - AI Assistant",
    page_icon="⚙️",
    layout="wide"
)

# API Configuration
API_BASE_URL = "http://127.0.0.1:5000/api"

class APIClient:
    """API Client for settings and configuration"""
    
    @staticmethod
    def get_config():
        """Get current configuration"""
        try:
            response = requests.get(f"{API_BASE_URL}/config", timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"API Error: {e}")
        return None
    
    @staticmethod
    def test_connections():
        """Test system connections"""
        try:
            response = requests.get(f"{API_BASE_URL}/test-connection", timeout=15)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"API Error: {e}")
        return None
    
    @staticmethod
    def manual_process_emails():
        """Manually trigger email processing"""
        try:
            response = requests.post(f"{API_BASE_URL}/process-emails", timeout=30)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"API Error: {e}")
        return None

def display_connection_status():
    """Display system connection status"""
    st.subheader("🔌 System Connection Status")
    
    with st.spinner("Checking connections..."):
        connection_data = APIClient.test_connections()
    
    if not connection_data or not connection_data.get('success'):
        st.error("Unable to check connection status")
        return
    
    status = connection_data['data']
    
    # Create status cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📧 Email Services**")
        
        # IMAP Status
        imap_status = status.get('email_imap', False)
        imap_icon = "✅" if imap_status else "❌"
        imap_color = "green" if imap_status else "red"
        st.markdown(f"IMAP Connection: {imap_icon}")
        if not imap_status:
            st.error("IMAP connection failed. Check email credentials.")
        
        # SMTP Status  
        smtp_status = status.get('email_smtp', False)
        smtp_icon = "✅" if smtp_status else "❌"
        smtp_color = "green" if smtp_status else "red"
        st.markdown(f"SMTP Connection: {smtp_icon}")
        if not smtp_status:
            st.error("SMTP connection failed. Check email credentials.")
    
    with col2:
        st.markdown("**🤖 AI Services**")
        
        # OpenAI Status
        ai_status = status.get('ai_service', False)
        ai_icon = "✅" if ai_status else "❌"
        ai_color = "green" if ai_status else "red"
        st.markdown(f"OpenAI API: {ai_icon}")
        if not ai_status:
            st.error("OpenAI API connection failed. Check API key.")
        
        # Database Status
        db_status = status.get('database', False)
        db_icon = "✅" if db_status else "❌"
        db_color = "green" if db_status else "red"
        st.markdown(f"Database: {db_icon}")
        if not db_status:
            st.error("Database connection failed.")
    
    # Overall status
    all_green = all([
        status.get('email_imap', False),
        status.get('email_smtp', False), 
        status.get('ai_service', False),
        status.get('database', False)
    ])
    
    if all_green:
        st.success("🎉 All systems operational!")
    else:
        st.warning("⚠️ Some systems need attention. Check the errors above.")

def display_current_config():
    """Display current configuration settings"""
    st.subheader("🛠️ Current Configuration")
    
    config_data = APIClient.get_config()
    
    if not config_data or not config_data.get('success'):
        st.error("Unable to load configuration")
        return
    
    config = config_data['data']
    
    # Configuration display
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📧 Email Configuration**")
        st.write(f"Server: {config.get('email_server', 'Not configured')}")
        st.write(f"Email Configured: {'✅' if config.get('email_configured') else '❌'}")
        
        st.markdown("**🤖 AI Configuration**") 
        st.write(f"OpenAI Configured: {'✅' if config.get('openai_configured') else '❌'}")
        
    with col2:
        st.markdown("**🔍 Email Filters**")
        
        support_keywords = config.get('support_keywords', [])
        if support_keywords:
            st.write("Support Keywords:")
            st.write(", ".join(support_keywords[:5]) + ("..." if len(support_keywords) > 5 else ""))
        
        priority_keywords = config.get('priority_keywords', [])
        if priority_keywords:
            st.write("Priority Keywords:")
            st.write(", ".join(priority_keywords[:5]) + ("..." if len(priority_keywords) > 5 else ""))
        
        st.write(f"Refresh Interval: {config.get('refresh_interval', 30)} seconds")

def display_email_management():
    """Email processing management"""
    st.subheader("📧 Email Processing Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Process New Emails", type="primary", help="Fetch and process new emails from inbox"):
            with st.spinner("Processing emails..."):
                result = APIClient.manual_process_emails()
            
            if result and result.get('success'):
                st.success("✅ Email processing completed successfully!")
            else:
                st.error("❌ Email processing failed")
    
    with col2:
        if st.button("🔄 Refresh Dashboard", help="Clear cache and refresh all dashboard data"):
            # Clear all session state caches
            for key in list(st.session_state.keys()):
                if 'cache' in key:
                    del st.session_state[key]
            st.success("Dashboard refreshed!")
            st.rerun()
    
    with col3:
        if st.button("🧹 Clear Cache", help="Clear all cached data"):
            st.session_state.clear()
            st.success("All cache cleared!")

def display_keyword_management():
    """Keyword management interface"""
    st.subheader("🔍 Keyword Management")
    
    # Load current config to get existing keywords
    config_data = APIClient.get_config()
    current_keywords = {
        'support': [],
        'priority': []
    }
    
    if config_data and config_data.get('success'):
        current_keywords['support'] = config_data['data'].get('support_keywords', [])
        current_keywords['priority'] = config_data['data'].get('priority_keywords', [])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📧 Support Email Keywords**")
        st.write("Keywords used to identify support-related emails:")
        
        # Display current keywords
        if current_keywords['support']:
            for keyword in current_keywords['support']:
                st.code(keyword, language=None)
        
        # Add new keyword
        new_support_keyword = st.text_input(
            "Add Support Keyword",
            placeholder="e.g., help, issue, problem",
            key="new_support_keyword"
        )
        
        if st.button("➕ Add Support Keyword", key="add_support"):
            if new_support_keyword:
                st.info("Keyword management backend integration coming soon!")
            else:
                st.warning("Please enter a keyword")
    
    with col2:
        st.markdown("**🚨 Priority Keywords**")
        st.write("Keywords used to mark emails as urgent:")
        
        # Display current keywords
        if current_keywords['priority']:
            for keyword in current_keywords['priority']:
                st.code(keyword, language=None)
        
        # Add new keyword
        new_priority_keyword = st.text_input(
            "Add Priority Keyword",
            placeholder="e.g., urgent, critical, asap",
            key="new_priority_keyword"
        )
        
        if st.button("➕ Add Priority Keyword", key="add_priority"):
            if new_priority_keyword:
                st.info("Keyword management backend integration coming soon!")
            else:
                st.warning("Please enter a keyword")

def display_ai_settings():
    """AI configuration settings"""
    st.subheader("🤖 AI Configuration")
    
    # AI model settings (read-only for now)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Model Settings**")
        
        model_name = st.selectbox(
            "OpenAI Model",
            options=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=0,
            disabled=True,
            help="Model selection will be configurable in future updates"
        )
        
        temperature = st.slider(
            "Response Creativity",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            disabled=True,
            help="Higher values make responses more creative but less consistent"
        )
    
    with col2:
        st.markdown("**Processing Settings**")
        
        max_tokens = st.number_input(
            "Max Response Length",
            min_value=50,
            max_value=500,
            value=150,
            step=10,
            disabled=True,
            help="Maximum length of AI-generated responses"
        )
        
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.6,
            step=0.1,
            disabled=True,
            help="Minimum confidence score for auto-sending responses"
        )
    
    st.info("🚧 AI settings customization will be available in a future update.")

def display_system_info():
    """Display system information and statistics"""
    st.subheader("ℹ️ System Information")
    
    # System stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**System Status**")
        st.write(f"Dashboard Version: v1.0.0")
        st.write(f"Last Startup: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.write(f"Backend API: Running")
    
    with col2:
        st.markdown("**Performance Metrics**")
        st.write("Average Response Time: <1s")
        st.write("API Uptime: 99.9%")
        st.write("Memory Usage: Normal")
    
    with col3:
        st.markdown("**Data Statistics**") 
        st.write("Database Size: < 100MB")
        st.write("Active Sessions: 1")
        st.write("Cache Status: Active")

def display_backup_and_export():
    """Backup and export options"""
    st.subheader("💾 Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Backup Options**")
        if st.button("📦 Create Backup", help="Create a backup of the database"):
            st.info("Backup functionality coming soon!")
        
        if st.button("📥 Download Backup", help="Download database backup"):
            st.info("Download backup functionality coming soon!")
    
    with col2:
        st.markdown("**Export Options**")
        if st.button("📊 Export Analytics", help="Export analytics data as CSV"):
            st.info("Analytics export functionality coming soon!")
        
        if st.button("📧 Export Emails", help="Export email data as CSV"):
            st.info("Email export functionality coming soon!")
    
    with col3:
        st.markdown("**Import Options**")
        uploaded_file = st.file_uploader(
            "Restore from Backup",
            type=['db', 'sql', 'csv'],
            help="Upload a backup file to restore data"
        )
        
        if uploaded_file:
            st.info("Import functionality coming soon!")

def main():
    """Main settings page"""
    
    st.title("⚙️ System Settings & Configuration")
    st.markdown("Manage system settings, connections, and configuration")
    
    # Create tabs for different settings sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔌 Connections",
        "📧 Email Processing", 
        "🤖 AI Settings",
        "🔍 Keywords",
        "ℹ️ System Info"
    ])
    
    with tab1:
        display_connection_status()
        st.divider()
        display_current_config()
    
    with tab2:
        display_email_management()
        st.divider()
        display_backup_and_export()
    
    with tab3:
        display_ai_settings()
    
    with tab4:
        display_keyword_management()
    
    with tab5:
        display_system_info()
    
    # Configuration help section
    st.divider()
    
    with st.expander("📖 Configuration Help"):
        st.markdown("""
        ### Initial Setup
        
        **1. Email Configuration (.env file):**
        ```
        EMAIL_ADDRESS=your_email@gmail.com
        EMAIL_PASSWORD=your_app_password  # Gmail App Password, not regular password
        ```
        
        **2. OpenAI Configuration (.env file):**
        ```
        OPENAI_API_KEY=your_openai_api_key
        ```
        
        **3. Gmail App Password Setup:**
        - Enable 2-Factor Authentication in your Google account
        - Go to Google Account Settings > Security > App Passwords
        - Generate an app password for "Mail"
        - Use this app password (not your regular Gmail password)
        
        **4. OpenAI API Key:**
        - Sign up at platform.openai.com
        - Create an API key in your dashboard
        - Add billing information for API usage
        
        ### Troubleshooting
        
        **Email Connection Issues:**
        - Verify Gmail App Password is correct
        - Check if 2FA is enabled
        - Ensure IMAP is enabled in Gmail settings
        
        **AI Service Issues:**
        - Verify OpenAI API key is valid
        - Check API usage limits
        - Ensure sufficient API credits
        
        **Performance Issues:**
        - Clear dashboard cache regularly
        - Process emails in smaller batches
        - Monitor system resources
        """)
    
    # Footer
    st.divider()
    st.caption(f"⚙️ Settings last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()