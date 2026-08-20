import math
import wave
import struct
import numpy as np
from pathlib import Path

def generate_cinematic_whoosh(output_wav: Path, duration: float = 0.5, sample_rate: int = 44100):
    """
    Sintetiza un efecto de sonido (SFX) cinemático profesional:
    - Ruido rosa filtrado con barrido exponencial de frecuencia (Low-Pass Filter).
    - Pulso de sub-graves sutil (50 Hz) para dar peso y presencia de estudio.
    - Curva de volumen suave (ataque rápido y caída gradual) calibrada a nivel profesional (-16 dB).
    """
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    num_samples = int(duration * sample_rate)
    
    # 1. Ruido blanco base
    np.random.seed(42)
    white_noise = np.random.uniform(-1.0, 1.0, num_samples)
    
    # 2. Generar ruido rosa mediante filtro de integración suave
    pink_noise = np.zeros(num_samples)
    b0, b1, b2 = 0.0, 0.0, 0.0
    for i in range(num_samples):
        white = white_noise[i]
        b0 = 0.99886 * b0 + white * 0.0555179
        b1 = 0.99332 * b1 + white * 0.0750759
        b2 = 0.96900 * b2 + white * 0.1538520
        pink_noise[i] = b0 + b1 + b2 + white * 0.5362
        
    # Normalizar
    pink_noise = pink_noise / (np.max(np.abs(pink_noise)) + 1e-6)
    
    # 3. Barrido de frecuencia resonante (Whoosh sweep de 150 Hz a 2400 Hz y caída)
    t = np.linspace(0, 1, num_samples)
    
    # Curva de envolvente de volumen profesional (Fade in en 35%, Fade out en 65%)
    # Ataque suave y cola larga
    envelope = np.sin(np.pi * (t ** 0.8)) ** 2
    
    # Modulación de tono cinemático
    sweep_phase = np.cumsum(150 + 2200 * np.sin(np.pi * t) ** 1.8) / sample_rate
    synth_air = np.sin(2 * np.pi * sweep_phase)
    
    # 4. Pulso de sub-graves (Sub-bass drop de 65 Hz a 35 Hz)
    sub_phase = np.cumsum(65 - 30 * t) / sample_rate
    sub_bass = np.sin(2 * np.pi * sub_phase) * np.exp(-4 * t)
    
    # 5. Mezcla estéreo profesional con paneo suave
    combined_mono = (pink_noise * 0.45 + synth_air * 0.25 + sub_bass * 0.30) * envelope
    
    # Calibrar volumen a -16 dB para no competir con la voz del locutor
    gain = 0.22
    left_channel = combined_mono * gain * (0.85 + 0.15 * np.cos(np.pi * t))
    right_channel = combined_mono * gain * (0.85 - 0.15 * np.cos(np.pi * t))
    
    # Convertir a 16-bit PCM estéreo
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
    Sintetiza una pista musical de fondo atmosférica cinemática (acordes suaves de sintetizador espacial / misterio)
    con envolventes lentas y ricas en armónicos, perfecta para documentales de curiosidades.
    """
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    num_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    
    # Progresión de acordes cinemáticos envolventes (Frecuencias base en Hz: Dm -> F -> C -> G)
    chord_duration = 8.0 # Cambia cada 8 segundos
    num_chords = int(np.ceil(duration / chord_duration))
    
    # Frecuencias de acordes ambientales profundos (D minor, F major, C major, G sus)
    chords = [
        [73.42, 110.00, 146.83, 220.00, 293.66], # D2, A2, D3, A3, D4
        [87.31, 130.81, 174.61, 261.63, 349.23], # F2, C3, F3, C4, F4
        [65.41, 98.00, 130.81, 196.00, 261.63],  # C2, G2, C3, G3, C4
        [98.00, 146.83, 196.00, 293.66, 392.00]  # G2, D3, G3, D4, G4
    ]
    
    music_mix = np.zeros(num_samples)
    
    for c_idx in range(num_chords):
        chord_freqs = chords[c_idx % len(chords)]
        start_samp = int(c_idx * chord_duration * sample_rate)
        end_samp = min(int((c_idx + 1) * chord_duration * sample_rate), num_samples)
        seg_len = end_samp - start_samp
        
        if seg_len <= 0:
            break
            
        seg_t = np.linspace(0, (seg_len / sample_rate), seg_len, endpoint=False)
        chord_signal = np.zeros(seg_len)
        
        # Generar armónicos ricos con modulación de fase suave (LFO lento para respiración)
        lfo = 1.0 + 0.15 * np.sin(2 * np.pi * 0.25 * seg_t)
        
        for f in chord_freqs:
            chord_signal += np.sin(2 * np.pi * f * seg_t) * 0.4
            chord_signal += np.sin(2 * np.pi * (f * 2.01) * seg_t) * 0.25
            chord_signal += np.sin(2 * np.pi * (f * 3.00) * seg_t) * 0.1
            
        # Envolvente de entrada y salida suave para cada acorde (fade in 2s, fade out 2s)
        fade_len = int(min(2.0 * sample_rate, seg_len / 2))
        env = np.ones(seg_len)
        if fade_len > 0:
            env[:fade_len] = np.sin(np.linspace(0, np.pi/2, fade_len)) ** 2
            env[-fade_len:] = np.cos(np.linspace(0, np.pi/2, fade_len)) ** 2
            
        music_mix[start_samp:end_samp] += chord_signal * env * lfo
        
    # Normalizar mezcla a volumen sutil de fondo (-20 dB)
    music_mix = music_mix / (np.max(np.abs(music_mix)) + 1e-6)
    master_gain = 0.11 # Nivel de mezcla de fondo profesional
    music_final = music_mix * master_gain
    
    # Pulso rítmico ultra-suave (heartbeat sub-bass sutil cada 2 segundos)
    heartbeat = np.sin(2 * np.pi * 45 * t) * np.exp(-12 * (t % 2.0)) * 0.05
    music_final += heartbeat
    
    left_ch = np.int16(np.clip(music_final * 0.95, -1.0, 1.0) * 32767)
    right_ch = np.int16(np.clip(music_final * 1.05, -1.0, 1.0) * 32767)
    
    stereo_data = np.empty((num_samples * 2,), dtype=np.int16)
    stereo_data[0::2] = left_ch
    stereo_data[1::2] = right_ch
    
    with wave.open(str(output_wav), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(stereo_data.tobytes())
        
    return output_wav
