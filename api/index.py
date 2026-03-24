import os
from streamlit.web import cli as stcli
import sys

# Configure Streamlit behavior for Vercel's serverless environment
os.environ["STREAMLIT_SERVER_PORT"] = "8501"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

def handler(request, response):
    # This acts as the entry point for Vercel Serverless Functions
    sys.argv = ["streamlit", "run", "app_premium.py"]
    sys.exit(stcli.main())
