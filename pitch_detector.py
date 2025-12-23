"""
Pitch Detection Module for Somali Solfege Converter

This module implements the YIN algorithm for accurate pitch detection
and note segmentation, optimized for musical analysis.
"""

import numpy as np
from scipy.signal import medfilt


def yin_pitch_detection(audio_samples, sr, frame_length=2048, hop_length=512, 
                        threshold=0.1, freq_min=80, freq_max=800):
    """
    Implement the YIN algorithm for pitch detection.
    
    The YIN algorithm is robust for musical pitch tracking and works well
    for monophonic signals like voice or single instruments.
    
    Args:
        audio_samples (np.array): Audio samples (float32, normalized)
        sr (int): Sample rate in Hz
        frame_length (int): Frame size for analysis (default: 2048 samples)
        hop_length (int): Hop size between frames (default: 512 samples)
        threshold (float): Threshold for pitch detection (default: 0.1)
        freq_min (float): Minimum frequency to detect in Hz (default: 80)
        freq_max (float): Maximum frequency to detect in Hz (default: 800)
    
    Returns:
        tuple: (times, pitches) where times are frame times in seconds and
               pitches are detected frequencies in Hz (0 = no pitch detected)
    """
    # Calculate lag range based on frequency limits
    lag_min = int(sr / freq_max)
    lag_max = int(sr / freq_min)
    
    # Number of frames
    n_frames = 1 + (len(audio_samples) - frame_length) // hop_length
    
    # Output arrays
    times = np.arange(n_frames) * hop_length / sr
    pitches = np.zeros(n_frames)
    
    # Process each frame
    for frame_idx in range(n_frames):
        start = frame_idx * hop_length
        end = start + frame_length
        
        if end > len(audio_samples):
            break
            
        frame = audio_samples[start:end]
        
        # YIN algorithm steps
        # Step 1: Difference function
        diff = np.zeros(lag_max)
        for lag in range(lag_min, lag_max):
            for j in range(frame_length - lag):
                delta = frame[j] - frame[j + lag]
                diff[lag] += delta * delta
        
        # Step 2: Cumulative mean normalized difference
        cmnd = np.ones(lag_max)
        cumsum = 0
        for lag in range(lag_min, lag_max):
            cumsum += diff[lag]
            if cumsum > 0:
                cmnd[lag] = diff[lag] / (cumsum / lag)
        
        # Step 3: Absolute threshold
        # Find the first lag where CMND drops below threshold
        pitch_lag = None
        for lag in range(lag_min, lag_max):
            if cmnd[lag] < threshold:
                pitch_lag = lag
                break
        
        # Step 4: Parabolic interpolation for accuracy
        if pitch_lag is not None and lag_min < pitch_lag < lag_max - 1:
            # Refine the lag estimate using parabolic interpolation
            alpha = cmnd[pitch_lag - 1]
            beta = cmnd[pitch_lag]
            gamma = cmnd[pitch_lag + 1]
            
            if alpha > beta and gamma > beta:
                peak_offset = 0.5 * (alpha - gamma) / (alpha - 2 * beta + gamma)
                refined_lag = pitch_lag + peak_offset
                pitches[frame_idx] = sr / refined_lag
            else:
                pitches[frame_idx] = sr / pitch_lag
        else:
            pitches[frame_idx] = 0.0  # No pitch detected
    
    return times, pitches


def smooth_pitch_track(pitches, kernel_size=5):
    """
    Smooth the pitch track using median filtering to remove outliers.
    
    Args:
        pitches (np.array): Raw pitch values in Hz
        kernel_size (int): Size of median filter kernel (default: 5)
    
    Returns:
        np.array: Smoothed pitch values
    """
    # Only smooth non-zero pitches
    smoothed = pitches.copy()
    non_zero_mask = pitches > 0
    
    if np.sum(non_zero_mask) > kernel_size:
        smoothed[non_zero_mask] = medfilt(pitches[non_zero_mask], kernel_size=kernel_size)
    
    return smoothed


