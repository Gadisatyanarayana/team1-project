"""
Ol Chiki character pronunciation and transliteration for TTS
"""

# Ol Chiki to phonetic spelling for text-to-speech
OLCHIKI_PHONETIC_MAP = {
    # Vowels
    'ᱚ': 'oh',
    'ᱟ': 'ah',
    'ᱤ': 'ee',
    'ᱦ': 'ha',
    'ᱩ': 'oo',
    'ᱮ': 'ay',
    'ᱰ': 'da',
    'ᱳ': 'o',
    
    # Consonants
    'ᱠ': 'ka',
    'ᱜ': 'ga',
    'ᱝ': 'nga',
    'ᱞ': 'la',
    'ᱢ': 'ma',
    'ᱣ': 'wa',
    'ᱤ': 'ya',
    'ᱨ': 'ra',
    'ᱪ': 'cha',
    'ᱫ': 'da',
    'ᱬ': 'dha',
    'ᱭ': 'ya',
    'ᱱ': 'na',
    'ᱥ': 'sa',
    'ᱧ': 'nya',
    'ᱨ': 'ra',
    'ᱲ': 'rra',
    'ᱳ': 'o',
    'ᱴ': 'ta',
    'ᱵ': 'ba',
    'ᱶ': 'va',
    'ᱷ': 'ha',
    'ᱸ': 'um',
    'ᱹ': 'anusvara',
    'ᱺ': 'visarga',
}

# Ol Chiki to Latin/Devanagari transliteration
OLCHIKI_TO_LATIN = {
    'ᱚ': 'a', 'ᱟ': 'ā', 'ᱤ': 'i', 'ᱦ': 'h', 'ᱩ': 'u', 'ᱮ': 'ē', 'ᱰ': 'd', 'ᱳ': 'o',
    'ᱠ': 'k', 'ᱜ': 'g', 'ᱝ': 'ṅ', 'ᱞ': 'l', 'ᱢ': 'm', 'ᱣ': 'w', 'ᱤ': 'y', 'ᱨ': 'r',
    'ᱪ': 'c', 'ᱫ': 'd', 'ᱬ': 'ḍh', 'ᱭ': 'y', 'ᱱ': 'n', 'ᱥ': 's', 'ᱧ': 'ñ', 'ᱲ': 'ṛ',
    'ᱳ': 'o', 'ᱴ': 't', 'ᱵ': 'b', 'ᱶ': 'v', 'ᱷ': 'h', 'ᱸ': 'm̐', 'ᱹ': '̃', 'ᱺ': 'h',
    '᱐': '0', '᱑': '1', '᱒': '2', '᱓': '3', '᱔': '4', '᱕': '5', '᱖': '6', '᱗': '7', '᱘': '8', '᱙': '9',
}

def transliterate_olchiki(text):
    """Convert Ol Chiki to readable phonetic pronunciation"""
    result = []
    for char in text:
        if char in OLCHIKI_PHONETIC_MAP:
            result.append(OLCHIKI_PHONETIC_MAP[char])
        elif char == ' ':
            result.append(' ')  # Keep spaces as spaces
        elif char == '।':
            result.append('')  # Silent pause marker
        else:
            result.append(char)
    return ''.join(result)

def create_tts_text_for_olchiki(text):
    """Create a phonetic version for TTS engine"""
    # Transliterate to phonetic pronunciation
    return transliterate_olchiki(text)

def is_olchiki_text(text):
    """Check if text contains Ol Chiki characters"""
    olchiki_range = range(0x1C50, 0x1C89)  # Ol Chiki Unicode range
    return any(ord(c) in olchiki_range for c in text)

def prepare_text_for_tts(text):
    """Prepare text for Text-to-Speech engine"""
    if is_olchiki_text(text):
        # For Ol Chiki, transliterate and spell out
        phonetic = create_tts_text_for_olchiki(text)
        return phonetic
    return text
