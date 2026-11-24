"""
Simple script to record test video using your webcam.
Works on Windows, Mac, and Linux (if opencv-python is installed).
"""

import cv2
import sys
from pathlib import Path

def record_video(filename="my_answer.mp4", duration=20):
    """
    Record video from your webcam.
    
    Args:
        filename: Output video file (MP4 format)
        duration: Recording duration in seconds
    
    Instructions:
        - Look at the camera
        - Speak clearly
        - Try to show emotions (smile, frown, etc.)
        - Answer a practice question (will be displayed on screen)
    """
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Could not access webcam")
        print("\nTroubleshooting:")
        print("  - Check if webcam is connected")
        print("  - Close other apps using the camera (Zoom, Skype, etc.)")
        print("  - Try a different camera index: python test_video_record.py 1")
        sys.exit(1)
    
    # Get video properties
    fps = 30  # Frames per second
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Define codec and create VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    print(f"🎥 Recording {duration} seconds of video...")
    print(f"Resolution: {width}x{height} @ {fps} FPS")
    print("\n" + "="*60)
    print("PRACTICE QUESTION:")
    print("Tell me about a challenging project you worked on.")
    print("Focus on: What was the challenge? What did you do? What was the result?")
    print("="*60)
    print("\nRecording will start in 3 seconds...")
    print("Look at the camera and speak clearly!\n")
    
    # Countdown
    for i in range(3, 0, -1):
        print(f"{i}...")
        cv2.waitKey(1000)
    
    print("🔴 RECORDING NOW!\n")
    
    frame_count = 0
    max_frames = fps * duration
    
    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Failed to capture frame")
            break
        
        # Add recording indicator (red dot)
        cv2.circle(frame, (30, 30), 15, (0, 0, 255), -1)
        
        # Add timer text
        elapsed = frame_count / fps
        remaining = duration - elapsed
        cv2.putText(
            frame, 
            f"Time remaining: {int(remaining)}s",
            (10, height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        # Write frame
        out.write(frame)
        
        # Display frame
        cv2.imshow('Recording - Press Q to stop early', frame)
        
        # Progress indicator
        if frame_count % fps == 0:
            print(f"  {int(elapsed)}s / {duration}s", end="\r")
        
        frame_count += 1
        
        # Allow early exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n⏸️ Recording stopped early by user")
            break
    
    # Release everything
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
    print(f"\n✅ Recording complete!")
    print(f"💾 Saved to: {filename}")
    print(f"📊 File size: {Path(filename).stat().st_size / 1_000_000:.1f} MB")
    print("\nTest with:")
    print(f"  curl -X POST http://localhost:8001/submit_answer \\")
    print(f"    -F 'video=@{filename}' \\")
    print(f"    -F 'question_id=1'")

if __name__ == "__main__":
    import sys
    
    # Parse arguments
    duration = 20  # Default: 20 seconds
    camera_index = 0  # Default: first camera
    
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            print("Usage: python test_video_record.py [duration_seconds] [camera_index]")
            print("Example: python test_video_record.py 30 0")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        try:
            camera_index = int(sys.argv[2])
        except ValueError:
            print("Invalid camera index. Using default (0)")
    
    # Update VideoCapture if custom camera index provided
    record_video(duration=duration)