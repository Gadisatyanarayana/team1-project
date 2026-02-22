"""
Audio generation for text-to-speech
Supports multiple TTS engines with Ol Chiki transliteration
Returns (audio_bytes, content_type) so callers can set the correct HTTP header.
"""

import os
import math
import struct
import tempfile
from io import BytesIO
from .olchiki_tts import prepare_text_for_tts, is_olchiki_text

def generate_speech_audio(text, language='hi'):
    """Generate speech audio using available TTS engines.

    Args:
        text: Text to speak
        language: Language code ('hi' for Hindi, 'sat' for Santali)

    Returns:
        tuple: (audio_bytes, content_type_string) or (None, None) on failure
    """
    if not text or not text.strip():
        print("[TTS] Empty text — nothing to speak")
        return None, None

    # Transliterate Ol Chiki to phonetic Latin so gTTS/pyttsx3 can pronounce it
    if is_olchiki_text(text):
        print("[TTS] Ol Chiki detected — transliterating to phonetic text")
        tts_text = prepare_text_for_tts(text)
        print("[TTS] Will speak: {}".format(tts_text))
        language = 'hi'  # use Hindi engine for phonetic Santali
    else:
        tts_text = text

    print("[TTS] Generating speech for: {} (lang={})".format(tts_text[:40], language))

    # 1) gTTS — best quality, needs internet
    try:
        audio_data = _generate_with_gtts(tts_text, language)
        if audio_data:
            print("[TTS] gTTS OK — {} bytes (MP3)".format(len(audio_data)))
            return audio_data, 'audio/mpeg'
    except Exception as e:
        print("[TTS] gTTS failed: {}".format(e))

    # 2) pyttsx3 — offline fallback
    try:
        audio_data = _generate_with_pyttsx3(tts_text, language)
        if audio_data:
            print("[TTS] pyttsx3 OK — {} bytes (WAV)".format(len(audio_data)))
            return audio_data, 'audio/wav'
    except Exception as e:
        print("[TTS] pyttsx3 failed: {}".format(e))

    # 3) Pure-Python silent-tone WAV — always works, no dependencies
    print("[TTS] Using built-in tone fallback (WAV)")
    tone = generate_simple_tone()
    if tone:
        return tone, 'audio/wav'
    return None, None


def _generate_with_gtts(text, language='hi'):
    """Generate speech using Google Text-to-Speech (gTTS)
    
    Args:
        text: Text to speak
        language: Language code
        
    Returns:
        bytes: MP3 audio data
    """
    try:
        from gtts import gTTS
        
        # Map languages
        lang_map = {
            'hi': 'hi',  # Hindi
            'sat': 'hi',  # Santali falls back to Hindi
            'en': 'en',  # English
        }
        
        lang_code = lang_map.get(language, 'hi')
        
        # Generate speech
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        # Save to bytes
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        print(f"Generated gTTS audio ({language}): {len(audio_buffer.getvalue())} bytes")
        return audio_buffer.getvalue()
        
    except ImportError:
        raise Exception("gTTS not installed")
    except Exception as e:
        raise Exception(f"gTTS error: {str(e)}")


def _generate_with_pyttsx3(text, language='hi'):
    """Generate speech using pyttsx3
    
    Args:
        text: Text to speak
        language: Language code
        
    Returns:
        bytes: WAV audio data
    """
    try:
        import pyttsx3
        
        # Initialize engine
        engine = pyttsx3.init()
        
        # Configure voice properties
        engine.setProperty('rate', 150)  # Speed
        engine.setProperty('volume', 0.9)  # Volume
        
        # Try to set language
        try:
            voices = engine.getProperty('voices')
            for voice in voices:
                if language.lower() in voice.languages[0].lower():
                    engine.setProperty('voice', voice.id)
                    break
        except:
            pass  # Use default voice
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Save to file
            engine.save_to_file(text, tmp_path)
            engine.runAndWait()
            engine.stop()
            
            # Read audio file
            with open(tmp_path, 'rb') as f:
                audio_data = f.read()
            
            print(f"Generated pyttsx3 audio: {len(audio_data)} bytes")
            return audio_data
            
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass
                    
    except ImportError:
        raise Exception("pyttsx3 not installed")
    except Exception as e:
        raise Exception(f"pyttsx3 error: {str(e)}")


def generate_simple_tone():
    """Generate a simple 440 Hz beep tone using only the Python standard library.
    No numpy, no scipy — always available.
    Returns raw WAV bytes.
    """
    try:
        sample_rate = 22050
        duration    = 0.5      # seconds
        frequency   = 440      # Hz  (concert A)
        amplitude   = 0.25     # 0-1
        num_samples = int(sample_rate * duration)

        # Build 16-bit mono PCM samples
        samples = bytearray()
        for i in range(num_samples):
            val = int(amplitude * 32767 *
                      math.sin(2 * math.pi * frequency * i / sample_rate))
            # clamp to int16 range
            val = max(-32768, min(32767, val))
            samples += struct.pack('<h', val)

        data_size = len(samples)
        # Standard PCM WAV header (44 bytes)
        header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF',
            36 + data_size,   # overall file size - 8
            b'WAVE',
            b'fmt ',
            16,               # subchunk1 size
            1,                # PCM audio format
            1,                # mono
            sample_rate,
            sample_rate * 2,  # byte rate (1 channel * 2 bytes)
            2,                # block align
            16,               # bits per sample
            b'data',
            data_size
        )
        return bytes(header) + bytes(samples)
    except Exception as e:
        print("[TTS] Tone generation failed: {}".format(e))
        return None
