# 🤖 AI-Mail-Manager (AI-Powered  Mail Communication Assistant)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.1-red.svg)](https://streamlit.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-purple.svg)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📦 Deliverables

1. End-to-end working solution of **AI-Mail-Manager (AI-Powered  Mail Communication Assistant ☝️)** 
2. Demonstration video of all the working features of the System 👉 [Watch Here](https://youtu.be/o54Eo8ImktY?feature=shared)  
3. Short self-written documentation  on architecture + approach used 👉 [Read Here](/AI%20Mail%20Manager%20Architecture%20with%20approach.pdf)

> **Transform your customer support with AI-powered email management, sentiment analysis, and intelligent response generation.**

## 🌟 **Features**
## 📸 Dashboard Preview

Experience the **AI Communication Assistant Dashboard** with a quick preview:

<p align="center">
  <img src="Dashboard images/dashboard_slides.gif" alt="AI Communication Assistant – dashboard slideshow" width="900">
</p>

<details>
  <summary><strong>View individual screenshots</strong></summary>

| Main Dashboard | AI Responses | Analytics | Emails | Sidebar Overview |
|---|---|---|---|---|
| <img src="Dashboard images/main_page_screenshot.png" width="400" /> | <img src="Dashboard images/ai_response_management_tab.png" width="400" /> | <img src="Dashboard images/analytics%20of%20email%20insights.png" width="400" /> | <img src="Dashboard images/email_management_tab.png" width="400" /> | <img src="Dashboard images/main_page_screenshot.png" width="400" /> |

</details>

## 🎥 Dashboard Demo

<p align="center">
  <a href="https://youtu.be/o54Eo8ImktY?feature=shared" target="_blank">
    <img src="https://img.youtube.com/vi/o54Eo8ImktY/0.jpg" alt="Dashboard Demo" width="800">
  </a>
</p>

> 🔗 Click the image above to watch the demo on YouTube.


### 📧 **Intelligent Email Management**
- **Automatic Email Retrieval**: Fetch emails from Gmail using IMAP
- **Smart Filtering**: Filter support emails based on keywords
- **Priority Classification**: AI-powered urgency detection
- **Sentiment Analysis**: Understand customer emotions and tone
- **Thread Management**: Group related conversations

### 🤖 **AI-Powered Response Generation**
- **RAG-Enhanced Responses**: Use knowledge base for contextual answers
- **Sentiment-Aware**: Empathetic responses based on customer mood
- **Professional Tone**: Consistent, high-quality communication
- **Confidence Scoring**: AI confidence levels for response quality
- **Human Review**: Edit and approve responses before sending

### 📊 **Analytics & Insights**
- **Real-time Dashboard**: Live metrics and performance tracking
- **Sentiment Trends**: Monitor customer satisfaction over time
- **Response Analytics**: Track resolution times and success rates
- **Volume Analysis**: Email volume patterns and peak times
- **Performance Insights**: AI-powered recommendations

### 📚 **Knowledge Base Management**
- **Document Storage**: FAQ, policies, and procedure management
- **Vector Search**: Semantic search across knowledge base
- **Auto-Import**: Bulk import from directories
- **Category Organization**: Organize by support topics



## 🚀 **Quick Start**

### Prerequisites
- Python 3.9+
- Gmail account with App Password
- OpenAI API key

### Installation
```bash
# Clone the repository
git clone https://github.com/your-username/ai-communication-assistant.git
cd ai-communication-assistant

# Create virtual environment
python -m venv mailassistant_env
source mailassistant_env/bin/activate  # On Windows: mailassistant_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your credentials

# Start the system
cd backend && python app.py &  # Backend
cd frontend && streamlit run streamlit_app.py  # Frontend
```

### Access Dashboard
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:5000

## 📋 **System Requirements**

### Minimum Requirements
- **OS**: Windows 10, macOS 10.14, or Linux Ubuntu 18.04+
- **Python**: 3.9 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connection for AI services

### Recommended Setup
- **RAM**: 16GB for optimal performance
- **Storage**: SSD with 10GB free space
- **CPU**: Multi-core processor (4+ cores)
- **Network**: Stable broadband connection

## 🏗️ **Architecture**

### Tech Stack
- **Backend**: Flask 3.0.0, SQLite, OpenAI GPT-4
- **Frontend**: Streamlit 1.28.1, Plotly, Custom CSS
- **AI/ML**: OpenAI API, Sentence Transformers, Scikit-learn
- **Database**: SQLite with vector embeddings
- **Email**: IMAP/SMTP with Gmail integration

### System Flow
```
Email Retrieval → AI Processing → Database Storage → Dashboard Display
                                    ↓
Response Generation (RAG) → Human Review → Email Sending
```

## 📁 **Project Structure**

```
ai-communication-assistant/
├── backend/                 # Flask API server
│   ├── app.py              # Main application
│   ├── config.py           # Configuration
│   ├── database.py         # Database operations
│   ├── email_service.py    # Email handling
│   ├── ai_service.py       # AI processing
│   ├── rag_service.py      # RAG system
│   └── knowledge_base.py   # Knowledge management
├── frontend/               # Streamlit dashboard
│   ├── streamlit_app.py    # Main dashboard
│   └── pages/              # Dashboard pages
├── knowledge_base/         # Knowledge documents
├── database/              # SQLite databases
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## 🔧 **Configuration**

### Environment Variables
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

### Gmail Setup
1. Enable 2-Factor Authentication
2. Generate App Password
3. Enable IMAP access
4. Use App Password in configuration

### OpenAI Setup
1. Create OpenAI account
2. Generate API key
3. Set up billing (if needed)
4. Add API key to configuration

## 📊 **Usage Examples**

### Basic Email Processing
```python
# Process emails automatically
POST /api/process-emails

# Get filtered emails
GET /api/emails?priority=urgent&status=unread

# Generate AI response
POST /api/generate-response
```

### Knowledge Base Management
```python
# Add document
POST /api/knowledge
{
    "title": "Account Access Issues",
    "content": "Common solutions for login problems...",
    "category": "FAQ",
    "tags": ["account", "login", "password"]
}

# Search knowledge base
GET /api/knowledge/search?q=password reset
```

### Analytics and Reporting
```python
# Get analytics data
GET /api/analytics?days=7

# Search emails
GET /api/search?q=customer complaint
```

## 🎯 **Use Cases**

### Customer Support Teams
- **High Volume**: Handle hundreds of emails daily
- **Consistent Quality**: Maintain professional communication standards
- **Faster Response**: Reduce response time by 70%
- **Better Insights**: Understand customer sentiment trends

### Small Businesses
- **Cost Effective**: Reduce support staff requirements
- **24/7 Availability**: Process emails outside business hours
- **Scalable**: Grow with your business needs
- **Professional Image**: Maintain high-quality customer communication

### Enterprise Organizations
- **Integration Ready**: Connect with existing CRM systems
- **Customizable**: Adapt to specific business requirements
- **Compliance**: Maintain audit trails and documentation
- **Multi-department**: Support various business units

## 🔒 **Security & Privacy**



## 📈 **Performance Metrics**

### Typical Performance
- **Email Processing**: 5-10 emails per minute
- **Response Generation**: 2-5 seconds per response
- **Sentiment Analysis**: 1-4 seconds per email
- **Knowledge Search**: <2 second for queries



## 🛠️ **Development**

### Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Code formatting
black backend/ frontend/
flake8 backend/ frontend/

# Type checking
mypy backend/
```

### Testing
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# End-to-end tests
pytest tests/e2e/
```

## 📚 **Documentation**

### User Guides
- [Setup Guide](SETUP_GUIDE.md) - Complete installation instructions


## 🙏 **Acknowledgments**

- **OpenAI** for providing the GPT-4 API
- **Streamlit** for the amazing dashboard framework
- **Flask** for the robust backend framework
- **Sentence Transformers** for semantic search capabilities
- **Community Contributors** for feedback and improvements

---

## 📞 **Contact**

- **Email**: mahe.mahendran806@gmail.com
- **LinkedIn**: [Mahendran B](https://www.linkedin.com/in/mahendran-b-95333521a/)

---

**⭐ Star this repository if you find it helpful!**

**🤝 Contribute to make it even better!**

**📢 Share with your network!**

