# Melodic Transcription & Solfège Translation System

A simple, educational tool for converting musical audio files into readable solfège sequences (Do, Re, Mi, Fa, Sol, La, Ti). This system helps you study the intervalic relationships of melodies by transcribing audio into solfège notation.

## Features

- 🎵 **Audio-to-Solfège Conversion**: Automatically transcribe melodies from audio files
- 🎼 **Multiple Formats**: Supports WAV, MP3, and other common audio formats
- 🎹 **Chromatic & Diatonic Modes**: Choose between standard diatonic or chromatic solfège
- 🔑 **Key Detection Support**: Specify the musical key for accurate solfège mapping
- 📊 **Detailed Analysis**: Optional verbose mode with timestamps, frequencies, and note durations
- 💻 **Single-File Implementation**: Simple, easy-to-understand codebase

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/arashidka/somali-solfege-converter.git
cd somali-solfege-converter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Convert an audio file to solfège notation:

```bash
python solfege_converter.py your_audio_file.wav
```

### Advanced Options

```bash
# Specify the musical key (default: C)
python solfege_converter.py song.mp3 -k G

# Use chromatic solfège (includes sharps/flats)
python solfege_converter.py melody.wav --chromatic

# Show detailed output with timestamps and frequencies
python solfege_converter.py audio.wav --verbose

# Set minimum note duration (in seconds)
python solfege_converter.py music.mp3 -m 0.2

# Save output to a file
python solfege_converter.py tune.wav -o output.txt

# Combine multiple options
python solfege_converter.py song.wav -k D --chromatic --verbose -o results.txt
```

### Command-Line Arguments

- `audio_file`: Path to the audio file (required)
- `-k, --key`: Musical key of the piece (default: C)
- `-c, --chromatic`: Use chromatic solfège notation
- `-v, --verbose`: Show detailed output with timestamps and frequencies
- `-m, --min-duration`: Minimum note duration in seconds (default: 0.1)
- `-o, --output`: Save results to output file

### Example Output

**Simple Mode:**
```
Detected 8 notes:
============================================================

Solfège Sequence:
Do - Re - Mi - Fa - Sol - La - Ti - Do

Note Sequence:
C4 - D4 - E4 - F4 - G4 - A4 - B4 - C5
```

**Verbose Mode:**
```
Detected 8 notes:
============================================================
    Time   Duration     Note    Solfège         Hz
------------------------------------------------------------
    0.12      0.250       C4         Do      261.6
    0.37      0.250       D4         Re      293.7
    0.62      0.250       E4         Mi      329.6
    0.87      0.250       F4         Fa      349.2
    1.12      0.250       G4        Sol      392.0
    1.37      0.250       A4         La      440.0
    1.62      0.250       B4         Ti      493.9
    1.87      0.250       C5         Do      523.3
============================================================
```

## How It Works

1. **Audio Loading**: Uses librosa to load audio files
2. **Pitch Extraction**: Employs pYIN (Probabilistic YIN) algorithm for monophonic pitch tracking
3. **Note Detection**: Identifies distinct notes by tracking pitch changes
4. **Solfège Mapping**: Converts detected pitches to solfège syllables based on the specified key
5. **Output Formatting**: Presents results in a clear, educational format

## Educational Use Cases

- **Melody Analysis**: Study the intervalic structure of songs
- **Ear Training**: Compare your perception with the actual notes
- **Music Theory**: Understand scale degrees and relationships
- **Transcription Practice**: Check your manual transcriptions
- **Composition**: Analyze melodic patterns in favorite pieces

## Limitations

- **Monophonic Audio**: Best results with single-note melodies (no chords or harmony)
- **Clean Audio**: Works best with clear recordings without much background noise
- **Pitch Range**: Detects pitches from C2 (65 Hz) to C7 (2093 Hz)

## Technical Details

### Dependencies

- **librosa**: Audio analysis and pitch detection
- **numpy**: Numerical computations
- **soundfile**: Audio file I/O
- **scipy**: Signal processing

### Algorithm

The system uses the pYIN (Probabilistic YIN) pitch detection algorithm, which is particularly effective for monophonic audio. It tracks fundamental frequency over time and converts these frequencies to MIDI note numbers, which are then mapped to solfège syllables based on the specified key.

## Contributing

Contributions are welcome! This is a simple, educational project focused on single-file implementations. Please maintain the simplicity when suggesting enhancements.

## License

This project is open source and available for educational purposes.

## Acknowledgments

- Built with [librosa](https://librosa.org/) - a Python package for music and audio analysis
- Inspired by the need for accessible music education tools