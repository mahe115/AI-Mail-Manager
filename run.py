import subprocess
import os

def main():
    # Set environment variables if needed
    os.environ['FLASK_APP'] = 'backend/app.py'
    os.environ['FLASK_ENV'] = 'development'  # or 'production' as needed

    # Launch Flask backend server
    flask_process = subprocess.Popen(
        ['python', 'backend/app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    flask_process.wait()
    
    # Launch Streamlit frontend dashboard
    streamlit_process = subprocess.Popen(
        ['streamlit', 'run', 'frontend/streamlit_app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    streamlit_process.wait()

    print("Backend and frontend are launching...")

    # Wait for both processes to complete
    try:
        flask_process.wait()
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
        flask_process.terminate()
        streamlit_process.terminate()

if __name__ == '__main__':
    main()
