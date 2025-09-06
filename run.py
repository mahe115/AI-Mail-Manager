import subprocess
import os
import signal

def main():
    # Set environment variables
    os.environ['FLASK_APP'] = 'backend/app.py'
    os.environ['FLASK_ENV'] = 'development'

    try:
        # Launch Flask backend server
        flask_process = subprocess.Popen(
            ['python', 'backend/app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Flask backend started (PID:", flask_process.pid, ")")

        # Launch Streamlit frontend dashboard
        streamlit_process = subprocess.Popen(
            ['streamlit', 'run', 'frontend/app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Streamlit frontend started (PID:", streamlit_process.pid, ")")

        print("\n🚀 Backend and frontend are running... Press Ctrl+C to stop.")

        # Keep the main process alive while both subprocesses run
        flask_process.wait()
        streamlit_process.wait()

    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        flask_process.terminate()
        streamlit_process.terminate()

if __name__ == '__main__':
    main()
