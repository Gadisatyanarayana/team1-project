"""
Dictionary management module for Hindi-Santali translations
Optimized for speed and accuracy
"""

import csv
import os
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
import unicodedata

class Dictionary:
    """Manage Hindi-Santali dictionary with optimized lookups"""
    
    def __init__(self, dictionary_path='data/dictionary.csv'):
        """Initialize dictionary
        
        Args:
            dictionary_path: Path to dictionary CSV file
        """
        self.dictionary_path = dictionary_path
        self.hindi_to_santali = {}
        self.santali_to_hindi = {}
        self.hindi_lower = {}  # Lowercase mapping for faster lookups
        self.prefix_index = {}  # Index for prefix matching
        self.total_rows_loaded = 0
        self.load_dictionary()
    
    def _normalize_text(self, text):
        """Normalize text for better matching"""
        if not text:
            return ''
        # Unicode NFC normalization (important for Devanagari composed vs decomposed forms)
        text = unicodedata.normalize('NFC', text)
        # Remove extra whitespace
        text = ' '.join(text.strip().split())
        return text
    
    def _is_valid_santali(self, text: str) -> bool:
        """Return False for garbled/corrupted Santali entries.

        Garbage entries (produced by broken transliteration of proper nouns)
        look like: "ᱞᱧ ᱞᱞ ᱢ ᱳ ᱱᱞ ᱠᱳ ᱢ ᱰᱨᱠᱪᱢ ᱣ ᱯ"
        — many space-separated single Ol Chiki characters.

        Good entries look like: "ᱟᱜᱡᱪᱷᱛᱩ ᱤᱱ ᱾" or "ᱡᱚᱦᱟᱨ"
        """
        if not text:
            return False
        # Any ASCII a-z / A-Z in a Santali translation = definitely garbage
        for ch in text:
            if ch.isascii() and ch.isalpha():
                return False
        tokens = text.split()
        if len(tokens) > 4:
            single_char = sum(1 for t in tokens if len(t) == 1)
            # If more than half the tokens are isolated single characters → garbled
            if single_char / len(tokens) > 0.50:
                return False
        return True

    def load_dictionary(self):
        """Load dictionary from CSV file with optimization"""
        if os.path.exists(self.dictionary_path):
            try:
                with open(self.dictionary_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    total_loaded = 0
                    duplicates_skipped = 0
                    
                    for row in reader:
                        # Handle different column names
                        hindi = row.get('hindi', row.get('Hindi', '')).strip() if row.get('hindi') or row.get('Hindi') else ''
                        santali = row.get('santali_olchiki', row.get('santali', row.get('Santali', ''))).strip() if row.get('santali_olchiki') or row.get('santali') or row.get('Santali') else ''
                        
                        if hindi and santali:
                            # Skip rows that are duplicate header entries
                            if hindi.lower() in ('hindi', 'h') or santali.lower() in ('santali', 's'):
                                continue
                            # Skip single-character Devanagari entries — they belong
                            # only in the letter-level transliteration map, NOT as word
                            # lookups (they corrupt multi-word lookups: एक→long junk, नदी→spaced)
                            if len(hindi) == 1:
                                continue
                            # Skip garbled/corrupted Santali values
                            if not self._is_valid_santali(santali):
                                continue
                            # Normalize
                            hindi = self._normalize_text(hindi)
                            santali = self._normalize_text(santali)
                            
                            # Skip duplicates
                            if hindi in self.hindi_to_santali:
                                duplicates_skipped += 1
                                continue
                            
                            # Store with original case (primary lookup)
                            self.hindi_to_santali[hindi] = santali
                            self.santali_to_hindi[santali] = hindi
                            total_loaded += 1
                            
                            # Build lowercase index for case-insensitive matching
                            hindi_lower = hindi.lower()
                            self.hindi_lower[hindi_lower] = hindi
                            
                            # Build prefix index for faster prefix matching
                            for i in range(1, len(hindi) + 1):
                                prefix = hindi[:i]
                                if prefix not in self.prefix_index:
                                    self.prefix_index[prefix] = []
                                if hindi not in self.prefix_index[prefix]:
                                    self.prefix_index[prefix].append(hindi)
                
                self.total_rows_loaded = total_loaded
            except Exception as e:
                print("[WARN] Error loading dictionary: {}".format(repr(e)))
                self._initialize_basic_dictionary()
                return
            # Print success outside try/except so a print encoding error
            # does NOT trigger the except clause and wipe the loaded data.
            try:
                print("[OK] Loaded {} Hindi-Santali pairs ({} duplicates skipped)".format(
                    total_loaded, duplicates_skipped))
            except Exception:
                print("[OK] Loaded {} pairs".format(total_loaded))
        else:
            print("[WARN] Dictionary file not found at {}".format(self.dictionary_path))
            self._initialize_basic_dictionary()
    
    
    def _initialize_basic_dictionary(self):
        """Initialize with basic Hindi-Santali word mappings"""
        basic_words = {
            'नमस्ते': 'जोहार',
            'धन्यवाद': 'सोनोज़',
            'हाँ': 'एले',
            'नहीं': 'माहा',
            'पानी': 'तुरु',
            'खाना': 'होपोर्',
            'दिन': 'अदिल',
            'रात': 'राति',
            'सूरज': 'सूर्य',
            'चाँद': 'चंद्र',
            'आँख': 'मेंदा',
            'कान': 'कुलु',
            'नाक': 'नाटा',
            'दांत': 'दाँत',
            'हाथ': 'सेल',
            'पैर': 'होरो',
            'सिर': 'जोहोल',
            'हृदय': 'हिया',
            'रक्त': 'कु',
            'घर': 'ओडि',
            'गली': 'पथा',
            'मार्ग': 'पथा',
            'विद्यालय': 'स्कूल',
            'पुस्तक': 'किताब',
            'कलम': 'लिख',
            'कागज': 'कागद',
            'शिक्षक': 'सिक्षक',
            'विद्यार्थी': 'छात्र',
            'हेलो': 'हेलो',
            'नमस्ते': 'जोहार',
            'अलविदा': 'अलविदा',
            'प्रणाम': 'जोहार',
            'आपका स्वागत है': 'जोहार',
            'कैसे हो': 'की कोडा',
            'ठीक हूँ': 'अक्छे छिहै',
            'क्या नाम है': 'ने नाय की छिहै',
            'मेरा नाम': 'अम् नाय',
            'कृपया': 'माइ',
            'मदद': 'दीरी',
            'पसंद': 'दिसाग',
            'प्रेम': 'लेबे',
            'दोस्त': 'दोस्त',
            'परिवार': 'हातेम',
            'माता': 'अय',
            'पिता': 'अप',
            'भाई': 'आयत',
            'बहन': 'तांग',
            'बेटा': 'पोरो',
            'बेटी': 'पोरोय',
            'पत्नी': 'पेंत',
            'पति': 'अवोर',
            'बुजुर्ग': 'बोड़ो',
            'बच्चा': 'छोटो',
            'छोटा': 'हेड़ो',
            'बड़ा': 'बाड़ो',
            'अच्छा': 'अक्छे',
            'बुरा': 'बेड़ो',
            'सुंदर': 'रंगा',
            'काला': 'कारा',
            'सफेद': 'पेत',
            'लाल': 'लाल',
            'हरा': 'हरे',
            'नीला': 'नील',
            'पीला': 'पीला',
            'गर्म': 'तपा',
            'ठंडा': 'सीता',
            'गीला': 'भेड़ो',
            'सूखा': 'सूका',
            'तेज': 'तिज',
            'धीमा': 'मीना',
            'मीठा': 'मीठो',
            'कड़वा': 'कड़वो',
            'नमकीन': 'खारो',
            'खट्टा': 'खारो',
        }
        self.hindi_to_santali = basic_words
        self.santali_to_hindi = {v: k for k, v in basic_words.items()}
    
    def lookup_hindi_to_santali(self, hindi_word: str) -> Optional[str]:
        """Look up Hindi word in dictionary - optimized for speed"""
        if not hindi_word:
            return None
        
        word_clean = self._normalize_text(hindi_word)
        
        # First: exact match with original case (fastest)
        if word_clean in self.hindi_to_santali:
            return self.hindi_to_santali[word_clean]
        
        # Second: lowercase match
        word_lower = word_clean.lower()
        if word_lower in self.hindi_lower:
            original = self.hindi_lower[word_lower]
            if original in self.hindi_to_santali:
                return self.hindi_to_santali[original]
        
        # Third: try NFD-normalized then NFC form (handles decomposed Devanagari input)
        import unicodedata as _ud
        word_nfd = _ud.normalize('NFD', hindi_word).strip()
        if word_nfd in self.hindi_to_santali:
            return self.hindi_to_santali[word_nfd]
        
        return None

    def lookup_santali_to_hindi(self, santali_word: str) -> Optional[str]:
        """Look up Santali word in dictionary"""
        if not santali_word:
            return None
        word_clean = self._normalize_text(santali_word)
        return self.santali_to_hindi.get(word_clean)

    def add_word(self, hindi: str, santali: str) -> None:
        """Add word pair to dictionary"""
        hindi = self._normalize_text(hindi)
        santali = self._normalize_text(santali)
        self.hindi_to_santali[hindi] = santali
        self.hindi_lower[hindi.lower()] = hindi
        self.santali_to_hindi[santali] = hindi

    def get_all_words(self) -> Dict[str, str]:
        """Get all Hindi-Santali word pairs"""
        return self.hindi_to_santali.copy()

    def save_dictionary(self) -> None:
        """Save dictionary to CSV file"""
        try:
            os.makedirs(os.path.dirname(self.dictionary_path), exist_ok=True)
            with open(self.dictionary_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['hindi', 'santali'])
                for hindi, santali in self.hindi_to_santali.items():
                    if not hindi.islower() or hindi not in [h.lower() for h in self.hindi_to_santali.keys()]:
                        writer.writerow([hindi, santali])
        except Exception as e:
            print("Error saving dictionary: {}".format(str(e)))

    def search_words(self, query: str, source_lang: str = 'hi') -> List[Tuple[str, str]]:
        """Search for words matching query - optimized"""
        results: List[Tuple[str, str]] = []
        query_lower = query.lower().strip()
        
        if not query_lower:
            return results
        
        if source_lang == 'hi':
            # Search in Hindi words
            for hindi in self.hindi_to_santali.keys():
                if hindi.islower() and hindi != hindi.lower():
                    continue  # Skip lowercase duplicates
                if query_lower in hindi.lower():
                    santali = self.hindi_to_santali[hindi]
                    results.append((hindi, santali))
        else:
            # Search in Santali words
            for santali in self.santali_to_hindi.keys():
                if query_lower in santali.lower():
                    hindi = self.santali_to_hindi[santali]
                    results.append((hindi, santali))
        
        return results[:20]  # Limit to top 20 results for speed

    def fuzzy_match_hindi_to_santali(self, hindi_word: str, threshold: float = 0.7) -> Optional[Tuple[str, float]]:
        """Find fuzzy match for Hindi word - optimized with threshold"""
        hindi_word_clean = self._normalize_text(hindi_word)
        hindi_word_lower = hindi_word_clean.lower()
        best_match: Optional[Tuple[str, float]] = None
        best_score = threshold
        
        for dictionary_word, santali_word in self.hindi_to_santali.items():
            # Try exact match first (should have been caught earlier, but double-check)
            if hindi_word_lower == dictionary_word.lower():
                return (santali_word, 1.0)
            
            # Calculate similarity
            similarity = SequenceMatcher(None, hindi_word_lower, dictionary_word.lower()).ratio()
            if similarity > best_score:
                best_score = similarity
                best_match = (santali_word, similarity)
        
        return best_match

    def fuzzy_match_santali_to_hindi(self, santali_word: str, threshold: float = 0.7) -> Optional[Tuple[str, float]]:
        """Find fuzzy match for Santali word using sequence matching"""
        santali_word_lower = santali_word.lower()
        best_match: Optional[Tuple[str, float]] = None
        best_score = threshold
        for dictionary_santali, hindi_word in self.santali_to_hindi.items():
            similarity = SequenceMatcher(None, santali_word_lower, dictionary_santali.lower()).ratio()
            if similarity > best_score:
                best_score = similarity
                best_match = (hindi_word, similarity)
        return best_match

    def get_stats(self) -> Dict[str, int]:
        """Get dictionary statistics"""
        return {
            'unique_pairs': len(self.hindi_to_santali),
            'total_rows_loaded': getattr(self, 'total_rows_loaded', 0),
        }

