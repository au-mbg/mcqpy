#!/usr/bin/env python3
"""
Entry point script for MCQPy web interface
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Launch the MCQPy Streamlit web interface"""
    
    # Get the path to the app.py file
    app_path = Path(__file__).parent / "app.py"
    
    # Run streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error launching MCQPy web interface: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down MCQPy web interface...")
        sys.exit(0)


if __name__ == "__main__":
    main()