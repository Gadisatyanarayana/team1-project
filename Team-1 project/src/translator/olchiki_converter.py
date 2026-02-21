"""
Devanagari to Ol Chiki Script Converter
Based on: https://github.com/Prasanta-Hembram/Devanagari-to-Ol-Chiki-Script-Converter-tool
License: CC0 1.0 Universal (Public Domain)
"""

class OlChikiConverter:
    """Converts Devanagari script to Ol Chiki script for Santali language"""
    
    # Devanagari to Ol Chiki character mappings
    SUBSTITUTIONS = {
        # Special phrases (longest patterns first)
        "उदुगोक् आ": "ᱩᱫᱩᱜᱚᱜᱼᱟ",
        "आ़च् किर": "ᱟᱹᱛᱠᱤᱨ",
        "मेसाक् आ": "ᱢᱮᱥᱟᱜᱼᱟ",
        "ओनोल": "ᱚᱱᱚᱞ",
        "चेदाक्": "ᱪᱮᱫᱟᱜ",
        "ओल": "ᱚᱞ",
        "रिच्": "ᱨᱤᱡ",
        "उचा": "ᱩᱪᱟᱹ",
        "ड़ोक्": "ᱲᱚᱜ",
        "नाक्": "ᱱᱟᱜ",
        "इप": "ᱭᱤᱯ",
        "ड़ो": "ᱲᱚ",
        "ड़ि": "ᱲᱤ",
        "नुक्": "ᱱᱩᱜ",
        "झा़": "ᱡᱷᱟᱹ",
        "बा़": "ᱵᱟᱹ",
        "विं": "ᱣᱤᱱ",
        "ाक्": "ᱟᱜ",
        "ोक्": "ᱚᱜ",
        
        # Vowels with diacritics
        "ऀ": "ऀ",
        "ँ": "ᱸ",
        "ं": "ᱸ",
        "ः": "ᱷ",
        "ऄ": "ऄ",
        "आ़": "ᱟᱹ",
        "अ": "ᱚ",
        "आ": "ᱟ",
        "इ": "ᱤ",
        "ई": "ᱤᱻ",
        "उ": "ᱩ",
        "ऊ": "ᱩᱻ",
        "ऋ": "ᱨᱩ",
        "ऌ": "ᱞᱩ",
        "ऍ": "ᱚᱹ",
        "ऎ": "ᱮᱹ",
        "ए": "ᱮ",
        "ऐ": "ᱚᱤ",
        "ऑ": "ᱟᱹ",
        "ऒ": "ᱳ",
        "ओ": "ᱳ",
        "औ": "ᱚᱣ",
        
        # Consonants
        "क्": "ᱠ",
        "क": "ᱠ",
        "ख": "ᱠᱷ",
        "ग": "ᱜ",
        "घ": "ᱜᱷ",
        "ङ": "ᱝ",
        "च्": "ᱡ",
        "च": "ᱪ",
        "छ": "ᱪᱷ",
        "ज": "ᱡ",
        "झ": "ᱡᱷ",
        "ञ": "ᱧ",
        "ट": "ᱴ",
        "ठ": "ᱴᱷ",
        "ड": "ᱰ",
        "ढ": "ᱰᱷ",
        "ण": "ᱬ",
        "त्": "ᱫ",
        "त": "ᱛ",
        "थ": "ᱛᱷ",
        "द": "ᱫ",
        "ध": "ᱫᱷ",
        "न": "ᱱ",
        "ऩ": "ᱱ",
        "प": "ᱯ",
        "फ": "ᱯᱷ",
        "ब": "ᱵ",
        "भ": "ᱵᱷ",
        "म": "ᱢ",
        "य": "ᱭ",
        "र": "ᱨ",
        "ऱ": "ᱨ",
        "ल": "ᱞ",
        "ळ": "ᱞ",
        "ऴ": "ᱞ",
        "व": "ᱣ",
        "श": "ᱥ",
        "ष": "ᱥ",
        "स": "ᱥ",
        "ह": "ᱦ",
        "ऺ": "",
        "ला़": "ᱞᱟᱹ",
        "ऻ": "ᱟ",
        
        # Vowel signs
        "ा़": "ᱟᱹ",
        "ा": "ᱟ",
        "ि": "ᱤ",
        "ी": "ᱤ",
        "ु": "ᱩ",
        "ू": "ᱩ",
        "ृ": "ᱨᱩ",
        "ॄ": "ᱨᱩ",
        "ॅ": "ᱟᱸ",
        "ॆ": "ᱮ",
        "े": "ᱮ",
        "ै": "ᱮᱭ",
        "ॉ": "ᱟᱸ",
        "ॊ": "ᱚ",
        "ो": "ᱚ",
        "ौ": "ᱚᱣ",
        "्": "",
        "ॎ": "ᱮ",
        "ॏ": "ॏ",
        "ॐ": "ᱳᱸ",
        "॑": "↑",
        "॒": "↓",
        "॓": "॓",
        "॔": "॔",
        "ॕ": "ᱚᱸ",
        "ॖ": "ᱩ",
        "ॗ": "ᱩ",
        
        # Nukta variants
        "क़": "ᱠᱚ",
        "ख़": "ᱠᱷᱚ",
        "ग़": "ᱜ",
        "ज़": "ᱡ",
        "ड़": "ᱲ",
        "ढ़": "ᱰᱷ",
        "फ़": "ᱯ",
        "य़": "ᱭ",
        
        # Additional characters
        "ॠ": "ᱨᱩ",
        "ॡ": "ᱞᱩ",
        "ॢ": "ᱞᱩ",
        "ॣ": "ᱞᱩ",
        
        # Punctuation
        "।": "᱾",
        "॥": "᱿",
        ".": "᱾",
        
        # Numbers
        "०": "᱐",
        "१": "᱑",
        "२": "᱒",
        "३": "᱓",
        "४": "᱔",
        "५": "᱕",
        "६": "᱖",
        "७": "᱗",
        "८": "᱘",
        "९": "᱙",
        
        # Other
        "॰": "॰",
        "ॱ": "ॱ",
        "ॲ": "ᱚᱹ",
        "ॳ": "ᱚ",
        "ॴ": "ᱟ",
        "ॵ": "ᱚᱣ",
        "ॶ": "ᱩ",
        "ॷ": "ᱩ",
    }
    
    @classmethod
    def convert(cls, devanagari_text):
        """
        Convert Devanagari text to Ol Chiki script
        
        Args:
            devanagari_text (str): Text in Devanagari script
            
        Returns:
            str: Text converted to Ol Chiki script
        """
        if not devanagari_text:
            return ""
        
        result = devanagari_text
        
        # Sort substitutions by length (longest first) to handle multi-character patterns
        sorted_subs = sorted(cls.SUBSTITUTIONS.items(), key=lambda x: len(x[0]), reverse=True)
        
        # Apply substitutions
        for devanagari, olchiki in sorted_subs:
            result = result.replace(devanagari, olchiki)
        
        return result
    
    @classmethod
    def is_devanagari(cls, text):
        """
        Check if text contains Devanagari characters
        
        Args:
            text (str): Text to check
            
        Returns:
            bool: True if text contains Devanagari characters
        """
        if not text:
            return False
        
        # Devanagari Unicode range: U+0900 to U+097F
        for char in text:
            if '\u0900' <= char <= '\u097F':
                return True
        return False
