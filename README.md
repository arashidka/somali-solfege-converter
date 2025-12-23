# Somali Solfege Converter

A Python-based audio/video processing system for converting musical content to Somali solfege notation.

## Features

### Phase 1: Audio Extraction & Pre-processing ✅
- 🎥 Video-to-audio extraction (supports MP4, MOV, AVI, MKV)
- 🎵 Audio file loading (supports WAV, MP3, FLAC, OGG)
- 🔊 Automatic stereo-to-mono conversion
- ⚡ Memory-efficient processing with 22.05kHz downsampling
- 🧹 Automatic cleanup of temporary files

### Phase 2: Pitch Detection & Note Segmentation ✅
- 🎼 YIN Algorithm for robust pitch detection
- 📊 Median filtering for smooth pitch tracks
- 🎵 Automatic note segmentation
- 📈 Pitch visualization with note boundaries
- 🎯 Optimized for clean frequency tracking (80-800 Hz range)
- 💡 Suitable for Somali Pentatonic practice

### Future Phases
- Phase 3: Somali Pentatonic Scale Mapping
- Phase 4: Solfege Notation Export

## Installation

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

### As a Jupyter Notebook
Open `audio_processing.ipynb` in Jupyter Notebook or VS Code with Jupyter extension:

```bash
jupyter notebook audio_processing.ipynb
```

Follow the cells in order to:
1. Check and install dependencies
2. Load and process audio from video or audio files
3. Visualize the audio waveform
4. Detect pitch using YIN algorithm
5. Smooth pitch track and segment into notes
6. Visualize pitch detection results

### As a Python Module

**Phase 1: Audio Processing**

```python
from audio_processor import prepare_audio_input, check_dependencies

# Check dependencies
check_dependencies()

# Process audio from video or audio file
samples, sample_rate = prepare_audio_input("your_file.mp4")

# samples is a numpy array of normalized audio data
# sample_rate is actual rate after resampling
```

**Phase 2: Pitch Detection**

```python
from pitch_detector import yin_pitch_detection, smooth_pitch_track, segment_notes

# Detect pitch
times, raw_pitches = yin_pitch_detection(samples, sample_rate)

# Smooth and segment
smoothed_pitches = smooth_pitch_track(raw_pitches, kernel_size=5)
detected_notes = segment_notes(times, smoothed_pitches, 
                               min_note_duration=0.1, 
                               pitch_tolerance=20)

# Analyze results
for i, note in enumerate(detected_notes):
    print(f"Note {i+1}: {note['mean_pitch']:.1f} Hz, "
          f"duration: {note['duration']:.2f}s")
```

## Requirements

- Python 3.8+
- moviepy >= 1.0.3
- numpy >= 1.21.0
- scipy >= 1.7.0
- matplotlib >= 3.4.0
- librosa >= 0.9.0

## Architecture

The system follows a **PRSE (Python Rapid-Systems Engine)** design approach:

- **Architectural Pattern:** Procedural (linear pipeline)
- **Memory Optimization:** Float32 conversion, immediate cleanup of video objects
- **Target Sample Rate:** 22.05kHz for 8GB RAM systems
- **Processing Pipeline:** Video → Audio Extraction → Resampling → Normalization → Analysis

## License

MIT License