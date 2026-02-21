"""
Test script to verify translations are working correctly
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.translator.engine import TranslationEngine

def test_translations():
    """Test various Hindi phrases"""
    print("=" * 60)
    print("HINDI TO SANTALI TRANSLATION TEST")
    print("=" * 60)
    
    # Initialize translator
    translator = TranslationEngine()
    
    # Test cases
    test_phrases = [
        "नमस्ते",
        "मुझे",
        "क्या",
        "मुझे क्या",
        "धन्यवाद",
        "आप कैसे हैं",
        "मेरा नाम राम है",
        "अच्छा",
    ]
    
    for phrase in test_phrases:
        print(f"\n{'─' * 60}")
        print(f"Hindi Input: {phrase}")
        result = translator.translate(phrase, 'hi', 'sat')
        
        if result['success']:
            print(f"Santali Output: {result['translated_text']}")
            print(f"Confidence: {result['confidence']}%")
            print(f"Matched: {result['matched_words']}/{result['total_words']} words")
            
            if result.get('word_mappings'):
                print("\nWord-by-word mapping:")
                for mapping in result['word_mappings']:
                    hindi = mapping.get('hindi', '')
                    santali = mapping.get('santali', '')
                    source = mapping.get('source', '')
                    conf = mapping.get('confidence', 0)
                    print(f"  {hindi} → {santali} ({source}, {conf})")
        else:
            print(f"ERROR: {result.get('error')}")
    
    print(f"\n{'=' * 60}")
    print("Dictionary Stats:")
    stats = translator.dictionary.get_stats()
    print(f"Total word pairs loaded: {stats['total_rows_loaded']}")
    print(f"Unique pairs: {stats['unique_pairs']}")
    print("=" * 60)

if __name__ == '__main__':
    test_translations()
