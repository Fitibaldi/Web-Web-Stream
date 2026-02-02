# Troubleshooting Guide

## File Not Being Created - Common Issues

### 1. FFmpeg Not Installed
**Symptom**: No video files created, process fails immediately

**Solution**: 
- Install FFmpeg from https://ffmpeg.org/download.html
- On Windows: Download, extract, and add to PATH
- Test with: `ffmpeg -version`

### 2. Stream URL Not Accessible
**Symptom**: No files created, FFmpeg hangs or fails

**Check**:
```bash
# Test if stream is accessible
curl -I http://octopi.local/webcam/?action=stream
```

**Solutions**:
- Verify OctoPi is running and accessible
- Check network connectivity
- Try accessing the stream URL in a browser
- Update `STREAM_URL` in `app/recorder.py` if needed

### 3. Directory Permissions
**Symptom**: Error creating directory or writing files

**Solution**:
- Ensure the `videos/` directory is writable
- Check Windows file permissions
- Try running as administrator (not recommended for production)

### 4. Codec Compatibility Issues / Video Cannot Be Played
**Symptom**: FFmpeg starts but file is 0 bytes, corrupted, or shows "Unknown GUID" error when playing

**Cause**: MJPEG streams from webcams need to be re-encoded to H.264 for proper MP4 playback

**Solution**: Already fixed in updated `recorder.py` - now uses:
  ```python
  "-f", "mjpeg",  # Specify input format
  "-c:v", "libx264",  # Re-encode to H.264
  "-preset", "ultrafast",  # Fast encoding
  "-pix_fmt", "yuv420p",  # Ensure compatibility
  ```

### 5. Process Termination Issues (Windows)
**Symptom**: Recording starts but stops immediately

**Cause**: `CREATE_NEW_PROCESS_GROUP` flag can cause issues with FFmpeg

**Solution**: Already fixed in updated `recorder.py` - now uses `CREATE_NO_WINDOW`

## Testing Steps

### 1. Run the Test Script
```bash
python test_recorder.py
```

This will:
- Test FFmpeg installation
- Attempt a 5-second recording
- Show detailed error messages
- Verify file creation

### 2. Check Logs
When running the FastAPI app:
```bash
uvicorn app.app:app --reload
```

Look for log messages indicating:
- Directory creation
- FFmpeg command being executed
- Process PID
- Any errors

### 3. Manual FFmpeg Test
Test FFmpeg directly:
```bash
ffmpeg -i http://octopi.local/webcam/?action=stream -t 5 -c copy test.mp4
```

### 4. Check File System
After starting recording, check:
```bash
dir videos /s  # Windows
ls -R videos   # Linux/Mac
```

## Common Error Messages

### "FFmpeg not found"
- FFmpeg is not installed or not in PATH
- Install FFmpeg and restart terminal

### "Connection refused" or "Connection timed out"
- Stream URL is not accessible
- Check OctoPi is running
- Verify network connectivity

### "Permission denied"
- Directory is not writable
- Check file/folder permissions

### "Invalid data found when processing input"
- Stream format is incompatible
- Try re-encoding instead of copying codec

## Debugging Checklist

- [ ] FFmpeg installed and in PATH (`ffmpeg -version`)
- [ ] Stream URL accessible in browser
- [ ] `videos/` directory exists and is writable
- [ ] FastAPI server running without errors
- [ ] Check server logs for error messages
- [ ] Run `test_recorder.py` to see detailed output
- [ ] Try manual FFmpeg command
- [ ] Check if antivirus is blocking file creation
- [ ] Verify disk space available

## Updated Features

The code has been updated with:

1. **Better Error Handling**: Exceptions are caught and logged
2. **Detailed Logging**: See exactly what's happening
3. **Improved Codec Settings**: More explicit codec specification
4. **Windows Compatibility**: Fixed process creation flags
5. **Better Termination**: Improved stop mechanism for Windows

## Next Steps

1. Run `test_recorder.py` to diagnose the issue
2. Check the output for specific error messages
3. Follow the relevant solution above
4. If still not working, check the FFmpeg stderr output in logs
