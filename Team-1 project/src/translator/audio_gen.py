"""
Audio generation for text-to-speech
Supports multiple TTS engines with Ol Chiki transliteration
"""

import os
import tempfile
from io import BytesIO
from .olchiki_tts import prepare_text_for_tts, is_olchiki_text

def generate_speech_audio(text, language='hi'):
    """Generate speech audio using available TTS engines
    
    Args:
        text: Text to speak
        language: Language code ('hi' for Hindi, 'sat' for Santali)
    
    Returns:
        bytes: Audio data in MP3 or WAV format
    """
    if not text or not text.strip():
        print("⚠ Empty text provided for TTS")
        return None
    
    # Prepare text for TTS (transliterate Ol Chiki if needed)
    if is_olchiki_text(text):
        print(f"🔤 Ol Chiki text detected, transliterating for TTS...")
        tts_text = prepare_text_for_tts(text)
        print(f"📝 TTS will speak: {tts_text}")
    else:
        tts_text = text
    
    print(f"🎤 Generating speech for: {text[:30]}... (lang={language})")
    
    # Try gTTS (Google Text-to-Speech) first - works best
    try:
        audio_data = _generate_with_gtts(tts_text, language)
        if audio_data:
            print(f"✓ gTTS generated {len(audio_data)} bytes of audio")
            return audio_data
    except Exception as e:
        print(f"⚠ gTTS failed: {e}")
    
    # Fallback to pyttsx3
    try:
        audio_data = _generate_with_pyttsx3(tts_text, language)
        if audio_data:
            print(f"✓ pyttsx3 generated {len(audio_data)} bytes of audio")
            return audio_data
    except Exception as e:
        print(f"⚠ pyttsx3 failed: {e}")
    
    # Last resort - return simple tone to at least give feedback
    print("⚠ Falling back to simple tone generator")
    return generate_simple_tone()


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
    """Generate a simple beep tone for testing"""
    try:
        import numpy as np
        from scipy.io import wavfile
        import tempfile
        
        # Generate beep
        sample_rate = 22050
        duration = 0.5  # seconds
        frequency = 1000  # Hz
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        wave = np.sin(2 * np.pi * frequency * t) * 0.3  # Sine wave
        
        # Convert to 16-bit PCM
        audio_data = np.int16(wave * 32767)
        
        # Save to BytesIO
        output = BytesIO()
        wavfile.write(output, sample_rate, audio_data)
        output.seek(0)
        
        return output.read()
    
    except Exception as e:
        print(f"Error generating tone: {e}")
        return None
