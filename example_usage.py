#!/usr/bin/env python3
"""
Example script demonstrating programmatic usage of the Solfège Converter.

This shows how to use the SolfegeConverter class in your own Python scripts.
"""

from solfege_converter import SolfegeConverter


def example_basic_usage():
    """Basic example: convert an audio file to solfège."""
    print("=== Basic Usage Example ===\n")
    
    # Create converter with default settings (C major, diatonic)
    converter = SolfegeConverter()
    
    # Convert audio file
    # Note: Replace with an actual audio file path to test
    audio_file = "example_melody.wav"
    
    try:
        notes = converter.convert_to_solfege(audio_file)
        output = converter.format_output(notes)
        print(output)
    except FileNotFoundError:
        print(f"Example file '{audio_file}' not found.")
        print("To use this example, provide a valid audio file path.")


def example_chromatic_mode():
    """Example: using chromatic solfège."""
    print("\n=== Chromatic Mode Example ===\n")
    
    # Create converter with chromatic mode enabled
    converter = SolfegeConverter(use_chromatic=True)
    
    audio_file = "chromatic_melody.wav"
    
    try:
        notes = converter.convert_to_solfege(audio_file)
        output = converter.format_output(notes, verbose=True)
        print(output)
    except FileNotFoundError:
        print(f"Example file '{audio_file}' not found.")


def example_different_key():
    """Example: converting in a different key."""
    print("\n=== Different Key Example (G Major) ===\n")
    
    # Create converter for G major
    converter = SolfegeConverter(key="G")
    
    audio_file = "g_major_melody.wav"
    
    try:
        notes = converter.convert_to_solfege(audio_file)
        
        # Print just the solfège sequence
        if notes:
            solfege_sequence = " - ".join([note['solfege'] for note in notes])
            print(f"Solfège Sequence: {solfege_sequence}")
            
            # Print intervalic analysis
            print("\nIntervalic Analysis:")
            for i in range(len(notes) - 1):
                current = notes[i]['solfege']
                next_note = notes[i + 1]['solfege']
                interval = notes[i + 1]['midi'] - notes[i]['midi']
                print(f"  {current} -> {next_note}: {interval:+d} semitones")
    except FileNotFoundError:
        print(f"Example file '{audio_file}' not found.")


def example_custom_processing():
    """Example: custom processing of detected notes."""
    print("\n=== Custom Processing Example ===\n")
    
    converter = SolfegeConverter()
    audio_file = "melody.wav"
    
    try:
        notes = converter.convert_to_solfege(audio_file, min_duration=0.15)
        
        if notes:
            # Calculate statistics
            total_duration = sum(note['duration'] for note in notes)
            avg_duration = total_duration / len(notes)
            
            # Find pitch range
            midi_notes = [note['midi'] for note in notes if note['midi'] >= 0]
            if midi_notes:
                lowest = min(midi_notes)
                highest = max(midi_notes)
                range_semitones = highest - lowest
                
                print(f"Total notes: {len(notes)}")
                print(f"Total duration: {total_duration:.2f} seconds")
                print(f"Average note duration: {avg_duration:.3f} seconds")
                print(f"Pitch range: {range_semitones} semitones")
                print(f"Lowest note: {converter.midi_to_note_name(lowest)}")
                print(f"Highest note: {converter.midi_to_note_name(highest)}")
                
                # Most common solfège syllable
                solfege_counts = {}
                for note in notes:
                    solfege = note['solfege']
                    solfege_counts[solfege] = solfege_counts.get(solfege, 0) + 1
                
                most_common = max(solfege_counts.items(), key=lambda x: x[1])
                print(f"\nMost common solfège: {most_common[0]} ({most_common[1]} times)")
    except FileNotFoundError:
        print(f"Example file '{audio_file}' not found.")
        print("These are just examples. Replace with actual audio files to test.")


def main():
    """Run all examples."""
    print("Solfège Converter - Programmatic Usage Examples")
    print("=" * 60)
    
    example_basic_usage()
    example_chromatic_mode()
    example_different_key()
    example_custom_processing()
    
    print("\n" + "=" * 60)
    print("Note: These examples require actual audio files to run.")
    print("You can create test audio or use recordings of melodies.")


if __name__ == "__main__":
    main()
