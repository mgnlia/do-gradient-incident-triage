"""
Vercel serverless entry point for DO Gradient Incident Triage API.
Wraps FastAPI app with Mangum for AWS Lambda / Vercel compatibility.
"""
import sys
import os

# Add parent directory to path so we can import from backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app
from mangum import Mangum

# Vercel uses this handler
handler = Mangum(app, lifespan="off")
