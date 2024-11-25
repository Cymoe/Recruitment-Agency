import os
import subprocess

# Get port from environment variable with fallback
port = os.environ.get('PORT', '8501')

# Ensure port is an integer
try:
    port = int(port)
except ValueError:
    port = 8501

# Start Streamlit
subprocess.run([
    'streamlit', 'run', 'app.py',
    '--server.port', str(port),
    '--server.address', '0.0.0.0'
])
