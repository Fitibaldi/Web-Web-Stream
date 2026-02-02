# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.recorder import start_recording
import subprocess
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

process = None

@app.post("/record/start")
def record_start():
    global process
    if process is None or (process.poll() is not None):
        process = start_recording()
        logging.info(f"Started recording (pid={process.pid})")
        return {"status": "recording", "pid": process.pid}
    logging.info("Start requested but already recording")
    return {"status": "already_recording", "pid": process.pid}

@app.post("/record/stop")
def record_stop():
    global process
    if not process:
        logging.info("Stop requested but no active recording")
        return {"status": "not_recording"}
    if process.poll() is not None:
        pid = process.pid
        process = None
        logging.info(f"Recording process pid={pid} already exited")
        return {"status": "stopped", "pid": pid}
    try:
        logging.info(f"Terminating recording pid={process.pid}")
        import os
        
        # On Windows, use taskkill for more reliable termination
        if os.name == "nt":
            try:
                # First try graceful termination with 'q' command to FFmpeg stdin
                process.communicate(input=b'q', timeout=2)
                logging.info("Sent 'q' command to FFmpeg")
            except:
                # If that fails, use taskkill
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], 
                             capture_output=True)
                logging.info("Used taskkill to terminate process")
        else:
            process.terminate()
            
        try:
            process.wait(timeout=5)
            logging.info("Process terminated gracefully")
        except subprocess.TimeoutExpired:
            logging.warning("Terminate timed out; killing process")
            process.kill()
            process.wait(timeout=5)
        pid = process.pid
        process = None
        return {"status": "stopped", "pid": pid}
    except Exception as e:
        logging.exception("Error stopping recording")
        return {"status": "error", "error": str(e)}

@app.get("/record/status")
def record_status():
    if process and process.poll() is None:
        return {"status": "recording", "pid": process.pid}
    return {"status": "stopped"}

app.mount("/", StaticFiles(directory="static", html=True), name="static")
