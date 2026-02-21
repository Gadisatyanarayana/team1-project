"""
Tests for translation engine
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.translator.engine import TranslationEngine

@pytest.fixture
def translator():
    """Create translator instance for testing"""
    return TranslationEngine()

def test_translate_hindi_to_santali(translator):
    """Test Hindi to Santali translation"""
    result = translator.translate('नमस्ते', 'hi', 'sat')
    assert result['success'] == True
    assert result['source_language'] == 'Hindi'
    assert result['target_language'] == 'Santali'

def test_translate_empty_text(translator):
    """Test translation with empty text"""
    result = translator.translate('', 'hi', 'sat')
    assert result['success'] == False
    assert 'Empty input text' in result['error']

def test_invalid_language_pair(translator):
    """Test invalid language pair"""
    result = translator.translate('hello', 'en', 'fr')
    assert result['success'] == False
    assert 'Unsupported language pair' in result['error']

def test_supported_languages(translator):
    """Test supported languages"""
    languages = translator.get_supported_languages()
    assert 'hi' in languages
    assert 'sat' in languages
    assert languages['hi'] == 'Hindi'
    assert languages['sat'] == 'Santali'

def test_batch_translate(translator):
    """Test batch translation"""
    texts = ['नमस्ते', 'धन्यवाद']
    results = translator.batch_translate(texts, 'hi', 'sat')
    assert len(results) == 2
    assert all(r['success'] for r in results)

def test_cache(translator):
    """Test translation caching"""
    text = 'नमस्ते'
    result1 = translator.translate(text, 'hi', 'sat')
    result2 = translator.translate(text, 'hi', 'sat')
    assert result1 == result2
    assert len(translator.translation_cache) > 0

def test_clear_cache(translator):
    """Test cache clearing"""
    translator.translate('नमस्ते', 'hi', 'sat')
    assert len(translator.translation_cache) > 0
    translator.clear_cache()
    assert len(translator.translation_cache) == 0
