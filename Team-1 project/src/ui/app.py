"""
Production-Ready Flask API for Hindi-Santali Translator
Modern API with React frontend support
"""

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from translator.engine import TranslationEngine

def create_app(config=None):
    """Create and configure Flask application"""
    # Use absolute paths so templates & static files resolve correctly both
    # locally and on Vercel's serverless filesystem.
    _here = os.path.dirname(os.path.abspath(__file__))
    app = Flask(__name__,
                template_folder=os.path.join(_here, 'templates'),
                static_folder=None)   # no separate static dir; everything inline
    
    CORS(app)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    if config:
        app.config.update(config)
    
    # Initialize translator (includes dictionary)
    translator = TranslationEngine()
    
    # ============ STATIC PAGES ============
    
    @app.route('/')
    def index():
        """Serve main React app"""
        return render_template('index.html')
    
    @app.route('/test')
    def test():
        """Quick test page"""
        result = translator.translate("नमस्ते", 'hi', 'sat')
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Test</title><style>body{{font-family:Arial;padding:20px}}</style></head>
        <body>
            <h1>Translation Test</h1>
            <p><strong>Input:</strong> नमस्ते</p>
            <p><strong>Output:</strong> {result.get('translated_text')}</p>
            <p><strong>Status:</strong> {'✓ Success' if result.get('success') else '✗ Failed'}</p>
        </body>
        </html>
        """
    
    # ============ TRANSLATION API ============
    
    @app.route('/api/translate', methods=['POST'])
    def translate():
        """Translate text (Hindi ↔ Santali)"""
        try:
            data = request.get_json()
            text = data.get('text', '').strip()
            source_lang = str(data.get('source_lang', 'hi')).strip().lower()
            target_lang = str(data.get('target_lang', 'sat')).strip().lower()
            
            if not text:
                return jsonify({'success': False, 'error': 'Empty text'}), 400
            
            result = translator.translate(text, source_lang, target_lang)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/batch-translate', methods=['POST'])
    def batch_translate():
        """Translate multiple texts"""
        try:
            data = request.get_json()
            texts = data.get('texts', [])
            source_lang = data.get('source_lang', 'hi')
            target_lang = data.get('target_lang', 'sat')
            
            if not texts:
                return jsonify({'error': 'No texts provided'}), 400
            
            results = []
            for text in texts:
                result = translator.translate(text, source_lang, target_lang)
                results.append(result)
            
            return jsonify({'success': True, 'count': len(results), 'results': results})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ============ DICTIONARY API ============
    
    @app.route('/api/dictionary/search', methods=['GET'])
    def search_dictionary():
        """Search dictionary"""
        try:
            q = request.args.get('q', '').strip()
            lang = request.args.get('lang', 'hi')
            
            if not q:
                return jsonify({'error': 'Empty query'}), 400
            
            results = translator.dictionary.search_words(q, lang)
            return jsonify({'query': q, 'results': results, 'count': len(results)})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/dictionary/lookup/<word>', methods=['GET'])
    def lookup_word(word):
        """Look up a single word"""
        try:
            result = translator.dictionary.lookup_hindi_to_santali(word)
            if result:
                return jsonify({'success': True, 'hindi': word, 'santali': result})
            return jsonify({'success': False, 'error': 'Word not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ============ SPEECH-TO-TEXT (TRANSCRIBE) API ============

    @app.route('/api/transcribe', methods=['POST'])
    def transcribe():
        """Transcribe uploaded WAV audio to Hindi text using SpeechRecognition."""
        try:
            import speech_recognition as sr

            audio_file = request.files.get('audio')
            if not audio_file:
                return jsonify({'success': False, 'error': 'No audio file uploaded'}), 400

            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 300
            recognizer.dynamic_energy_threshold = True

            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)

            # Try Google Web Speech HTTP API (different endpoint from Chrome's — often works when Chrome fails)
            try:
                text = recognizer.recognize_google(audio_data, language='hi-IN')
                return jsonify({'success': True, 'text': text, 'engine': 'google'})
            except sr.UnknownValueError:
                return jsonify({'success': False, 'error': 'Could not understand the audio. Please speak clearly in Hindi.'})
            except sr.RequestError as e:
                return jsonify({'success': False, 'error': 'Speech service unavailable: ' + str(e)})

        except ImportError:
            return jsonify({'success': False, 'error': 'SpeechRecognition not installed. Run: pip install SpeechRecognition'}), 500
        except Exception as e:
            import traceback
            print('[/api/transcribe] Exception:', traceback.format_exc())
            return jsonify({'success': False, 'error': str(e)}), 500

    # ============ TEXT-TO-SPEECH API ============
    
    @app.route('/api/speak', methods=['POST'])
    def speak():
        """Generate audio for text (Text-to-Speech).
        Returns MP3 (gTTS) or WAV (pyttsx3 / fallback tone) with correct Content-Type.
        """
        try:
            from translator.audio_gen import generate_speech_audio

            data = request.get_json(force=True, silent=True) or {}
            text = data.get('text', '').strip()
            language = str(data.get('language', 'hi')).strip().lower()

            if not text:
                return jsonify({'error': 'Empty text provided'}), 400

            # generate_speech_audio now returns (bytes, content_type)
            audio_data, content_type = generate_speech_audio(text, language)

            if not audio_data:
                return jsonify({'error': 'All TTS engines failed — check server logs'}), 500

            return Response(
                audio_data,
                mimetype=content_type,
                headers={
                    'Content-Length': str(len(audio_data)),
                    'Cache-Control': 'no-cache'
                }
            )
        except Exception as e:
            import traceback
            print("[/api/speak] Exception:", traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    # ============ STATS & INFO ============
    
    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        """Get translator statistics"""
        try:
            stats = {
                'total_rows_loaded': getattr(translator.dictionary, 'total_rows_loaded', 0),
                'unique_pairs': len(translator.dictionary.hindi_to_santali),
                'cache_size': len(translator.translation_cache),
                'dataset_path': getattr(translator.dictionary, 'dictionary_path', ''),
                'languages': ['Hindi', 'Santali']
            }
            return jsonify({'success': True, 'stats': stats})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ============ ERROR HANDLERS ============
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=5000)
