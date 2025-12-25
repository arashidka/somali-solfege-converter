"""
Example usage of the Somali Solfege Converter - Audio Processor

This script demonstrates how to use the audio processing module.
"""

from audio_processor import prepare_audio_input, check_dependencies, get_audio_info
import numpy as np


def example_basic_usage():
    """
    Example 1: Basic usage with a simple audio file
    """
    print("=" * 60)
    print("Example 1: Basic Audio Processing")
    print("=" * 60)
    
    # This is a placeholder example - you would replace with your actual file
    # samples, sr = prepare_audio_input("your_audio.wav")
    # print(f"Loaded {len(samples)/sr:.2f}s of audio")
    # print(f"Sample rate: {sr}Hz")
    # print(f"Sample values range: [{samples.min():.3f}, {samples.max():.3f}]")
    
    print("To use this example:")
    print("1. Replace 'your_audio.wav' with your actual file path")
    print("2. Uncomment the code above")
    print("3. Run this script")
    print()


def example_video_extraction():
    """
    Example 2: Extracting audio from video
    """
    print("=" * 60)
    print("Example 2: Video to Audio Extraction")
    print("=" * 60)
    
    # Extract audio from testVideo.mp4
    try:
        samples, sr = prepare_audio_input("testVideo.mp4", target_sr=22050)
        print(f"✅ Successfully extracted {len(samples)/sr:.2f}s of audio from testVideo.mp4")
        print(f"   Sample rate: {sr}Hz")
        print(f"   Number of samples: {len(samples):,}")
        print(f"   Audio range: [{samples.min():.3f}, {samples.max():.3f}]")
    except Exception as e:
        print(f"❌ Error processing testVideo.mp4: {e}")
        print("   Make sure the file exists in the project folder")
    
    print()


def example_file_info():
    """
    Example 3: Getting file information without loading
    """
    print("=" * 60)
    print("Example 3: Get File Information")
    print("=" * 60)
    
    # Get info about testVideo.mp4
    try:
        info = get_audio_info("testVideo.mp4")
        print(f"✅ File: {info['path']}")
        print(f"   Format: {info['extension']}")
        print(f"   Size: {info['size_mb']:.2f} MB")
        print(f"   Duration: {info['duration']:.2f}s")
        print(f"   Sample rate: {info['sample_rate']}Hz")
        print(f"   Channels: {info['channels']}")
    except Exception as e:
        print(f"❌ Error getting file info: {e}")
        print("   Make sure testVideo.mp4 exists in the project folder")
    
    print()


def example_with_analysis():
    """
    Example 4: Load audio and perform basic analysis
    """
    print("=" * 60)
    print("Example 4: Audio Analysis")
    print("=" * 60)
    
    # This is a placeholder example
    # samples, sr = prepare_audio_input("your_audio.wav")
    # 
    # # Basic statistics
    # duration = len(samples) / sr
    # rms_energy = np.sqrt(np.mean(samples**2))
    # peak_amplitude = np.max(np.abs(samples))
    # 
    # print(f"Duration: {duration:.2f}s")
    # print(f"RMS Energy: {rms_energy:.4f}")
    # print(f"Peak Amplitude: {peak_amplitude:.4f}")
    # print(f"Dynamic Range: {20 * np.log10(peak_amplitude/rms_energy):.2f} dB")
    
    print("To use this example:")
    print("1. Replace 'your_audio.wav' with your actual file path")
    print("2. Uncomment the code above")
    print("3. Run this script")
    print()


def main():
    """
    Main function demonstrating all examples
    """
    print("\n" + "=" * 60)
    print("SOMALI SOLFEGE CONVERTER - USAGE EXAMPLES")
    print("=" * 60)
    print()
    
    # Check dependencies first
    print("Checking dependencies...")
    if check_dependencies():
        print("✅ All dependencies are installed!\n")
    else:
        print("⚠️ Some dependencies are missing. Install them with:")
        print("   pip install -r requirements.txt\n")
        return
    
    # Show examples
    example_basic_usage()
    example_video_extraction()
    example_file_info()
    example_with_analysis()
    
    print("=" * 60)
    print("For more details, see:")
    print("  - audio_processor.py (module documentation)")
    print("  - audio_processing.ipynb (interactive notebook)")
    print("  - test_audio_processor.py (test suite)")
    print("=" * 60)


if __name__ == "__main__":
    main()
