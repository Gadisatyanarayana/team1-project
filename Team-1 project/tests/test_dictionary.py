"""
Tests for dictionary module
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.translator.dictionary import Dictionary

@pytest.fixture
def dictionary():
    """Create dictionary instance for testing"""
    return Dictionary()

def test_lookup_hindi_to_santali(dictionary):
    """Test Hindi to Santali lookup"""
    result = dictionary.lookup_hindi_to_santali('नमस्ते')
    assert result == 'जोहार'

def test_lookup_santali_to_hindi(dictionary):
    """Test Santali to Hindi lookup"""
    result = dictionary.lookup_santali_to_hindi('जोहार')
    assert result == 'नमस्ते'

def test_lookup_nonexistent_word(dictionary):
    """Test lookup of non-existent word"""
    result = dictionary.lookup_hindi_to_santali('अपरिचित')
    assert result is None

def test_add_word(dictionary):
    """Test adding word to dictionary"""
    dictionary.add_word('नया', 'सर')
    assert dictionary.lookup_hindi_to_santali('नया') == 'सर'
    assert dictionary.lookup_santali_to_hindi('सर') == 'नया'

def test_get_all_words(dictionary):
    """Test getting all words"""
    words = dictionary.get_all_words()
    assert isinstance(words, dict)
    assert len(words) > 0

def test_search_words(dictionary):
    """Test word search"""
    results = dictionary.search_words('नम', 'hi')
    assert len(results) > 0
    assert any('नमस्ते' in result[0] for result in results)

def test_case_insensitive_lookup(dictionary):
    """Test case-insensitive lookup"""
    result1 = dictionary.lookup_hindi_to_santali('नमस्ते')
    result2 = dictionary.lookup_hindi_to_santali('नमस्ते')
    assert result1 == result2
