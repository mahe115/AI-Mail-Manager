# AI-Powered Communication Assistant - Complete Setup Guide

## 🚀 **Quick Start (5 Minutes)**

### Prerequisites
- Python 3.9 or higher
- Gmail account with App Password
- OpenAI API key
- Git (optional, for version control)

### Step 1: Clone/Download Project
```bash
# If using Git
git clone <your-repository-url>
cd ai-communication-assistant

# Or download and extract the project files
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv mailassistant_env

# Activate virtual environment
# On Windows:
mailassistant_env\Scripts\activate
# On macOS/Linux:
source mailassistant_env/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Copy environment template
copy env.example .env

# Edit .env file with your credentials
```

### Step 5: Run the System
```bash
# Start backend (Terminal 1)
cd backend
python app.py

# Start frontend (Terminal 2)
cd frontend
streamlit run streamlit_app.py
```

### Step 6: Access Dashboard
- Open browser: http://localhost:8501
- Backend API: http://localhost:5000

---

## 📋 **Detailed Setup Instructions**

### 1. Environment Setup

#### Python Installation
- Download Python 3.9+ from [python.org](https://python.org)
- Ensure Python is added to PATH
- Verify installation: `python --version`

#### Virtual Environment
```bash
# Create virtual environment
python -m venv mailassistant_env

# Activate (Windows)
mailassistant_env\Scripts\activate

# Activate (macOS/Linux)
source mailassistant_env/bin/activate

# Verify activation (should show virtual env path)
where python  # Windows
which python  # macOS/Linux
```

### 2. Dependencies Installation

#### Install from requirements.txt
```bash
pip install -r requirements.txt
```

#### Manual Installation (if needed)
```bash
# Core dependencies
pip install Flask==3.0.0 Flask-CORS==4.0.0
pip install streamlit==1.28.1 plotly==5.17.0
pip install pandas==2.1.3 numpy==1.25.2

# AI/ML dependencies
pip install openai==1.6.1 tiktoken==0.5.2
pip install sentence-transformers==2.2.2 scikit-learn==1.3.2

# Utility dependencies
pip install python-dotenv==1.0.0 requests==2.31.0
pip install beautifulsoup4==4.12.2 html2text==2020.1.16
```

### 3. Configuration Setup

#### Create .env File
```bash
# Copy template
copy env.example .env

# Edit .env with your credentials
notepad .env  # Windows
nano .env     # macOS/Linux
```

#### .env File Contents
```env
# Email Configuration
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# Server Configuration
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=True
STREAMLIT_PORT=8501
```

### 4. Gmail Setup

#### Enable 2-Factor Authentication
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification
3. Generate App Password:
   - Go to Security → 2-Step Verification → App passwords
   - Select "Mail" and "Other (custom name)"
   - Enter "AI Assistant" as name
   - Copy the generated password (16 characters)

#### Gmail Settings
- Ensure IMAP is enabled in Gmail settings
- Allow less secure apps (if needed)
- Use the App Password in your .env file

### 5. OpenAI Setup

#### Get API Key
1. Go to [OpenAI Platform](https://platform.openai.com)
2. Sign up/Login to your account
3. Go to API Keys section
4. Create new secret key
5. Copy the key (starts with sk-)

#### API Usage
- Free tier: $5 credit
- Paid tier: Set up billing
- Monitor usage in OpenAI dashboard

### 6. Database Setup

#### Automatic Setup
The system automatically creates SQLite databases:
- `database/emails.db` - Email storage
- `database/knowledge.db` - Knowledge base

#### Manual Database Creation (if needed)
```bash
cd backend
python -c "from database import db; print('Database initialized')"
```

### 7. Knowledge Base Setup

#### Initialize Knowledge Base
```bash
cd backend
python -c "from rag_service import rag_service; print('Knowledge base initialized')"
```

#### Add Sample Documents
The system automatically creates default FAQ documents. You can add more:
- Place documents in `knowledge_base/` folders
- Use the Knowledge Base page in the dashboard
- Import documents via API

---

## 🚀 **Running the System**

### Method 1: Manual Start (Recommended for Development)

#### Terminal 1 - Backend
```bash
cd backend
python app.py
```
Expected output:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
Email processor started
```

#### Terminal 2 - Frontend
```bash
cd frontend
streamlit run streamlit_app.py
```
Expected output:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### Method 2: Using run.py (Alternative)
```bash
python run.py
```

### Method 3: Production Setup
```bash
# Install production dependencies
pip install gunicorn

# Start backend with Gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Start frontend
cd frontend
streamlit run streamlit_app.py --server.port 8501
```

---

## 🔧 **Configuration Options**

### Backend Configuration (backend/config.py)
```python
# Email settings
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# AI settings
OPENAI_MODEL = "gpt-4"
MAX_TOKENS = 150
TEMPERATURE = 0.7

# Filter settings
SUPPORT_KEYWORDS = ["support", "help", "query", "request"]
PRIORITY_KEYWORDS = ["urgent", "critical", "asap", "immediately"]
```

### Frontend Configuration
- Dashboard refresh interval: 30 seconds
- Auto-refresh: Configurable
- Theme: Custom CSS styling

---

## 📊 **System Architecture**

### File Structure
```
ai-communication-assistant/
├── backend/
│   ├── app.py              # Flask API server
│   ├── config.py           # Configuration
│   ├── database.py         # Database operations
│   ├── email_service.py    # Email handling
│   ├── ai_service.py       # AI processing
│   ├── rag_service.py      # RAG system
│   └── knowledge_base.py   # Knowledge management
├── frontend/
│   ├── streamlit_app.py    # Main dashboard
│   └── pages/              # Dashboard pages
├── knowledge_base/         # Knowledge documents
├── database/              # SQLite databases
├── requirements.txt       # Dependencies
└── .env                  # Environment variables
```

### API Endpoints
- `GET /api/emails` - Retrieve emails
- `POST /api/process-emails` - Process new emails
- `GET /api/analytics` - Get analytics data
- `GET /api/knowledge` - Knowledge base management
- `POST /api/responses/{id}/send` - Send responses

---

## 🛠️ **Troubleshooting**

### Common Issues

#### 1. Import Errors
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 2. Gmail Connection Issues
- Verify App Password is correct
- Check 2FA is enabled
- Ensure IMAP is enabled in Gmail
- Try different Gmail account

#### 3. OpenAI API Issues
- Verify API key is correct
- Check API usage limits
- Ensure billing is set up (if needed)
- Try with a different API key

#### 4. Database Issues
```bash
# Delete and recreate databases
rm database/emails.db database/knowledge.db
cd backend
python -c "from database import db; from rag_service import rag_service"
```

#### 5. Port Conflicts
```bash
# Check if ports are in use
netstat -an | findstr :5000  # Windows
lsof -i :5000               # macOS/Linux

# Change ports in config.py if needed
```

### Debug Mode
```bash
# Enable debug logging
export FLASK_DEBUG=True  # macOS/Linux
set FLASK_DEBUG=True     # Windows

# Check logs
tail -f logs/app.log     # If logging to file
```

### Performance Issues
- Reduce email processing frequency
- Limit number of emails processed
- Use smaller AI models
- Optimize database queries

---

## 📈 **Usage Guide**

### 1. First Time Setup
1. Start the system
2. Go to Settings page
3. Test email connection
4. Test AI service connection
5. Process some emails to populate database

### 2. Daily Usage
1. Open dashboard (http://localhost:8501)
2. Check Email Queue for new emails
3. Review AI-generated responses
4. Send approved responses
5. Monitor analytics

### 3. Knowledge Base Management
1. Go to Knowledge Base page
2. Add FAQ documents
3. Import policy documents
4. Search and update existing documents

### 4. Analytics and Monitoring
1. View Analytics page for insights
2. Monitor email volume trends
3. Check sentiment analysis
4. Track response times

---

## 🔒 **Security Considerations**

### Environment Variables
- Never commit .env file to version control
- Use strong, unique passwords
- Rotate API keys regularly

### Email Security
- Use App Passwords, not regular passwords
- Enable 2FA on Gmail account
- Monitor email access logs

### API Security
- Keep OpenAI API keys secure
- Monitor API usage and costs
- Use environment variables for all secrets

### Data Privacy
- Emails are stored locally in SQLite
- No data is sent to third parties (except OpenAI)
- Regular database backups recommended

---

## 📞 **Support and Maintenance**

### Regular Maintenance
- Update dependencies monthly
- Backup database files
- Monitor system logs
- Review and update knowledge base

### Backup Strategy
```bash
# Backup databases
cp database/emails.db backup/emails_$(date +%Y%m%d).db
cp database/knowledge.db backup/knowledge_$(date +%Y%m%d).db

# Backup knowledge base
tar -czf backup/knowledge_base_$(date +%Y%m%d).tar.gz knowledge_base/
```

### Updates
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Update system
git pull origin main  # If using Git
```

### Monitoring
- Check system health via dashboard
- Monitor API response times
- Track email processing success rates
- Review AI response quality

---

## 🎯 **Next Steps**

### Immediate Actions
1. ✅ Complete setup following this guide
2. ✅ Test email processing
3. ✅ Add knowledge base documents
4. ✅ Configure email filters
5. ✅ Train team on dashboard usage

### Future Enhancements
- Multi-language support
- Advanced analytics
- CRM integration
- Mobile app
- Voice integration
- Custom AI models

### Scaling Considerations
- Database optimization
- Caching implementation
- Load balancing
- Container deployment
- Cloud hosting

---

## 📚 **Additional Resources**

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Gmail IMAP Documentation](https://developers.google.com/gmail/imap)

### Community
- [GitHub Issues](https://github.com/your-repo/issues)
- [Discord Community](https://discord.gg/your-community)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/ai-communication-assistant)

### Training Materials
- Video tutorials (coming soon)
- Webinar series (monthly)
- Best practices guide
- Case studies and examples

---

**🎉 Congratulations! You now have a fully functional AI-Powered Communication Assistant!**

For additional support, please refer to the troubleshooting section or contact the development team.

