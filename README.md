# Somali Solfege Converter

A Python-based audio/video processing system for converting musical content to Somali solfege notation.

## Features

### Phase 1: Audio Extraction & Pre-processing (Current)
- 🎥 Video-to-audio extraction (supports MP4, MOV, AVI, MKV)
- 🎵 Audio file loading (supports WAV, MP3, FLAC, OGG)
- 🔊 Automatic stereo-to-mono conversion
- ⚡ Memory-efficient processing with 22.05kHz downsampling
- 🧹 Automatic cleanup of temporary files

### Future Phases
- Phase 2: Pitch Detection using YIN Algorithm
- Phase 3: Note Segmentation
- Phase 4: Somali Pentatonic Scale Mapping

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

### As a Python Module

```python
from audio_processor import prepare_audio_input, check_dependencies

# Check dependencies
check_dependencies()

# Process audio from video or audio file
samples, sample_rate = prepare_audio_input("your_file.mp4")

# samples is a numpy array of normalized audio data
# sample_rate is 22050 Hz by default
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