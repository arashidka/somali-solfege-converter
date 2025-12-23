#!/usr/bin/env python3
"""
Melodic Transcription & Solfège Translation System

This script converts musical audio files into solfège notation (Do, Re, Mi, Fa, Sol, La, Ti).
It extracts pitch information from audio and maps it to the appropriate solfège syllables.

Educational purpose: Study intervalic relationships of melodies.
"""

import argparse
import sys
import traceback
from pathlib import Path
from typing import List, Tuple, Optional

try:
    import librosa
    import numpy as np
except ImportError:
    print("Error: Required libraries not installed.")
    print("Please install dependencies: pip install librosa numpy soundfile")
    sys.exit(1)


# Solfège syllables in order (chromatic scale)
SOLFEGE_CHROMATIC = [
    "Do", "Di", "Re", "Ri", "Mi", "Fa", "Fi", "Sol", "Si", "La", "Li", "Ti"
]

# Solfège syllables for major scale (diatonic)
SOLFEGE_DIATONIC = ["Do", "Re", "Mi", "Fa", "Sol", "La", "Ti"]

# Note names in chromatic order
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


class SolfegeConverter:
    """Main class for converting audio to solfège notation."""
    
    def __init__(self, use_chromatic: bool = False, key: str = "C"):
        """
        Initialize the converter.
        
        Args:
            use_chromatic: If True, use chromatic solfège (with sharps/flats)
            key: The key of the music (default: C major)
        """
        self.use_chromatic = use_chromatic
        self.key = key
    
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        Load audio file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            audio, sr = librosa.load(file_path, sr=22050)
            return audio, sr
        except Exception as e:
            raise ValueError(f"Failed to load audio file: {e}")
    
    def extract_pitches(self, audio: np.ndarray, sr: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract pitch information from audio using pitch tracking.
        
        Args:
            audio: Audio time series
            sr: Sample rate
            
        Returns:
            Tuple of (pitch_values_hz, timestamps)
        """
        # Use librosa's pyin (Probabilistic YIN) for pitch tracking
        # This is good for monophonic melodies
        hop_length = 512
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio,
            fmin=librosa.note_to_hz('C2'),  # Lowest note: C2
            fmax=librosa.note_to_hz('C7'),   # Highest note: C7
            sr=sr,
            hop_length=hop_length
        )
        
        # Create timestamps using the same hop_length
        timestamps = librosa.frames_to_time(
            np.arange(len(f0)), 
            sr=sr, 
            hop_length=hop_length
        )
        
        return f0, timestamps
    
    def hz_to_midi(self, hz: float) -> int:
        """
        Convert frequency in Hz to MIDI note number.
        
        Args:
            hz: Frequency in Hz
            
        Returns:
            MIDI note number
        """
        if hz <= 0 or np.isnan(hz):
            return -1
        return int(np.round(librosa.hz_to_midi(hz)))
    
    def midi_to_note_name(self, midi_note: int) -> str:
        """
        Convert MIDI note number to note name.
        
        Args:
            midi_note: MIDI note number
            
        Returns:
            Note name (e.g., "C4", "D#5")
        """
        if midi_note < 0:
            return "Rest"
        note_idx = midi_note % 12
        octave = (midi_note // 12) - 1
        return f"{NOTE_NAMES[note_idx]}{octave}"
    
    def midi_to_solfege(self, midi_note: int, key_root: int = 0) -> str:
        """
        Convert MIDI note to solfège syllable.
        
        Args:
            midi_note: MIDI note number
            key_root: Root note of the key (0=C, 1=C#, 2=D, etc.)
            
        Returns:
            Solfège syllable
        """
        if midi_note < 0:
            return "Rest"
        
        # Calculate scale degree relative to key
        scale_degree = (midi_note - key_root) % 12
        
        if self.use_chromatic:
            return SOLFEGE_CHROMATIC[scale_degree]
        else:
            # Map to diatonic scale (major scale: 0,2,4,5,7,9,11)
            major_scale_degrees = [0, 2, 4, 5, 7, 9, 11]
            if scale_degree in major_scale_degrees:
                diatonic_idx = major_scale_degrees.index(scale_degree)
                return SOLFEGE_DIATONIC[diatonic_idx]
            else:
                # For non-diatonic notes, find nearest and add #/b
                nearest = min(major_scale_degrees, key=lambda x: abs(x - scale_degree))
                diatonic_idx = major_scale_degrees.index(nearest)
                if scale_degree > nearest:
                    return SOLFEGE_DIATONIC[diatonic_idx] + "#"
                else:
                    return SOLFEGE_DIATONIC[diatonic_idx] + "b"
    
    def convert_to_solfege(self, file_path: str, min_duration: float = 0.1) -> List[dict]:
        """
        Main conversion function: audio file -> solfège sequence.
        
        Args:
            file_path: Path to audio file
            min_duration: Minimum duration (seconds) for a note to be included
            
        Returns:
            List of dictionaries with note information
        """
        print(f"Loading audio from: {file_path}")
        audio, sr = self.load_audio(file_path)
        
        print("Extracting pitches...")
        pitches_hz, timestamps = self.extract_pitches(audio, sr)
        
        print("Converting to solfège...")
        
        # Get key root (default C = 0)
        key_root = NOTE_NAMES.index(self.key) if self.key in NOTE_NAMES else 0
        
        # Process pitches
        notes = []
        current_note = None
        current_hz = None
        note_start_time = None
        
        for i, (hz, time) in enumerate(zip(pitches_hz, timestamps)):
            midi_note = self.hz_to_midi(hz)
            
            # Handle note changes or silence
            if current_note != midi_note:
                # Save previous note if it existed long enough
                if current_note is not None and note_start_time is not None:
                    duration = time - note_start_time
                    if duration >= min_duration:
                        note_name = self.midi_to_note_name(current_note)
                        solfege = self.midi_to_solfege(current_note, key_root)
                        notes.append({
                            'time': note_start_time,
                            'duration': duration,
                            'midi': current_note,
                            'note': note_name,
                            'solfege': solfege,
                            'hz': current_hz
                        })
                
                # Start new note
                current_note = midi_note
                current_hz = hz
                note_start_time = time
        
        # Add last note
        if current_note is not None and note_start_time is not None:
            duration = timestamps[-1] - note_start_time
            if duration >= min_duration:
                note_name = self.midi_to_note_name(current_note)
                solfege = self.midi_to_solfege(current_note, key_root)
                notes.append({
                    'time': note_start_time,
                    'duration': duration,
                    'midi': current_note,
                    'note': note_name,
                    'solfege': solfege,
                    'hz': current_hz
                })
        
        return notes
    
    def format_output(self, notes: List[dict], verbose: bool = False) -> str:
        """
        Format the solfège sequence for output.
        
        Args:
            notes: List of note dictionaries
            verbose: If True, include detailed information
            
        Returns:
            Formatted string
        """
        if not notes:
            return "No notes detected in the audio."
        
        output = []
        output.append(f"\nDetected {len(notes)} notes:")
        output.append("=" * 60)
        
        if verbose:
            output.append(f"{'Time':>8} {'Duration':>10} {'Note':>8} {'Solfège':>10} {'Hz':>10}")
            output.append("-" * 60)
            for note in notes:
                output.append(
                    f"{note['time']:>8.2f} {note['duration']:>10.3f} "
                    f"{note['note']:>8} {note['solfege']:>10} {note['hz']:>10.1f}"
                )
        else:
            output.append("\nSolfège Sequence:")
            solfege_seq = " - ".join([note['solfege'] for note in notes])
            output.append(solfege_seq)
            
            output.append("\nNote Sequence:")
            note_seq = " - ".join([note['note'] for note in notes])
            output.append(note_seq)
        
        output.append("=" * 60)
        return "\n".join(output)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Melodic Transcription & Solfège Translation System",
        epilog="Example: python solfege_converter.py input.wav -k C -v"
    )
    
    parser.add_argument(
        "audio_file",
        help="Path to audio file (WAV, MP3, etc.)"
    )
    
    parser.add_argument(
        "-k", "--key",
        default="C",
        help="Musical key of the piece (default: C)"
    )
    
    parser.add_argument(
        "-c", "--chromatic",
        action="store_true",
        help="Use chromatic solfège (includes sharps/flats)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output with timestamps and frequencies"
    )
    
    parser.add_argument(
        "-m", "--min-duration",
        type=float,
        default=0.1,
        help="Minimum note duration in seconds (default: 0.1)"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file to save results (optional)"
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"Error: Audio file not found: {audio_path}")
        sys.exit(1)
    
    # Create converter and process
    try:
        converter = SolfegeConverter(
            use_chromatic=args.chromatic,
            key=args.key
        )
        
        notes = converter.convert_to_solfege(
            str(audio_path),
            min_duration=args.min_duration
        )
        
        output = converter.format_output(notes, verbose=args.verbose)
        print(output)
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"\nResults saved to: {args.output}")
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
