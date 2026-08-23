import math
import wave
import struct
import random
import numpy as np
from pathlib import Path

def generate_cinematic_whoosh(output_wav: Path, duration: float = 0.6, sample_rate: int = 44100, style: str = "auto"):
    """
    Sintetiza un efecto de sonido (SFX) cinemático profesional con 4 estilos dinámicos:
    1. 'sub_drop': Sub-bass drop profundo (65 Hz -> 35 Hz) con barrido de aire.
    2. 'heartbeat_thump': Doble pulso visceral de latido cardíaco de alta tensión.
    3. 'glitch_riser': Barrido ascendente agresivo (80 Hz -> 1800 Hz) con textura metálica.
    4. 'thunder_hit': Impacto orquestal cinematográfico con reverb espacial simulada.
    """
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    num_samples = int(duration * sample_rate)
    
    styles = ["sub_drop", "heartbeat_thump", "glitch_riser", "thunder_hit"]
    if style == "auto" or style not in styles:
        style = random.choice(styles)
        
    t = np.linspace(0, 1, num_samples)
    white_noise = np.random.uniform(-1.0, 1.0, num_samples)
    
    if style == "sub_drop":
        # Barrido de frecuencia descendente con sub-graves
        envelope = np.sin(np.pi * (t ** 0.8)) ** 2
        sweep_phase = np.cumsum(180 + 2000 * np.sin(np.pi * t) ** 1.8) / sample_rate
        synth_air = np.sin(2 * np.pi * sweep_phase)
        sub_phase = np.cumsum(70 - 35 * t) / sample_rate
        sub_bass = np.sin(2 * np.pi * sub_phase) * np.exp(-3.5 * t)
        combined_mono = (white_noise * 0.35 + synth_air * 0.30 + sub_bass * 0.35) * envelope

    elif style == "heartbeat_thump":
        # Doble latido de alta tensión
        envelope1 = np.exp(-((t - 0.15) ** 2) / (2 * (0.04 ** 2)))
        envelope2 = np.exp(-((t - 0.45) ** 2) / (2 * (0.05 ** 2)))
        sub1 = np.sin(2 * np.pi * 52 * t) * envelope1
        sub2 = np.sin(2 * np.pi * 44 * t) * envelope2
        combined_mono = (sub1 * 0.7 + sub2 * 0.8 + white_noise * 0.15 * (envelope1 + envelope2))

    elif style == "glitch_riser":
        # Riser ascendente de tensión
        envelope = (t ** 1.5) * np.exp(-2.0 * (1.0 - t))
        rise_phase = np.cumsum(90 + 1600 * (t ** 2)) / sample_rate
        synth_rise = np.sin(2 * np.pi * rise_phase)
        combined_mono = (white_noise * 0.4 + synth_rise * 0.6) * envelope

    else: # "thunder_hit"
        # Impacto orquestal explosivo con decaimiento natural
        envelope = np.exp(-4.5 * t)
        impact_sub = np.sin(2 * np.pi * (60 - 25 * t) * t) * envelope
        snap = (white_noise * np.exp(-25 * t)) * 0.5
        combined_mono = impact_sub * 0.75 + snap + (white_noise * 0.25 * envelope)

    # Calibrar ganancia (-16 dB) y espacialidad estéreo
    gain = 0.24
    left_channel = combined_mono * gain * (0.85 + 0.15 * np.cos(np.pi * t))
    right_channel = combined_mono * gain * (0.85 - 0.15 * np.cos(np.pi * t))
    
    left_int = np.int16(np.clip(left_channel, -1.0, 1.0) * 32767)
    right_int = np.int16(np.clip(right_channel, -1.0, 1.0) * 32767)
    
    stereo_interleaved = np.empty((num_samples * 2,), dtype=np.int16)
    stereo_interleaved[0::2] = left_int
    stereo_interleaved[1::2] = right_int
    
    with wave.open(str(output_wav), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(stereo_interleaved.tobytes())
        
    return output_wav

def generate_ambient_cinematic_music(output_wav: Path, duration: float = 65.0, sample_rate: int = 44100):
    """
    Sintetiza una pista musical de fondo atmosférica cinemática con progresión armónica cambiante.
    """
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    num_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    
    chord_duration = 7.5
    num_chords = int(np.ceil(duration / chord_duration))
    
    # Progresiones cinematográficas variadas (Modos Dm, Am, Em, Bm)
    progressions = [
        [[73.42, 110.00, 146.83, 220.00, 293.66], [87.31, 130.81, 174.61, 261.63, 349.23], [65.41, 98.00, 130.81, 196.00, 261.63], [98.00, 146.83, 196.00, 293.66, 392.00]],
        [[55.00, 82.41, 110.00, 164.81, 220.00], [65.41, 98.00, 130.81, 196.00, 261.63], [73.42, 110.00, 146.83, 220.00, 293.66], [82.41, 123.47, 164.81, 246.94, 329.63]],
        [[82.41, 123.47, 164.81, 246.94, 329.63], [73.42, 110.00, 146.83, 220.00, 293.66], [65.41, 98.00, 130.81, 196.00, 261.63], [55.00, 82.41, 110.00, 164.81, 220.00]]
    ]
    chords = random.choice(progressions)
    
    music_mix = np.zeros(num_samples)
    
    for c_idx in range(num_chords):
        chord_freqs = chords[c_idx % len(chords)]
        start_samp = int(c_idx * chord_duration * sample_rate)
        end_samp = min(int((c_idx + 1) * chord_duration * sample_rate), num_samples)
        seg_len = end_samp - start_samp
        
        seg_t = np.linspace(0, seg_len / sample_rate, seg_len, endpoint=False)
        env = np.sin(np.pi * np.linspace(0, 1, seg_len)) ** 1.2
        
        chord_signal = np.zeros(seg_len)
        for f in chord_freqs:
            chord_signal += np.sin(2 * np.pi * f * seg_t) * 0.4
            chord_signal += np.sin(2 * np.pi * (f * 2.005) * seg_t) * 0.18
            chord_signal += np.sin(2 * np.pi * (f * 3.01) * seg_t) * 0.06
            
        music_mix[start_samp:end_samp] += chord_signal * env
        
    norm_factor = np.max(np.abs(music_mix)) + 1e-6
    music_mix = (music_mix / norm_factor) * 0.16 # -16 dB para fondo limpio
    
    left_channel = music_mix * 0.9
    right_channel = music_mix * 0.95
    
    left_int = np.int16(np.clip(left_channel, -1.0, 1.0) * 32767)
    right_int = np.int16(np.clip(right_channel, -1.0, 1.0) * 32767)
    
    stereo_interleaved = np.empty((num_samples * 2,), dtype=np.int16)
    stereo_interleaved[0::2] = left_int
    stereo_interleaved[1::2] = right_int
    
    with wave.open(str(output_wav), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(stereo_interleaved.tobytes())
        
    return output_wav
