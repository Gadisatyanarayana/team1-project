"""
Text processing module for language preprocessing
"""

import re
from typing import List

class TextProcessor:
    """Handle text preprocessing and cleaning (simplified version without NLTK)"""
    
    def __init__(self):
        """Initialize text processor"""
        self.patterns = {
            'extra_spaces': r'\s+',
            'special_chars': r'[^\w\s\u0900-\u097F\u1C65-\u1C88।॥]',  # Hindi and Santali Unicode ranges
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(self.patterns['extra_spaces'], ' ', text)
        # Strip leading and trailing whitespace
        text = text.strip()
        return text
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """Tokenize text into sentences"""
        # Simple split by sentence markers
        sentences = re.split(r'[।॥\.!\?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def tokenize_words(self, text: str) -> List[str]:
        """Tokenize text into words"""
        # Simple split by whitespace
        tokens = text.split()
        return tokens
    
    def remove_special_chars(self, text: str, keep_unicode: bool = True) -> str:
        """Remove special characters"""
        if keep_unicode:
            # Keep Hindi and Santali characters
            text = re.sub(r'[^\w\s\u0900-\u097F\u1C65-\u1C88।॥.,!?\-]', '', text)
        else:
            text = re.sub(r'[^\w\s.,!?\-]', '', text)
        return text
    
    def normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace"""
        return re.sub(self.patterns['extra_spaces'], ' ', text).strip()
    
    def preprocess(self, text: str) -> str:
        """Complete preprocessing pipeline"""
        text = self.clean_text(text)
        text = self.normalize_whitespace(text)
        return text
