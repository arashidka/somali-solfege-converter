"""
Audio Processor Module for Somali Solfege Converter

This module provides functionality to extract audio from video files
and prepare audio data for pitch detection and musical analysis.
Optimized for memory efficiency with 8GB RAM systems.
"""

import os
import sys
import subprocess
import numpy as np
import gc
from scipy.io import wavfile


def check_dependencies():
    """
    Check and install required dependencies if missing.
    
    Returns:
        bool: True if all dependencies are available, False otherwise
    """
    libraries = ['moviepy', 'numpy', 'scipy', 'matplotlib', 'librosa']
    
    print("Checking environment dependencies...")
    all_available = True
    
    for lib in libraries:
        try:
            __import__(lib)
            print(f"✅ {lib} is installed.")
        except ImportError:
            print(f"❌ {lib} missing. Installing now...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
                print(f"✅ {lib} installed successfully.")
            except subprocess.CalledProcessError:
                print(f"⚠️ Failed to install {lib}. Please install manually.")
                all_available = False
    
    return all_available


def prepare_audio_input(file_path, target_sr=22050):
    """
    Extract audio from video if needed and load it into memory.
    Optimized for 8GB RAM using float32 and downsampling.
    
    Args:
        file_path (str): Path to input video or audio file
        target_sr (int): Target sample rate in Hz (default: 22050)
    
    Returns:
        tuple: (samples, sample_rate) where samples is a numpy array of audio data
               normalized to float32 in range [-1.0, 1.0]
    
    Raises:
        FileNotFoundError: If the input file doesn't exist
        ValueError: If the file format is not supported
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")
    
    # Import moviepy only when needed (lazy import)
    try:
        # Try moviepy 2.x style import
        from moviepy import VideoFileClip
    except ImportError:
        # Fall back to moviepy 1.x style import
        from moviepy.editor import VideoFileClip
    
    ext = os.path.splitext(file_path)[1].lower()
    temp_audio = "temp_extracted_audio.wav"
    
    # Step 1: Video to Audio Extraction (If needed)
    if ext in ['.mp4', '.mov', '.avi', '.mkv']:
        print(f"Video detected. Extracting audio from {file_path}...")
        try:
            video = VideoFileClip(file_path)
            if video.audio is None:
                raise ValueError(f"Video file has no audio track: {file_path}")
            video.audio.write_audiofile(temp_audio, fps=target_sr, verbose=False, logger=None)
            video.close()  # Close file handle immediately
            load_path = temp_audio
            del video
        except Exception as e:
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
            raise ValueError(f"Failed to extract audio from video: {e}")
    elif ext in ['.wav', '.mp3', '.flac', '.ogg']:
        load_path = file_path
    else:
        raise ValueError(f"Unsupported file format: {ext}. "
                        f"Supported formats: .mp4, .mov, .avi, .mkv, .wav, .mp3, .flac, .ogg")

    # Step 2: Load and Downsample
    print(f"Loading and normalizing audio...")
    try:
        sr, data = wavfile.read(load_path)
    except Exception as e:
        if os.path.exists(temp_audio) and ext in ['.mp4', '.mov', '.avi', '.mkv']:
            os.remove(temp_audio)
        raise ValueError(f"Failed to load audio file: {e}")
    
    # Convert to Mono if Stereo
    if len(data.shape) > 1:
        print(f"Converting stereo to mono...")
        data = data.mean(axis=1)
    
    # Downsample logic (Simple decimation for speed)
    if sr != target_sr:
        print(f"Resampling from {sr}Hz to {target_sr}Hz...")
        resample_factor = max(1, sr // target_sr)
        data = data[::resample_factor]
        sr = sr // resample_factor
    
    # Memory-safe conversion to float32
    if data.dtype in [np.int16, np.int32]:
        # Integer audio data - normalize by type max
        info = np.iinfo(data.dtype)
        samples = data.astype(np.float32) / max(abs(info.min), abs(info.max))
    else:
        # Already float - just convert and normalize
        samples = data.astype(np.float32)
        max_val = np.max(np.abs(samples))
        if max_val > 0:
            samples /= max_val
    
    # Cleanup
    if os.path.exists(temp_audio) and ext in ['.mp4', '.mov', '.avi', '.mkv']:
        os.remove(temp_audio)
    
    del data
    gc.collect()
    
    duration = len(samples) / sr
    print(f"✅ Done. Loaded {duration:.2f}s of audio at {sr}Hz.")
    print(f"   Audio shape: {samples.shape}, dtype: {samples.dtype}")
    print(f"   Value range: [{samples.min():.3f}, {samples.max():.3f}]")
    
    return samples, sr


def get_audio_info(file_path):
    """
    Get basic information about an audio/video file without loading it fully.
    
    Args:
        file_path (str): Path to input file
    
    Returns:
        dict: Dictionary with file information (format, duration, etc.)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        from moviepy import VideoFileClip
    except ImportError:
        from moviepy.editor import VideoFileClip
    
    ext = os.path.splitext(file_path)[1].lower()
    info = {
        'path': file_path,
        'extension': ext,
        'size_mb': os.path.getsize(file_path) / (1024 * 1024)
    }
    
    if ext in ['.mp4', '.mov', '.avi', '.mkv']:
        try:
            video = VideoFileClip(file_path)
            info['duration'] = video.duration
            info['has_audio'] = video.audio is not None
            if video.audio:
                info['fps'] = video.audio.fps
            video.close()
        except Exception as e:
            info['error'] = str(e)
    else:
        try:
            sr, data = wavfile.read(file_path)
            info['sample_rate'] = sr
            info['duration'] = len(data) / sr
            info['channels'] = 1 if len(data.shape) == 1 else data.shape[1]
        except Exception as e:
            info['error'] = str(e)
    
    return info


if __name__ == "__main__":
    # Example usage
    print("Audio Processor Module for Somali Solfege Converter")
    print("=" * 60)
    
    # Check dependencies
    if check_dependencies():
        print("\n✅ All dependencies are available!")
    else:
        print("\n⚠️ Some dependencies are missing. Please install them manually.")
