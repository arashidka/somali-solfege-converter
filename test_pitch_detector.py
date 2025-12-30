"""
Test script for pitch detection module

Tests the YIN algorithm and note segmentation functionality.
"""

import sys
import os
import pytest
import numpy as np
from scipy.io import wavfile

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pitch_detector import (
    yin_pitch_detection,
    smooth_pitch_track,
    segment_notes,
    hz_to_midi,
    midi_to_note_name
)


def test_pitch_detection_with_sine_wave():
    """Test pitch detection with a synthetic sine wave"""
    print("=" * 60)
    print("Test 1: Pitch Detection with Sine Wave")
    print("=" * 60)
    
    # Create a 440Hz sine wave (A4 note)
    sr = 22050
    duration = 1.0
    frequency = 440.0

    t = np.linspace(0, duration, int(sr * duration))
    samples = np.sin(2 * np.pi * frequency * t).astype(np.float32)

    # Detect pitch
    times, pitches = yin_pitch_detection(samples, sr,
                                         frame_length=2048,
                                         hop_length=512,
                                         threshold=0.1)

    # Check detected pitches
    voiced_pitches = pitches[pitches > 0]
    assert len(voiced_pitches) > 0, "No voiced pitches detected"

    mean_pitch = np.mean(voiced_pitches)
    pitch_std = np.std(voiced_pitches)
    assert abs(mean_pitch - frequency) < 25, f"Pitch error too large: {abs(mean_pitch-frequency):.1f} Hz"


def test_pitch_smoothing():
    """Test pitch smoothing functionality"""
    print("=" * 60)
    print("Test 2: Pitch Smoothing")
    print("=" * 60)
    
    # Create pitch track with outliers
    pitches = np.array([200, 205, 199, 500, 201, 203, 0, 0, 210, 205])

    smoothed = smooth_pitch_track(pitches, kernel_size=3)

    # Check that outlier (500) was reduced
    assert smoothed[3] < pitches[3], f"Outlier not reduced: {smoothed[3]} >= {pitches[3]}"


def test_note_segmentation():
    """Test note segmentation functionality"""
    print("=" * 60)
    print("Test 3: Note Segmentation")
    print("=" * 60)
    
    # Create a pitch track with 3 distinct notes
    sr = 22050
    hop_length = 512

    # Times: 0, 0.023, 0.046, ... (512 samples apart)
    times = np.arange(100) * hop_length / sr

    # Create 3 notes: 200Hz, silence, 300Hz, silence, 250Hz
    pitches = np.concatenate([
        np.full(20, 200.0),  # Note 1: 200 Hz
        np.full(10, 0.0),     # Silence
        np.full(20, 300.0),  # Note 2: 300 Hz
        np.full(10, 0.0),     # Silence
        np.full(20, 250.0),  # Note 3: 250 Hz
        np.full(20, 0.0)      # Trailing silence
    ])

    # Segment notes
    notes = segment_notes(times, pitches,
                         min_note_duration=0.1,
                         pitch_tolerance=20)

    assert len(notes) == 3, f"Expected 3 notes, got {len(notes)}"


def test_frequency_conversions():
    """Test frequency conversion utilities"""
    print("=" * 60)
    print("Test 4: Frequency Conversions")
    print("=" * 60)
    
    # Test A4 = 440 Hz = MIDI 69
    freq = 440.0
    midi = hz_to_midi(freq)
    note_name = midi_to_note_name(midi)
    assert abs(midi - 69) < 0.1 and note_name == "A4", f"A4 conversion incorrect: {midi}, {note_name}"

    # Test C4 = 261.63 Hz = MIDI 60
    freq = 261.63
    midi = hz_to_midi(freq)
    note_name = midi_to_note_name(midi)
    assert abs(midi - 60) < 0.1 and note_name == "C4", f"C4 conversion incorrect: {midi}, {note_name}"


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PITCH DETECTION MODULE - TEST SUITE")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Sine Wave Pitch Detection", test_pitch_detection_with_sine_wave()))
    results.append(("Pitch Smoothing", test_pitch_smoothing()))
    results.append(("Note Segmentation", test_note_segmentation()))
    results.append(("Frequency Conversions", test_frequency_conversions()))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<45} {status}")
    
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
