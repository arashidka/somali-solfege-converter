import os
import tempfile
import json
import csv
import math
import numpy as np
import soundfile as sf
import librosa
from scipy.signal import medfilt

try:
    from moviepy.editor import VideoFileClip
except Exception:
    VideoFileClip = None

try:
    import mido
except Exception:
    mido = None

try:
    import music21 as m21
except Exception:
    m21 = None


def prepare_audio_input(path, target_sr=22050):
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.mp4', '.mov', '.mkv') and VideoFileClip is not None:
        with VideoFileClip(path) as clip:
            tf = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            tmp_path = tf.name
            tf.close()
            clip.audio.write_audiofile(tmp_path, verbose=False, logger=None)
            samples, sr = librosa.load(tmp_path, sr=target_sr, mono=True)
            os.unlink(tmp_path)
    else:
        samples, sr = librosa.load(path, sr=target_sr, mono=True)
    return samples, sr


def yin_pitch_detection(samples, sr, frame_length=1024, hop_length=256, threshold=0.08, freq_min=60, freq_max=1000):
    try:
        f0 = librosa.yin(samples, fmin=freq_min, fmax=freq_max, sr=sr, frame_length=frame_length, hop_length=hop_length, trough_threshold=threshold)
        times = librosa.frames_to_time(np.arange(len(f0)), sr=sr, hop_length=hop_length)
        # librosa.yin returns np.nan for unvoiced
        return times.tolist(), f0.tolist()
    except Exception as e:
        raise


def smooth_pitch_track(pitches, kernel_size=7):
    arr = np.array(pitches, dtype=np.float32)
    # replace nan with 0 for median filter, then restore
    nan_mask = np.isnan(arr)
    arr_filled = np.copy(arr)
    arr_filled[nan_mask] = 0.0
    if kernel_size % 2 == 0:
        kernel_size += 1
    sm = medfilt(arr_filled, kernel_size=kernel_size)
    sm[nan_mask] = np.nan
    return sm.tolist()


def hz_to_midi(freq):
    if freq is None or np.isnan(freq) or freq <= 0:
        return None
    return int(round(69 + 12 * math.log2(freq / 440.0)))


def segment_notes(times, pitches, min_note_duration=0.08, pitch_tolerance=18):
    notes = []
    voiced = [not (p is None or math.isnan(p)) for p in pitches]
    start_idx = None
    for i, v in enumerate(voiced):
        if v and start_idx is None:
            start_idx = i
        elif (not v or i == len(voiced)-1) and start_idx is not None:
            end_idx = i if not v else i+1
            start_t = times[start_idx]
            end_t = times[end_idx-1]
            duration = end_t - start_t
            if duration >= min_note_duration:
                segment_pitches = [p for p in pitches[start_idx:end_idx] if not (p is None or math.isnan(p))]
                if len(segment_pitches) == 0:
                    start_idx = None
                    continue
                mean_pitch = float(np.mean(segment_pitches))
                median_pitch = float(np.median(segment_pitches))
                notes.append({
                    'start_time': float(start_t),
                    'end_time': float(end_t),
                    'duration': float(duration),
                    'mean_pitch': mean_pitch,
                    'median_pitch': median_pitch,
                    'midi_note': hz_to_midi(mean_pitch)
                })
            start_idx = None
    return notes


def save_json_csv_structured(notes, prefix='detected_notes'):
    json_path = f'{prefix}.json'
    with open(json_path, 'w', encoding='utf-8') as jf:
        json.dump(notes, jf, indent=2)
    csv_path = f'{prefix}.csv'
    fieldnames = ['start_time','end_time','duration','mean_pitch','median_pitch','midi_note']
    with open(csv_path, 'w', newline='', encoding='utf-8') as cf:
        writer = csv.DictWriter(cf, fieldnames=fieldnames)
        writer.writeheader()
        for n in notes:
            writer.writerow({k: n.get(k, '') for k in fieldnames})
    structured_path = f'{prefix}_structured.json'
    with open(structured_path, 'w', encoding='utf-8') as sf:
        json.dump(notes, sf, indent=2)
    return json_path, csv_path, structured_path


