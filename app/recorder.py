# app/recorder.py
import subprocess
from datetime import datetime
import os
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STREAM_URL = "http://octopi.local/webcam/?action=stream"

FFMPEG_CMD = [
    "ffmpeg",
    "-y",
    "-reconnect", "1",
    "-reconnect_streamed", "1",
    "-reconnect_delay_max", "5",
    "-i", STREAM_URL,
    "-c", "copy",  # Copy stream without re-encoding (faster and more reliable)
]

def check_stream_available(timeout=5):
    """
    Check if the stream URL is accessible.
    Returns (True, None) if accessible, (False, error_message) if not.
    """
    try:
        logger.info(f"Checking stream availability at: {STREAM_URL}")
        response = requests.get(STREAM_URL, timeout=timeout, stream=True)

        if response.status_code == 200:
            logger.info("Stream is accessible")
            return True, None
        else:
            error_msg = f"Stream returned status code {response.status_code}"
            logger.warning(error_msg)
            return False, error_msg

    except requests.exceptions.Timeout:
        error_msg = "Stream connection timed out"
        logger.warning(error_msg)
        return False, error_msg
    except requests.exceptions.ConnectionError:
        error_msg = "Cannot connect to stream - check if OctoPi is running and accessible"
        logger.warning(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error checking stream: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def start_recording():
    date = datetime.now().strftime("%Y-%m-%d")
    video_dir = f"videos/{date}"
    
    try:
        os.makedirs(video_dir, exist_ok=True)
        logger.info(f"Created/verified directory: {video_dir}")
    except Exception as e:
        logger.error(f"Failed to create directory {video_dir}: {e}")
        raise

    filename = datetime.now().strftime("%H-%M-%S.mp4")
    output_path = f"{video_dir}/{filename}"
    
    cmd = FFMPEG_CMD + [output_path]
    logger.info(f"Starting recording to: {output_path}")
    logger.info(f"FFmpeg command: {' '.join(cmd)}")
    
    try:
        # On Windows, don't use CREATE_NEW_PROCESS_GROUP as it can cause issues
        # Instead, we'll handle termination differently
        # IMPORTANT: Use stdin=subprocess.PIPE for graceful shutdown with 'q' command
        # Use DEVNULL for stdout/stderr to prevent pipe blocking
        if os.name == "nt":
            # Use CREATE_NO_WINDOW to hide console window
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        logger.info(f"FFmpeg process started with PID: {process.pid}")
        return process
        
    except FileNotFoundError:
        logger.error("FFmpeg not found. Please install FFmpeg and add it to PATH")
        raise
    except Exception as e:
        logger.error(f"Failed to start recording: {e}")
        raise

