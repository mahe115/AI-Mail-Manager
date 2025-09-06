from setuptools import setup, find_packages

setup(
    name='ai_communication_assistant',
    version='1.0.0',
    description='AI-Powered Email Communication Assistant for automated support email management',
    author='Your Name',
    packages=find_packages(include=['backend', 'backend.*', 'frontend', 'frontend.pages', 'frontend.components']),
    install_requires=[
        'Flask==3.0.0',
        'Flask-CORS==4.0.0',
        'Flask-Mail==0.9.1',
        'streamlit==1.28.1',
        'plotly==5.17.0',
        'pandas==2.1.3',
        'numpy==1.25.2',
        'openai==1.6.1',
        'tiktoken==0.5.2',
        'imaplib3==0.9.5',
        'email-mime-base==1.1.1',
        'python-dotenv==1.0.0',
        'pydantic==2.5.0',
        'requests==2.31.0',
        'beautifulsoup4==4.12.2',
        'html2text==2020.1.16',
        'python-dateutil==2.8.2',
        'pytest==7.4.3',
        'black==23.11.0',
        'flake8==6.1.0'
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'run-ai-assistant=run:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
    ],
)