def write_midi(notes, path='detected_notes.mid', tempo_bpm=120):
    if mido is None:
        return None
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo_bpm)))
    ticks_per_beat = mid.ticks_per_beat
    tempo = mido.bpm2tempo(tempo_bpm)
    ticks_per_second = ticks_per_beat * 1e6 / tempo
    last_tick = 0
    for n in notes:
        start_tick = int(n['start_time'] * ticks_per_second)
        end_tick = int(n['end_time'] * ticks_per_second)
        delta = start_tick - last_tick
        if delta < 0:
            delta = 0
        midi_note = n.get('midi_note')
        if midi_note is None:
            continue
        track.append(mido.Message('note_on', note=midi_note, velocity=64, time=delta))
        track.append(mido.Message('note_off', note=midi_note, velocity=64, time=(end_tick - start_tick)))
        last_tick = end_tick
    mid.save(path)
    return path


def export_musicxml(notes, path='detected_notes.musicxml', tempo_bpm=120):
    if m21 is None:
        return None
    s = m21.stream.Stream()
    ts = m21.tempo.MetronomeMark(number=tempo_bpm)
    s.append(ts)
    for n in notes:
        midi = n.get('midi_note')
        if midi is None:
            continue
        dur_seconds = n.get('duration', 0.0)
        quarter_length = dur_seconds * (tempo_bpm / 60.0)
        m = m21.note.Note(m21.pitch.Pitch(midi=midi))
        m.quarterLength = quarter_length
        s.append(m)
    s.write('musicxml', fp=path)
    return path


def synth_preview(notes, path='detected_notes_preview.wav', sr=44100):
    total_dur = 0.0
    for n in notes:
        total_dur = max(total_dur, n['end_time'])
    out = np.zeros(int(total_dur * sr) + 1, dtype=np.float32)
    for n in notes:
        midi = n.get('midi_note')
        if midi is None:
            continue
        freq = 440.0 * (2.0 ** ((midi - 69) / 12.0))
        start = int(n['start_time'] * sr)
        end = int(n['end_time'] * sr)
        t = np.linspace(0, n['duration'], end-start, endpoint=False)
        tone = 0.12 * np.sin(2 * np.pi * freq * t)
        out[start:end] += tone
    # normalize
    maxv = np.max(np.abs(out))
    if maxv > 0:
        out = out / maxv * 0.9
    sf.write(path, out, sr)
    return path


if __name__ == '__main__':
    INPUT = os.path.join(os.path.dirname(__file__), 'testVideo.mp4')
    if not os.path.exists(INPUT):
        INPUT = os.path.join(os.path.dirname(__file__), 'testAudio.wav')
    print('Input file:', INPUT)
    samples, sr = prepare_audio_input(INPUT, target_sr=22050)
    print(f'Loaded {len(samples)/sr:.2f}s of audio at {sr}Hz')
    times, raw_pitches = yin_pitch_detection(samples, sr, frame_length=1024, hop_length=256, threshold=0.08, freq_min=60, freq_max=1000)
    print('Detected frames:', len(times))
    smoothed = smooth_pitch_track(raw_pitches, kernel_size=7)
    notes = segment_notes(times, smoothed, min_note_duration=0.08, pitch_tolerance=18)
    print('Segmented notes:', len(notes))
    from datetime import datetime
    prefix = f"detected_notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    j, c, s = save_json_csv_structured(notes, prefix=prefix)
    print('Saved:', j, c, s)
    midi_path = write_midi(notes, path=f"{prefix}.mid") if mido is not None else None
    if midi_path:
        print('Saved MIDI:', midi_path)
    xml_path = export_musicxml(notes, path=f"{prefix}.musicxml") if m21 is not None else None
    if xml_path:
        print('Saved MusicXML:', xml_path)
    wav_preview = synth_preview(notes, path=f"{prefix}_preview.wav")
    print('Saved preview WAV:', wav_preview)
