"""
Test script for audio_processor module

This script tests the basic functionality of the audio processor
without requiring actual audio/video files.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_processor import check_dependencies, get_audio_info
import numpy as np


def test_dependency_checker():
    """Test the dependency checker function"""
    print("=" * 60)
    print("Test 1: Dependency Checker")
    print("=" * 60)
    result = check_dependencies()
    print(f"\nDependency check result: {result}")
    print()


def test_audio_processor_imports():
    """Test that all imports work correctly"""
    print("=" * 60)
    print("Test 2: Module Imports")
    print("=" * 60)
    try:
        from audio_processor import prepare_audio_input
        print("✅ prepare_audio_input function imported successfully")
        
        # Check function signature
        import inspect
        sig = inspect.signature(prepare_audio_input)
        print(f"   Function signature: {sig}")
        print()
        return True
    except Exception as e:
        print(f"❌ Failed to import: {e}")
        print()
        return False


def test_with_synthetic_audio():
    """Test with a synthetic audio file"""
    print("=" * 60)
    print("Test 3: Synthetic Audio Processing")
    print("=" * 60)
    
    try:
        from scipy.io import wavfile
        from audio_processor import prepare_audio_input
        
        # Create a simple synthetic audio file (1 second, 440Hz sine wave)
        sample_rate = 44100
        duration = 1.0
        frequency = 440.0  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = np.sin(2 * np.pi * frequency * t)
        
        # Convert to int16
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # Save to temporary file
        test_file = "test_audio.wav"
        wavfile.write(test_file, sample_rate, audio_data)
        print(f"✅ Created synthetic audio file: {test_file}")
        
        # Process the audio
        samples, sr = prepare_audio_input(test_file, target_sr=22050)
        
        print(f"✅ Audio processed successfully!")
        print(f"   Original sample rate: {sample_rate}Hz")
        print(f"   Processed sample rate: {sr}Hz")
        print(f"   Audio duration: {len(samples)/sr:.2f}s")
        print(f"   Sample shape: {samples.shape}")
        print(f"   Sample dtype: {samples.dtype}")
        print(f"   Value range: [{samples.min():.3f}, {samples.max():.3f}]")
        
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"✅ Cleaned up test file")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Cleanup on failure
        if os.path.exists("test_audio.wav"):
            os.remove("test_audio.wav")
        
        print()
        return False


def test_error_handling():
    """Test error handling for invalid inputs"""
    print("=" * 60)
    print("Test 4: Error Handling")
    print("=" * 60)
    
    try:
        from audio_processor import prepare_audio_input
        
        # Test with non-existent file
        try:
            prepare_audio_input("nonexistent_file.mp4")
            print("❌ Should have raised FileNotFoundError")
            return False
        except FileNotFoundError:
            print("✅ Correctly raised FileNotFoundError for missing file")
        
        # Test with unsupported format
        try:
            # Create a dummy file with unsupported extension
            with open("test.xyz", "w") as f:
                f.write("dummy")
            
            prepare_audio_input("test.xyz")
            print("❌ Should have raised ValueError for unsupported format")
            os.remove("test.xyz")
            return False
        except ValueError as e:
            print(f"✅ Correctly raised ValueError for unsupported format: {str(e)[:50]}...")
            if os.path.exists("test.xyz"):
                os.remove("test.xyz")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Test failed unexpectedly: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SOMALI SOLFEGE CONVERTER - AUDIO PROCESSOR TEST SUITE")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    test_dependency_checker()
    results.append(("Module Imports", test_audio_processor_imports()))
    results.append(("Synthetic Audio", test_with_synthetic_audio()))
    results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print()
    print(f"Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️ {total_count - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
