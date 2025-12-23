#!/usr/bin/env python3
"""
Generate a simple test audio file with a C major scale.
This is used for testing the solfège converter.
"""

import numpy as np
import soundfile as sf

# Parameters
sample_rate = 22050
note_duration = 0.5  # seconds

# C major scale frequencies (C4 to C5)
# Do, Re, Mi, Fa, Sol, La, Ti, Do
notes_hz = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]

# Generate audio
audio = []
for freq in notes_hz:
    t = np.linspace(0, note_duration, int(sample_rate * note_duration))
    # Simple sine wave
    note = np.sin(2 * np.pi * freq * t)
    # Apply envelope to avoid clicks
    envelope = np.ones_like(t)
    fade_samples = int(sample_rate * 0.02)  # 20ms fade
    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
    note = note * envelope
    audio.extend(note)

audio = np.array(audio)

# Save as WAV file
output_file = "test_c_major_scale.wav"
sf.write(output_file, audio, sample_rate)
print(f"Created test audio file: {output_file}")
print(f"Duration: {len(audio) / sample_rate:.2f} seconds")
print(f"Notes: C major scale (Do Re Mi Fa Sol La Ti Do)")
