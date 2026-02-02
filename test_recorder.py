# test_recorder.py
import subprocess
from datetime import datetime
import os
import time

STREAM_URL = "http://octopi.local/webcam/?action=stream"

def test_recording():
    date = datetime.now().strftime("%Y-%m-%d")
    os.makedirs(f"videos/{date}", exist_ok=True)
    
    filename = datetime.now().strftime("%H-%M-%S.mp4")
    output_path = f"videos/{date}/{filename}"
    
    print(f"Output path: {output_path}")
    print(f"Stream URL: {STREAM_URL}")
    
    # Test with better error handling and logging
    cmd = [
        "ffmpeg",
        "-y",
        "-reconnect", "1",
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "5",
        "-i", STREAM_URL,
        "-c", "copy",
        "-t", "5",  # Record only 5 seconds for testing
        output_path
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Run with output capture to see errors
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print(f"\nReturn code: {result.returncode}")
        print(f"\nSTDOUT:\n{result.stdout}")
        print(f"\nSTDERR:\n{result.stderr}")
        
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"\nFile created successfully! Size: {size} bytes")
        else:
            print(f"\nFile was NOT created at {output_path}")
            
    except subprocess.TimeoutExpired:
        print("Command timed out")
    except FileNotFoundError:
        print("FFmpeg not found. Please install FFmpeg and add it to PATH")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_recording()