def segment_notes(times, pitches, min_note_duration=0.1, pitch_tolerance=20):
    """
    Segment the pitch track into individual notes.
    
    Args:
        times (np.array): Time stamps in seconds
        pitches (np.array): Pitch values in Hz (0 = no pitch)
        min_note_duration (float): Minimum note duration in seconds (default: 0.1s)
        pitch_tolerance (float): Pitch tolerance in Hz for grouping (default: 20 Hz)
    
    Returns:
        list: List of note dictionaries with keys:
              - 'start_time': Start time in seconds
              - 'end_time': End time in seconds
              - 'duration': Duration in seconds
              - 'mean_pitch': Mean pitch in Hz
              - 'median_pitch': Median pitch in Hz
    """
    if len(times) == 0 or len(pitches) == 0:
        return []
    
    notes = []
    current_note = None
    
    for i, (time, pitch) in enumerate(zip(times, pitches)):
        if pitch > 0:  # Voiced frame
            if current_note is None:
                # Start a new note
                current_note = {
                    'start_time': time,
                    'start_idx': i,
                    'pitches': [pitch]
                }
            else:
                # Check if this pitch is similar to current note
                mean_pitch = np.mean(current_note['pitches'])
                if abs(pitch - mean_pitch) < pitch_tolerance:
                    # Continue current note
                    current_note['pitches'].append(pitch)
                else:
                    # End current note and start new one
                    end_time = times[i - 1] if i > 0 else time
                    duration = end_time - current_note['start_time']
                    
                    if duration >= min_note_duration:
                        current_note['end_time'] = end_time
                        current_note['duration'] = duration
                        current_note['mean_pitch'] = np.mean(current_note['pitches'])
                        current_note['median_pitch'] = np.median(current_note['pitches'])
                        notes.append(current_note)
                    
                    # Start new note
                    current_note = {
                        'start_time': time,
                        'start_idx': i,
                        'pitches': [pitch]
                    }
        else:  # Unvoiced frame
            if current_note is not None:
                # End current note
                end_time = times[i - 1] if i > 0 else time
                duration = end_time - current_note['start_time']
                
                if duration >= min_note_duration:
                    current_note['end_time'] = end_time
                    current_note['duration'] = duration
                    current_note['mean_pitch'] = np.mean(current_note['pitches'])
                    current_note['median_pitch'] = np.median(current_note['pitches'])
                    notes.append(current_note)
                
                current_note = None
    
    # Handle the last note if it exists
    if current_note is not None:
        end_time = times[-1]
        duration = end_time - current_note['start_time']
        
        if duration >= min_note_duration:
            current_note['end_time'] = end_time
            current_note['duration'] = duration
            current_note['mean_pitch'] = np.mean(current_note['pitches'])
            current_note['median_pitch'] = np.median(current_note['pitches'])
            notes.append(current_note)
    
    return notes


def hz_to_midi(freq_hz):
    """
    Convert frequency in Hz to MIDI note number.
    
    Args:
        freq_hz (float): Frequency in Hz
    
    Returns:
        float: MIDI note number (can be fractional for microtones)
    """
    if freq_hz <= 0:
        return 0
    return 69 + 12 * np.log2(freq_hz / 440.0)


def midi_to_note_name(midi_number):
    """
    Convert MIDI note number to note name.
    
    Args:
        midi_number (float): MIDI note number
    
    Returns:
        str: Note name (e.g., "C4", "A4")
    """
    if midi_number <= 0:
        return "---"
    
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = int(midi_number // 12) - 1
    note_idx = int(round(midi_number)) % 12
    
    return f"{note_names[note_idx]}{octave}"


if __name__ == "__main__":
    print("Pitch Detection Module for Somali Solfege Converter")
    print("=" * 60)
    print("Available functions:")
    print("  - yin_pitch_detection(): YIN algorithm for pitch tracking")
    print("  - smooth_pitch_track(): Median filtering for noise reduction")
    print("  - segment_notes(): Segment pitch track into individual notes")
    print("  - hz_to_midi(): Convert Hz to MIDI note number")
    print("  - midi_to_note_name(): Convert MIDI to note name")
