"""
Translation engine for Hindi to Santali translation
"""

from typing import Dict, Optional
from .dictionary import Dictionary
from .processor import TextProcessor
import json

# Hindi to Ol Chiki letter mapping for fallback transliteration
HINDI_OLCHIKI_MAP = {
    'अ': 'ᱚ', 'आ': 'ᱟ', 'इ': 'ᱤ', 'ई': 'ᱤ', 'उ': 'ᱩ', 'ऊ': 'ᱩ',
    'ए': 'ᱮ', 'ऐ': 'ᱮ', 'ओ': 'ᱳ', 'औ': 'ᱳ', 'ऋ': 'ᱨᱤ',
    'क': 'ᱠ', 'ख': 'ᱠ', 'ग': 'ᱜ', 'घ': 'ᱜ', 'ङ': 'ᱝ',
    'च': 'ᱪ', 'छ': 'ᱪ', 'ज': 'ᱡ', 'झ': 'ᱡ', 'ञ': 'ᱧ',
    'ट': 'ᱴ', 'ठ': 'ᱴ', 'ड': 'ᱫ', 'ढ': 'ᱫ', 'ण': 'ᱱ',
    'त': 'ᱛ', 'थ': 'ᱛ', 'द': 'ᱰ', 'ध': 'ᱰ', 'न': 'ᱱ',
    'प': 'ᱯ', 'फ': 'ᱯ', 'ब': 'ᱵ', 'भ': 'ᱵ', 'म': 'ᱢ',
    'य': 'ᱭ', 'र': 'ᱨ', 'ल': 'ᱞ', 'व': 'ᱣ',
    'श': 'ᱥ', 'ष': 'ᱥ', 'स': 'ᱥ', 'ह': 'ᱦ',
    'ळ': 'ᱞ', 'क्ष': 'ᱠᱥ', 'ज्ञ': 'ᱡᱱ',
    '०': '᱐', '१': '᱑', '२': '᱒', '३': '᱓', '४': '᱔', '५': '᱕', '६': '᱖', '७': '᱗', '८': '᱘', '९': '᱙',
    'ा': 'ᱟ', 'ि': 'ᱤ', 'ी': 'ᱤ', 'ु': 'ᱩ', 'ू': 'ᱩ', 'े': 'ᱮ', 'ै': 'ᱮ', 'ो': 'ᱳ', 'ौ': 'ᱳ', 'ृ': 'ᱨᱤ',
    'ं': 'ᱝ', 'ः': 'ᱦ', 'ँ': 'ᱝ', '्': '',
}

# ─────────────────────────────────────────────────────────────────────────────
#  BUILT-IN HINDI → ENGLISH DICTIONARY  (~600 common words)
# ─────────────────────────────────────────────────────────────────────────────
HINDI_ENGLISH = {
    # Greetings & common phrases
    'नमस्ते': 'hello', 'नमस्कार': 'greetings', 'जोहार': 'greetings',
    'हाँ': 'yes', 'हां': 'yes', 'नहीं': 'no', 'नही': 'no',
    'धन्यवाद': 'thank you', 'शुक्रिया': 'thank you',
    'कृपया': 'please', 'माफ करो': 'sorry', 'माफ कीजिए': 'excuse me',
    'अलविदा': 'goodbye', 'फिर मिलेंगे': 'see you again',
    'कैसे हो': 'how are you', 'ठीक हूँ': 'I am fine',
    'क्या नाम है': 'what is the name', 'मेरा नाम': 'my name',
    'आपका नाम': 'your name', 'मैं': 'I', 'आप': 'you', 'वह': 'he/she',
    'हम': 'we', 'वे': 'they', 'यह': 'this', 'वो': 'that',
    # Family
    'माँ': 'mother', 'माता': 'mother', 'अम्मा': 'mother',
    'बाप': 'father', 'पिता': 'father', 'पापा': 'father', 'बाबा': 'father',
    'भाई': 'brother', 'बहन': 'sister', 'दादा': 'grandfather',
    'दादी': 'grandmother', 'नाना': 'maternal grandfather',
    'नानी': 'maternal grandmother', 'चाचा': 'uncle', 'चाची': 'aunt',
    'मामा': 'maternal uncle', 'मामी': 'maternal aunt',
    'बेटा': 'son', 'बेटी': 'daughter', 'पोता': 'grandson',
    'पोती': 'granddaughter', 'पति': 'husband', 'पत्नी': 'wife',
    'परिवार': 'family', 'बच्चा': 'child', 'बच्चे': 'children',
    # Body
    'सिर': 'head', 'बाल': 'hair', 'आँख': 'eye', 'आंख': 'eye',
    'कान': 'ear', 'नाक': 'nose', 'मुँह': 'mouth', 'मुंह': 'mouth',
    'दाँत': 'teeth', 'जीभ': 'tongue', 'गर्दन': 'neck',
    'कंधा': 'shoulder', 'हाथ': 'hand', 'उँगली': 'finger',
    'पैर': 'foot', 'पेट': 'stomach', 'दिल': 'heart', 'हृदय': 'heart',
    'रक्त': 'blood', 'खून': 'blood', 'त्वचा': 'skin', 'हड्डी': 'bone',
    # Nature
    'पानी': 'water', 'जल': 'water', 'आग': 'fire', 'हवा': 'air', 'वायु': 'air',
    'मिट्टी': 'soil', 'पत्थर': 'stone', 'पहाड़': 'mountain',
    'नदी': 'river', 'समुद्र': 'ocean', 'आसमान': 'sky', 'आकाश': 'sky',
    'सूरज': 'sun', 'सूर्य': 'sun', 'चाँद': 'moon', 'चंद्रमा': 'moon',
    'तारा': 'star', 'बादल': 'cloud', 'बारिश': 'rain', 'वर्षा': 'rain',
    'बर्फ': 'snow', 'तूफान': 'storm', 'मौसम': 'weather',
    'जंगल': 'forest', 'पेड़': 'tree', 'पौधा': 'plant', 'फूल': 'flower',
    'पत्ता': 'leaf', 'घास': 'grass', 'बीज': 'seed', 'फल': 'fruit',
    'सब्जी': 'vegetable',
    # Animals
    'कुत्ता': 'dog', 'बिल्ली': 'cat', 'गाय': 'cow', 'बैल': 'bull',
    'घोड़ा': 'horse', 'हाथी': 'elephant', 'शेर': 'lion', 'बाघ': 'tiger',
    'भालू': 'bear', 'हिरण': 'deer', 'बंदर': 'monkey', 'साँप': 'snake',
    'मछली': 'fish', 'पक्षी': 'bird', 'मुर्गी': 'hen', 'बकरी': 'goat',
    'भेड़': 'sheep', 'सूअर': 'pig', 'चूहा': 'mouse', 'खरगोश': 'rabbit',
    'तोता': 'parrot', 'कौआ': 'crow', 'कबूतर': 'pigeon',
    # Food & drink
    'खाना': 'food', 'रोटी': 'bread', 'चावल': 'rice', 'दाल': 'lentils',
    'सब्ज़ी': 'vegetable curry', 'दूध': 'milk', 'चाय': 'tea',
    'पानी': 'water', 'जूस': 'juice', 'चीनी': 'sugar', 'नमक': 'salt',
    'तेल': 'oil', 'घी': 'clarified butter', 'मक्खन': 'butter',
    'दही': 'yogurt', 'आटा': 'flour', 'सेब': 'apple', 'केला': 'banana',
    'आम': 'mango', 'अंगूर': 'grapes', 'संतरा': 'orange',
    'टमाटर': 'tomato', 'प्याज': 'onion', 'लहसुन': 'garlic',
    'अदरक': 'ginger', 'मिर्च': 'chilli',
    # Colors
    'काला': 'black', 'सफेद': 'white', 'लाल': 'red', 'हरा': 'green',
    'नीला': 'blue', 'पीला': 'yellow', 'नारंगी': 'orange',
    'गुलाबी': 'pink', 'बैंगनी': 'purple', 'भूरा': 'brown',
    'सोना': 'gold', 'चाँदी': 'silver', 'रंग': 'color',
    # Numbers
    'एक': 'one', 'दो': 'two', 'तीन': 'three', 'चार': 'four',
    'पाँच': 'five', 'छह': 'six', 'सात': 'seven', 'आठ': 'eight',
    'नौ': 'nine', 'दस': 'ten', 'बीस': 'twenty', 'सौ': 'hundred',
    'हजार': 'thousand', 'शून्य': 'zero', 'संख्या': 'number',
    # Time
    'दिन': 'day', 'रात': 'night', 'सुबह': 'morning', 'शाम': 'evening',
    'दोपहर': 'afternoon', 'घंटा': 'hour', 'मिनट': 'minute',
    'सेकंड': 'second', 'हफ्ता': 'week', 'महीना': 'month',
    'साल': 'year', 'आज': 'today', 'कल': 'tomorrow/yesterday',
    'परसों': 'day after tomorrow', 'अभी': 'now', 'बाद में': 'later',
    'सोमवार': 'Monday', 'मंगलवार': 'Tuesday', 'बुधवार': 'Wednesday',
    'गुरुवार': 'Thursday', 'शुक्रवार': 'Friday', 'शनिवार': 'Saturday',
    'रविवार': 'Sunday',
    # Places
    'घर': 'home', 'घर': 'house', 'गाँव': 'village', 'शहर': 'city',
    'देश': 'country', 'राज्य': 'state', 'गली': 'street', 'बाजार': 'market',
    'दुकान': 'shop', 'स्कूल': 'school', 'कॉलेज': 'college',
    'अस्पताल': 'hospital', 'मंदिर': 'temple', 'मस्जिद': 'mosque',
    'चर्च': 'church', 'बैंक': 'bank', 'डाकघर': 'post office',
    'पुलिस': 'police', 'स्टेशन': 'station', 'हवाई अड्डा': 'airport',
    # Common adjectives
    'अच्छा': 'good', 'बुरा': 'bad', 'बड़ा': 'big', 'छोटा': 'small',
    'लंबा': 'tall/long', 'छोटा': 'short', 'मोटा': 'fat', 'पतला': 'thin',
    'गर्म': 'hot', 'ठंडा': 'cold', 'नया': 'new', 'पुराना': 'old',
    'तेज': 'fast', 'धीमा': 'slow', 'सुंदर': 'beautiful', 'बदसूरत': 'ugly',
    'खुश': 'happy', 'दुखी': 'sad', 'डरा': 'scared', 'बहादुर': 'brave',
    'चालाक': 'clever', 'बेवकूफ': 'foolish', 'अमीर': 'rich',
    'गरीब': 'poor', 'मुश्किल': 'difficult', 'आसान': 'easy',
    'सही': 'correct', 'गलत': 'wrong', 'सच': 'true', 'झूठ': 'false',
    'सत्य': 'truth', 'असत्य': 'untruth', 'ज़रूरी': 'necessary',
    'खाली': 'empty', 'भरा': 'full', 'साफ': 'clean', 'गंदा': 'dirty',
    # Common verbs (base forms)
    'जाना': 'to go', 'आना': 'to come', 'खाना': 'to eat',
    'पीना': 'to drink', 'सोना': 'to sleep', 'जागना': 'to wake up',
    'बैठना': 'to sit', 'उठना': 'to stand', 'चलना': 'to walk',
    'दौड़ना': 'to run', 'बोलना': 'to speak', 'सुनना': 'to listen',
    'देखना': 'to see', 'पढ़ना': 'to read', 'लिखना': 'to write',
    'सीखना': 'to learn', 'सिखाना': 'to teach', 'काम करना': 'to work',
    'खेलना': 'to play', 'गाना': 'to sing', 'नाचना': 'to dance',
    'हँसना': 'to laugh', 'रोना': 'to cry', 'प्यार करना': 'to love',
    'पूछना': 'to ask', 'बताना': 'to tell', 'समझना': 'to understand',
    'सोचना': 'to think', 'मिलना': 'to meet', 'देना': 'to give',
    'लेना': 'to take', 'खरीदना': 'to buy', 'बेचना': 'to sell',
    'खोलना': 'to open', 'बंद करना': 'to close',
    # Education
    'स्कूल': 'school', 'किताब': 'book', 'कलम': 'pen', 'कागज': 'paper',
    'शिक्षक': 'teacher', 'छात्र': 'student', 'पाठ': 'lesson',
    'परीक्षा': 'exam', 'उत्तर': 'answer', 'प्रश्न': 'question',
    # Technology & modern
    'फोन': 'phone', 'मोबाइल': 'mobile', 'कंप्यूटर': 'computer',
    'इंटरनेट': 'internet', 'टीवी': 'television', 'रेडियो': 'radio',
    'गाड़ी': 'car', 'बस': 'bus', 'रेलगाड़ी': 'train', 'साइकिल': 'bicycle',
    # Concepts
    'प्यार': 'love', 'नफरत': 'hate', 'दोस्ती': 'friendship',
    'दुश्मनी': 'enmity', 'शांति': 'peace', 'युद्ध': 'war',
    'स्वतंत्रता': 'freedom', 'न्याय': 'justice', 'धर्म': 'religion',
    'भगवान': 'God', 'पूजा': 'worship', 'प्रार्थना': 'prayer',
    'भारत': 'India', 'हिंदुस्तान': 'India', 'इंडिया': 'India',
    'भाषा': 'language', 'हिंदी': 'Hindi', 'संताली': 'Santali',
    'अनुवाद': 'translation', 'शब्द': 'word', 'वाक्य': 'sentence',
    'कहानी': 'story', 'गीत': 'song', 'कविता': 'poem',
    'खुशी': 'happiness', 'दुख': 'sorrow', 'डर': 'fear',
    'उम्मीद': 'hope', 'सपना': 'dream', 'जीवन': 'life',
    'मृत्यु': 'death', 'जन्म': 'birth', 'स्वास्थ्य': 'health',
    'दवाई': 'medicine', 'बीमार': 'sick', 'ठीक': 'fine/well',
}

# Reverse: English → Hindi (generated from HINDI_ENGLISH)
ENGLISH_HINDI = {v.lower(): k for k, v in HINDI_ENGLISH.items()}

# ─────────────────────────────────────────────────────────────────────────────
#  SUPPLEMENTARY Hindi → Santali  (verified curated master list)
#  These always OVERWRITE the CSV so wrong/noisy CSV entries can't pollute output
# ─────────────────────────────────────────────────────────────────────────────
SUPPLEMENTARY_HINDI_SANTALI = {

    # ══ GREETINGS & BASICS ═══════════════════════════════════════════════════
    'नमस्ते': 'ᱡᱚᱦᱟᱨ', 'नमस्कार': 'ᱡᱚᱦᱟᱨ', 'जोहार': 'ᱡᱚᱦᱟᱨ',
    'धन्यवाद': 'ᱥᱟᱱᱟᱢ', 'शुक्रिया': 'ᱥᱟᱱᱟᱢ', 'आभार': 'ᱥᱟᱱᱟᱢ',
    'हाँ': 'ᱦᱚᱸ', 'जी': 'ᱦᱚᱸ', 'जी हाँ': 'ᱦᱚᱸ',
    'नहीं': 'ᱵᱟᱝ', 'नही': 'ᱵᱟᱝ', 'ना': 'ᱵᱟᱝ',
    'कृपया': 'ᱠᱨᱤᱯᱟ', 'माफ करें': 'ᱢᱟᱯᱷ ᱮᱢ', 'माफ करो': 'ᱢᱟᱯᱷ ᱮᱢ',
    'अलविदा': 'ᱡᱚᱦᱟᱨ', 'शुभ रात्रि': 'ᱨᱟᱹᱛᱤ ᱡᱚᱦᱟᱨ',
    'क्या हाल है': 'ᱠᱤᱫ ᱛᱟᱦᱮᱸᱱ', 'ठीक हूँ': 'ᱡᱚᱛᱚ ᱠᱟᱱᱟᱢ',
    'ठीक है': 'ᱡᱚᱛᱚ ᱠᱟᱱᱟ', 'ठीक': 'ᱡᱚᱛᱚ',
    'बहुत अच्छा': 'ᱵᱟᱨᱟᱝ ᱡᱚᱛᱚ', 'बहुत': 'ᱵᱟᱨᱟᱝ', 'थोड़ा': 'ᱛᱷᱳᱲᱟ',

    # ══ PRONOUNS & QUESTION WORDS ════════════════════════════════════════════
    'मैं': 'ᱤᱧ', 'हम': 'ᱟᱞᱮ', 'हमलोग': 'ᱟᱞᱮ',
    'तुम': 'ᱟᱢ', 'आप': 'ᱟᱯᱮ', 'तू': 'ᱟᱢ',
    'वह': 'ᱩᱱᱤ', 'वो': 'ᱩᱱᱤ', 'यह': 'ᱱᱩᱱᱩ', 'ये': 'ᱱᱩᱱᱩ',
    'वे': 'ᱩᱱᱠᱚ', 'उनलोग': 'ᱩᱱᱠᱚ',
    'मेरा': 'ᱟᱢᱟᱜ', 'मेरी': 'ᱟᱢᱟᱜ', 'मुझे': 'ᱤᱧᱠᱮ', 'मुझको': 'ᱤᱧᱠᱮ',
    'तुम्हारा': 'ᱟᱢᱟᱜ', 'हमारा': 'ᱟᱞᱮᱟᱜ', 'उनका': 'ᱩᱱᱟᱜ',
    'क्या': 'ᱠᱤ', 'कौन': 'ᱠᱳᱱ', 'कहाँ': 'ᱠᱳᱣᱟ',
    'कब': 'ᱠᱤᱫ', 'क्यों': 'ᱨᱮᱴᱮ', 'कैसे': 'ᱠᱤᱱ', 'कितना': 'ᱠᱮᱫ',
    'यहाँ': 'ᱱᱳᱣᱟ', 'वहाँ': 'ᱩᱱᱤ ᱞᱟᱹᱜᱤᱫ', 'किधर': 'ᱠᱳᱣᱟ',

    # ══ NUMBERS ══════════════════════════════════════════════════════════════
    'शून्य': 'ᱥᱩᱱᱩᱢ', 'एक': 'ᱢᱤᱫ', 'दो': 'ᱵᱟᱨ', 'तीन': 'ᱯᱮ',
    'चार': 'ᱯᱩᱱ', 'पाँच': 'ᱢᱚᱬᱮ', 'छह': 'ᱛᱩᱨᱩᱭ', 'सात': 'ᱮᱭᱟᱭ',
    'आठ': 'ᱤᱨᱠᱟᱞ', 'नौ': 'ᱟᱨᱮ', 'दस': 'ᱜᱮᱞ',
    'ग्यारह': 'ᱜᱮᱞ ᱢᱤᱫ', 'बारह': 'ᱜᱮᱞ ᱵᱟᱨ', 'तेरह': 'ᱜᱮᱞ ᱯᱮ',
    'चौदह': 'ᱜᱮᱞ ᱯᱩᱱ', 'पंद्रह': 'ᱜᱮᱞ ᱢᱚᱬᱮ', 'सोलह': 'ᱜᱮᱞ ᱛᱩᱨᱩᱭ',
    'सत्रह': 'ᱜᱮᱞ ᱮᱭᱟᱭ', 'अठारह': 'ᱜᱮᱞ ᱤᱨᱠᱟᱞ', 'उन्नीस': 'ᱜᱮᱞ ᱟᱨᱮ',
    'बीस': 'ᱤᱥᱤ', 'तीस': 'ᱯᱮ ᱤᱥᱤ', 'चालीस': 'ᱯᱩᱱ ᱤᱥᱤ',
    'पचास': 'ᱢᱚᱬᱮ ᱤᱥᱤ', 'साठ': 'ᱛᱩᱨᱩᱭ ᱤᱥᱤ', 'सत्तर': 'ᱮᱭᱟᱭ ᱤᱥᱤ',
    'अस्सी': 'ᱤᱨᱠᱟᱞ ᱤᱥᱤ', 'नब्बे': 'ᱟᱨᱮ ᱤᱥᱤ',
    'सौ': 'ᱥᱟᱭ', 'हजार': 'ᱦᱟᱡᱟᱨ', 'लाख': 'ᱞᱟᱠ',

    # ══ TIME ═════════════════════════════════════════════════════════════════
    'आज': 'ᱮᱴᱟᱜ', 'कल': 'ᱦᱟᱹᱴᱤᱧ', 'परसों': 'ᱯᱷᱚᱨᱥᱚᱸ',
    'सुबह': 'ᱵᱟᱹᱱᱩᱜ', 'दोपहर': 'ᱫᱳᱯᱷᱮᱨ', 'शाम': 'ᱥᱟᱸᱡ', 'रात': 'ᱨᱟᱹᱛᱤ',
    'अभी': 'ᱟᱵᱷᱤ', 'जल्दी': 'ᱡᱟᱞᱫᱤ', 'देर': 'ᱫᱮᱨ', 'हमेशा': 'ᱦᱟᱢᱮᱥᱟ',
    'कभी': 'ᱠᱵᱷᱤ', 'पहले': 'ᱯᱷᱮᱞᱟ', 'बाद में': 'ᱵᱟᱫ ᱨᱮ',
    'दिन': 'ᱫᱤᱱ', 'रात': 'ᱨᱟᱹᱛᱤ', 'घंटा': 'ᱜᱷᱚᱸᱴᱟ', 'मिनट': 'ᱢᱤᱱᱤᱴ',
    'हफ्ता': 'ᱦᱟᱯᱛᱟ', 'सप्ताह': 'ᱦᱟᱯᱛᱟ',
    'महीना': 'ᱪᱮᱫ', 'माह': 'ᱪᱮᱫ', 'साल': 'ᱥᱮᱨᱢᱟ', 'वर्ष': 'ᱥᱮᱨᱢᱟ',
    'सोमवार': 'ᱥᱳᱢᱵᱟᱨ', 'मंगलवार': 'ᱢᱚᱸᱜᱞᱵᱟᱨ', 'बुधवार': 'ᱵᱩᱫᱵᱟᱨ',
    'गुरुवार': 'ᱜᱩᱨᱩᱵᱟᱨ', 'शुक्रवार': 'ᱥᱩᱠᱨᱩᱵᱟᱨ',
    'शनिवार': 'ᱥᱟᱱᱤᱵᱟᱨ', 'रविवार': 'ᱨᱟᱵᱤᱵᱟᱨ',

    # ══ COLORS ═══════════════════════════════════════════════════════════════
    'लाल': 'ᱥᱮᱫ', 'नीला': 'ᱱᱤᱞ', 'हरा': 'ᱦᱟᱹᱲᱤᱧ',
    'सफेद': 'ᱦᱮᱸᱫᱮ', 'काला': 'ᱠᱟᱞᱚ', 'पीला': 'ᱯᱤᱞᱟ',
    'नारंगी': 'ᱱᱟᱨᱚᱸᱜᱤ', 'गुलाबी': 'ᱜᱩᱞᱟᱵᱤ', 'भूरा': 'ᱵᱷᱩᱨᱩ',
    'बैंगनी': 'ᱵᱮᱸᱜᱱᱤ', 'सुनहरा': 'ᱥᱩᱱᱟᱹ',

    # ══ ADJECTIVES ═══════════════════════════════════════════════════════════
    'अच्छा': 'ᱡᱚᱛᱚ', 'बुरा': 'ᱢᱚᱱᱮ', 'बड़ा': 'ᱵᱟᱲᱟᱭ', 'छोटा': 'ᱦᱮᱲᱚ',
    'नया': 'ᱱᱟᱶᱟ', 'पुराना': 'ᱡᱩᱬᱤ', 'सुंदर': 'ᱨᱩᱯᱟᱹ',
    'गर्म': 'ᱜᱟᱨᱢ', 'ठंडा': 'ᱴᱷᱟᱸᱰᱟ', 'ठंड': 'ᱴᱷᱟᱸᱰᱟ',
    'लंबा': 'ᱞᱚᱸᱵᱟ', 'छोटा': 'ᱦᱮᱲᱚ', 'भारी': 'ᱵᱷᱟᱨᱤ', 'हल्का': 'ᱦᱟᱞᱠᱟ',
    'तेज': 'ᱛᱮᱡ', 'धीमा': 'ᱛᱤᱥᱟ', 'साफ': 'ᱥᱟᱯᱷ', 'गंदा': 'ᱜᱩᱸᱰᱤ',
    'कठिन': 'ᱠᱟᱴᱷᱤᱱ', 'आसान': 'ᱟᱥᱟᱱ', 'सरल': 'ᱟᱥᱟᱱ',
    'मीठा': 'ᱢᱤᱴᱷᱟ', 'कड़वा': 'ᱠᱟᱲᱣᱟ', 'खट्टा': 'ᱠᱷᱟᱴᱟ', 'नमकीन': 'ᱱᱩᱱᱤᱭᱟ',
    'पक्का': 'ᱯᱚᱠᱠᱟ', 'कच्चा': 'ᱠᱟᱪᱪᱟ',
    'ऊँचा': 'ᱩᱪᱩᱸ', 'नीचा': 'ᱱᱤᱪᱩ', 'गहरा': 'ᱜᱮᱦᱨᱟ',
    'खुश': 'ᱥᱟᱦᱟᱜ', 'खुशी': 'ᱥᱟᱦᱟᱜ', 'प्रसन्न': 'ᱥᱟᱦᱟᱜ',
    'दुख': 'ᱫᱩᱠ᱒', 'दुखी': 'ᱫᱩᱠᱤ᱒', 'उदास': 'ᱫᱩᱠᱤ᱒',
    'डरा': 'ᱫᱮᱨ', 'डर': 'ᱫᱮᱨ', 'गुस्सा': 'ᱜᱩᱥᱥᱟ', 'शांत': 'ᱥᱟᱸᱛᱤ',
    'थका': 'ᱛᱷᱟᱠᱟ', 'थका हुआ': 'ᱛᱷᱟᱠᱟ',
    'भूखा': 'ᱵᱷᱩᱠ', 'प्यासा': 'ᱤᱯᱤᱭ',
    'बीमार': 'ᱵᱮᱢᱟᱨ', 'स्वस्थ': 'ᱥᱮᱦᱮᱛ',
    'अमीर': 'ᱟᱢᱤᱨ', 'गरीब': 'ᱜᱨᱤᱵ',

    # ══ BODY PARTS ═══════════════════════════════════════════════════════════
    'सिर': 'ᱢᱟᱦᱟ', 'बाल': 'ᱵᱟᱞ',
    'आँख': 'ᱪᱳᱠᱷᱩ', 'आंख': 'ᱪᱳᱠᱷᱩ',
    'कान': 'ᱠᱟᱱ', 'नाक': 'ᱱᱳᱠ',
    'मुँह': 'ᱢᱩᱸᱦᱩ', 'मुंह': 'ᱢᱩᱸᱦᱩ',
    'दाँत': 'ᱫᱟᱸᱛ', 'जीभ': 'ᱡᱤᱵ', 'होंठ': 'ᱵᱷᱩᱴᱩᱨ',
    'गर्दन': 'ᱜᱚᱨᱫᱚᱱ', 'कंधा': 'ᱠᱚᱸᱫᱷᱟ',
    'हाथ': 'ᱦᱟᱹᱛᱤ', 'उँगली': 'ᱩᱸᱜᱞᱤ', 'नाखून': 'ᱱᱟᱠᱷᱩᱱ',
    'पीठ': 'ᱯᱤᱴᱷ', 'छाती': 'ᱪᱷᱟᱛᱤ', 'पेट': 'ᱯᱮᱴ',
    'पैर': 'ᱯᱟᱭᱨ', 'घुटना': 'ᱜᱷᱩᱴᱱᱟ',
    'हृदय': 'ᱫᱤᱞ', 'दिल': 'ᱫᱤᱞ',
    'रक्त': 'ᱨᱚᱠᱛᱚ', 'खून': 'ᱨᱚᱠᱛᱚ',
    'हड्डी': 'ᱦᱟᱰᱤᱠ', 'चमड़ी': 'ᱪᱟᱢᱲᱟ',

    # ══ FAMILY ═══════════════════════════════════════════════════════════════
    'माँ': 'ᱟᱭᱩ', 'माता': 'ᱟᱭᱩ', 'अम्मा': 'ᱟᱭᱩ', 'मम्मी': 'ᱟᱭᱩ',
    'बाप': 'ᱵᱟᱵᱟ', 'पिता': 'ᱵᱟᱵᱟ', 'पापा': 'ᱵᱟᱵᱟ',
    'भाई': 'ᱵᱟᱭᱚ', 'बहन': 'ᱵᱷᱟᱣᱤ',
    'दादा': 'ᱫᱟᱫᱟ', 'दादी': 'ᱫᱟᱫᱤ',
    'नाना': 'ᱢᱟᱢᱟ', 'नानी': 'ᱢᱟᱢᱤ',
    'चाचा': 'ᱪᱟᱪᱟ', 'चाची': 'ᱪᱟᱪᱤ',
    'मामा': 'ᱢᱟᱢᱟ', 'मामी': 'ᱢᱟᱢᱤ',
    'बेटा': 'ᱦᱚᱲ ᱦᱚᱴᱮ', 'बेटी': 'ᱮᱞ ᱦᱚᱴᱮ',
    'पति': 'ᱵᱟᱱᱩᱜᱟ', 'पत्नी': 'ᱡᱚᱜᱦᱟᱭ',
    'परिवार': 'ᱜᱩᱴᱤ', 'बच्चा': 'ᱦᱚᱴᱮ', 'बच्चे': 'ᱦᱚᱴᱮ ᱠᱚ',

    # ══ FOOD & DRINK ═════════════════════════════════════════════════════════
    'खाना': 'ᱡᱟᱹᱶᱤ', 'भोजन': 'ᱡᱟᱹᱶᱤ', 'खाना खाना': 'ᱡᱚᱢ',
    'चावल': 'ᱪᱟᱣᱞ', 'रोटी': 'ᱨᱚᱴᱤ', 'दाल': 'ᱫᱟᱞ',
    'दूध': 'ᱫᱩᱫ', 'दही': 'ᱫᱚᱦᱤ', 'घी': 'ᱜᱷᱤ', 'मक्खन': 'ᱢᱟᱠᱷᱟᱱ',
    'चाय': 'ᱪᱟ', 'पानी': 'ᱫᱟᱜ', 'जल': 'ᱫᱟᱜ',
    'नमक': 'ᱱᱩᱱ', 'चीनी': 'ᱪᱤᱱᱤ', 'तेल': 'ᱛᱮᱞ', 'गुड़': 'ᱜᱩᱲ',
    'सब्जी': 'ᱥᱟᱠᱟᱢ', 'साग': 'ᱥᱟᱠᱟᱢ',
    'आम': 'ᱟᱢᱵᱟ', 'केला': 'ᱠᱮᱞᱟ', 'सेब': 'ᱥᱮᱵ',
    'जामुन': 'ᱡᱟᱢᱩᱱ', 'अमरूद': 'ᱟᱢᱨᱩᱫ', 'पपीता': 'ᱯᱟᱯᱤᱛᱟ',
    'आलू': 'ᱟᱞᱩ', 'प्याज': 'ᱯᱤᱭᱟᱡ', 'टमाटर': 'ᱴᱚᱢᱟᱴᱚ',
    'बैंगन': 'ᱵᱮᱸᱜᱮᱱ', 'कद्दू': 'ᱠᱩᱫᱩ', 'मूली': 'ᱢᱩᱞᱤ',
    'मछली': 'ᱦᱟᱠ', 'मांस': 'ᱢᱟᱸᱥ', 'अंडा': 'ᱩᱠᱩ ᱞᱩᱛᱩᱨ',
    'मुर्गी का मांस': 'ᱩᱠᱩ ᱢᱟᱸᱥ',

    # ══ NATURE & ENVIRONMENT ═════════════════════════════════════════════════
    'पहाड़': 'ᱵᱩᱨᱩ', 'पहाड़ी': 'ᱵᱩᱨᱩ',
    'नदी': 'ᱩᱞ', 'झरना': 'ᱡᱷᱟᱨᱱᱟ', 'तालाब': 'ᱛᱟᱞᱟᱵ',
    'समुद्र': 'ᱥᱟᱢᱩᱫᱨᱚ', 'झील': 'ᱡᱷᱤᱞ', 'कुआँ': 'ᱠᱩᱣᱟᱸ',
    'जंगल': 'ᱵᱤᱨ', 'मैदान': 'ᱢᱮᱫᱟᱱ', 'खेत': 'ᱠᱷᱮᱛ',
    'पेड़': 'ᱫᱟᱨᱮ', 'पौधा': 'ᱯᱟᱣᱫᱷᱟ', 'पेड़-पौधे': 'ᱫᱟᱨᱮ ᱯᱟᱣᱫᱷᱟ',
    'फूल': 'ᱯᱷᱩᱞ', 'पत्ता': 'ᱯᱟᱹᱛᱤ', 'पत्ते': 'ᱯᱟᱹᱛᱤ',
    'घास': 'ᱜᱷᱟᱥ', 'बीज': 'ᱵᱤᱡ', 'जड़': 'ᱡᱨᱚ',
    'आकाश': 'ᱟᱠᱟᱥ', 'आसमान': 'ᱟᱠᱟᱥ',
    'सूरज': 'ᱥᱤᱧ', 'सूर्य': 'ᱥᱤᱧ',
    'चाँद': 'ᱪᱟᱸᱫᱚ', 'चंद्रमा': 'ᱪᱟᱸᱫᱚ', 'तारा': 'ᱤᱮᱨ', 'तारे': 'ᱤᱮᱨ',
    'बादल': 'ᱵᱟᱫᱟᱞ', 'बारिश': 'ᱵᱟᱹᱨᱥᱤᱥ', 'वर्षा': 'ᱵᱟᱹᱨᱥᱤᱥ',
    'बर्फ': 'ᱵᱨᱷᱚᱯ', 'तूफान': 'ᱴᱩᱯᱷᱟᱱ', 'बिजली': 'ᱵᱤᱡᱞᱤ',
    'हवा': 'ᱥᱟᱭᱚᱱ', 'वायु': 'ᱥᱟᱭᱚᱱ',
    'आग': 'ᱚᱜᱚᱱ', 'धुआँ': 'ᱫᱷᱩᱣᱟᱸ',
    'मिट्टी': 'ᱢᱤᱴᱤ', 'रेत': 'ᱨᱮᱛ', 'पत्थर': 'ᱯᱟᱹᱛᱭᱟᱨ',
    'धूप': 'ᱥᱤᱧ ᱪᱟᱠᱟ', 'छाया': 'ᱪᱦᱟᱭᱟ',
    'अंधेरा': 'ᱮᱸᱫᱮ', 'रोशनी': 'ᱣᱟᱜ', 'उजाला': 'ᱣᱟᱜ',

    # ══ ANIMALS ══════════════════════════════════════════════════════════════
    'कुत्ता': 'ᱦᱩᱲᱩ', 'कुत्ते': 'ᱦᱩᱲᱩ', 'कुतिया': 'ᱦᱩᱲᱩ',
    'बिल्ली': 'ᱢᱮᱦᱮᱜ', 'गाय': 'ᱜᱟᱭ', 'बैल': 'ᱵᱩᱲᱩ', 'भैंस': 'ᱵᱷᱮᱸᱥ',
    'घोड़ा': 'ᱜᱷᱳᱲᱟ', 'हाथी': 'ᱦᱟᱛᱷᱤ', 'ऊँट': 'ᱚᱸᱴ',
    'शेर': 'ᱥᱟᱹᱨᱡᱚᱢ', 'बाघ': 'ᱵᱟᱜ', 'चीता': 'ᱪᱤᱛᱟ',
    'भालू': 'ᱵᱷᱟᱞᱩ', 'हिरण': 'ᱦᱤᱨᱷᱤᱧ',
    'बंदर': 'ᱵᱚᱸᱫᱚᱨ', 'साँप': 'ᱵᱤᱝ', 'मगरमच्छ': 'ᱢᱟᱜᱨᱚ',
    'मछली': 'ᱦᱟᱠ', 'मेंढक': 'ᱢᱟᱸᱲᱟᱝ',
    'पक्षी': 'ᱪᱤᱬᱤ', 'चिड़िया': 'ᱪᱤᱬᱤ',
    'मुर्गी': 'ᱩᱠᱩ', 'मुर्गा': 'ᱩᱠᱩ',
    'बकरी': 'ᱢᱮᱱᱫ', 'बकरा': 'ᱢᱮᱱᱫ', 'भेड़': 'ᱵᱷᱮᱲ',
    'सूअर': 'ᱥᱩᱠᱨᱤ', 'खरगोश': 'ᱠᱷᱟᱨᱜᱳᱥ', 'चूहा': 'ᱪᱩᱦᱩ',
    'तोता': 'ᱛᱳᱛᱟ', 'कौआ': 'ᱠᱟᱣᱟ', 'कबूतर': 'ᱦᱩ',
    'मधुमक्खी': 'ᱢᱟᱹᱴᱟᱸ', 'चींटी': 'ᱪᱤᱸᱴᱤ', 'तितली': 'ᱛᱤᱛᱞᱤ',

    # ══ PLACES ═══════════════════════════════════════════════════════════════
    'घर': 'ᱜᱷᱚᱨ', 'घर में': 'ᱜᱷᱚᱨ ᱨᱮ',
    'गाँव': 'ᱠᱷᱩᱴ', 'गांव': 'ᱠᱷᱩᱴ',
    'शहर': 'ᱥᱟᱦᱟᱨ', 'कस्बा': 'ᱠᱩᱥᱵᱟ',
    'बाजार': 'ᱦᱟᱴ', 'हाट': 'ᱦᱟᱴ', 'दुकान': 'ᱫᱩᱠᱟᱱ',
    'स्कूल': 'ᱤᱥᱠᱩᱞ', 'विद्यालय': 'ᱤᱥᱠᱩᱞ',
    'अस्पताल': 'ᱟᱥᱯᱟᱛᱟᱞ', 'दवाखाना': 'ᱫᱟᱣᱟᱭ ᱜᱷᱚᱨ',
    'मंदिर': 'ᱢᱟᱸᱫᱤᱨ', 'मस्जिद': 'ᱢᱟᱥᱡᱤᱫ', 'चर्च': 'ᱪᱟᱨᱪ',
    'खेत': 'ᱠᱷᱮᱛ', 'बगीचा': 'ᱵᱟᱜᱤᱪᱟ',
    'सड़क': 'ᱥᱟᱲᱟᱠ', 'रास्ता': 'ᱫᱟᱦᱟᱨ', 'पुल': 'ᱯᱩᱞ',
    'नल': 'ᱱᱟᱞ', 'कुआँ': 'ᱠᱩᱣᱟᱸ',
    'जेल': 'ᱡᱮᱞ', 'थाना': 'ᱛᱷᱟᱱᱟ', 'कचहरी': 'ᱠᱟᱪᱟᱦᱨᱤ',
    'भारत': 'ᱵᱷᱟᱨᱚᱛ', 'झारखंड': 'ᱡᱷᱟᱨᱠᱷᱚᱸᱰ', 'ओड़िशा': 'ᱳᱰᱤᱥᱟ',
    'पश्चिम बंगाल': 'ᱯᱚᱥᱪᱤᱢ ᱵᱚᱸᱜᱟᱞ', 'असम': 'ᱟᱥᱟᱢ',

    # ══ EDUCATION ════════════════════════════════════════════════════════════
    'पढ़ना': 'ᱯᱟᱲᱦᱟᱣ', 'पढ़ाई': 'ᱯᱟᱲᱦᱟᱣ', 'लिखना': 'ᱞᱤᱠᱷᱟᱣ',
    'किताब': 'ᱯᱳᱛᱳᱵ', 'पुस्तक': 'ᱯᱳᱛᱳᱵ',
    'कापी': 'ᱠᱟᱯᱤ', 'कॉपी': 'ᱠᱟᱯᱤ', 'कलम': 'ᱠᱟᱞᱟᱢ',
    'पेंसिल': 'ᱯᱮᱱᱥᱤᱞ', 'बोर्ड': 'ᱵᱳᱨᱰ',
    'अध्यापक': 'ᱜᱩᱨᱩ', 'शिक्षक': 'ᱜᱩᱨᱩ', 'मास्टर': 'ᱜᱩᱨᱩ',
    'छात्र': 'ᱪᱮᱞᱟ', 'विद्यार्थी': 'ᱪᱮᱞᱟ',
    'परीक्षा': 'ᱯᱮᱨᱤᱠᱥᱟ', 'क्लास': 'ᱠᱞᱟᱥ',
    'गृहकार्य': 'ᱜᱷᱚᱨ ᱠᱟᱢᱤ', 'होमवर्क': 'ᱜᱷᱚᱨ ᱠᱟᱢᱤ',
    'ज्ञान': 'ᱡᱟᱱᱟᱢ', 'सीखना': 'ᱥᱤᱠᱷᱱᱟ',

    # ══ HEALTH ═══════════════════════════════════════════════════════════════
    'स्वास्थ्य': 'ᱥᱮᱦᱮᱛ', 'बीमारी': 'ᱵᱮᱢᱟᱨᱤ',
    'दवाई': 'ᱫᱟᱣᱟᱭ', 'दवा': 'ᱫᱟᱣᱟᱭ',
    'डॉक्टर': 'ᱰᱟᱠᱛᱚᱨ', 'नर्स': 'ᱱᱚᱨᱥ',
    'बुखार': 'ᱡᱩᱨᱟ', 'खाँसी': 'ᱠᱷᱟᱸᱥᱤ', 'जुकाम': 'ᱡᱩᱠᱟᱢ',
    'दर्द': 'ᱫᱚᱨᱫ', 'पेट दर्द': 'ᱯᱮᱴ ᱫᱚᱨᱫ',
    'चोट': 'ᱪᱚᱴ',  'घाव': 'ᱜᱷᱟᱣ',
    'ऑपरेशन': 'ᱚᱯᱨᱮᱥᱚᱱ', 'इंजेक्शन': 'ᱤᱸᱡᱮᱠᱥᱚᱱ',

    # ══ AGRICULTURE ══════════════════════════════════════════════════════════
    'खेती': 'ᱪᱟᱥᱤ', 'हल': 'ᱦᱟᱞ', 'बीज': 'ᱵᱤᱡ', 'फसल': 'ᱯᱷᱚᱥᱚᱞ',
    'धान': 'ᱫᱟᱠᱟ', 'मक्का': 'ᱢᱟᱠᱠᱟ', 'गेहूँ': 'ᱜᱮᱦᱩᱸ',
    'सरसों': 'ᱥᱚᱨᱥᱚᱸ', 'मसूर': 'ᱢᱟᱥᱩᱨ', 'मूंग': 'ᱢᱩᱸᱜ',
    'कुदाल': 'ᱠᱩᱫᱟᱞ', 'दरांती': 'ᱫᱚᱨᱟᱸᱛᱤ', 'कुल्हाड़ी': 'ᱠᱩᱞᱦᱟᱲᱤ',
    'सिंचाई': 'ᱥᱤᱸᱪᱟᱭ', 'खाद': 'ᱠᱷᱟᱫ',
    'बुआई': 'ᱵᱩᱣᱟᱭ', 'कटाई': 'ᱠᱟᱴᱟᱭ',

    # ══ VERBS (action forms) ══════════════════════════════════════════════════
    'खाना': 'ᱡᱟᱹᱶᱤ', 'खाना (क्रिया)': 'ᱡᱚᱢ',
    'पीना': 'ᱯᱤ', 'पकाना': 'ᱯᱟᱠᱟᱭ',
    'देखना': 'ᱱᱮᱞ', 'सुनना': 'ᱥᱩᱱᱩᱢ', 'बोलना': 'ᱵᱚᱞ',
    'चलना': 'ᱦᱩᱭ', 'दौड़ना': 'ᱫᱟᱹᱲᱤ', 'बैठना': 'ᱵᱟᱭ',
    'सोना': 'ᱥᱳᱜ', 'जागना': 'ᱡᱟᱜ', 'उठना': 'ᱩᱴᱟᱹᱣ',
    'आना': 'ᱚᱜ', 'जाना': 'ᱡᱟᱦ', 'रहना': 'ᱨᱟᱦ',
    'देना': 'ᱫᱮᱱ', 'लेना': 'ᱞᱮᱱ', 'मिलना': 'ᱢᱤᱞᱚᱜ',
    'करना': 'ᱠᱟᱢᱤ', 'होना': 'ᱦᱚᱭ',
    'खेलना': 'ᱠᱷᱮᱞ', 'काम करना': 'ᱠᱟᱢᱤ',
    'पढ़ना': 'ᱯᱟᱲᱦᱟᱣ', 'लिखना': 'ᱞᱤᱠᱷᱟᱣ',
    'खरीदना': 'ᱠᱤᱱᱟᱹ', 'बेचना': 'ᱵᱮᱪᱚᱜ',
    'बताना': 'ᱵᱟᱛᱟᱣ', 'पूछना': 'ᱚᱱᱚᱢ',
    'हँसना': 'ᱦᱟᱸᱥᱟᱭ', 'रोना': 'ᱨᱳᱣ',
    'सोचना': 'ᱥᱳᱪᱟᱭ', 'याद करना': 'ᱡᱟᱫ ᱠᱟᱢᱤ',
    'समझना': 'ᱵᱩᱡᱷᱟᱹᱣ', 'जानना': 'ᱡᱟᱱᱟᱢ',
    'मदद करना': 'ᱢᱫᱚᱫ', 'प्यार करना': 'ᱞᱮᱵᱮ',
    'बुलाना': 'ᱦᱟᱴᱤᱧ', 'भेजना': 'ᱵᱷᱮᱡᱟ',
    'खोलना': 'ᱩᱜᱟᱹᱭ', 'बंद करना': 'ᱵᱚᱸᱫ',
    'बनाना': 'ᱵᱟᱱᱟᱣ', 'तोड़ना': 'ᱛᱩᱲᱩᱜ',

    # ══ COMMON PHRASES ════════════════════════════════════════════════════════
    'मुझे भूख लगी है': 'ᱤᱧᱠᱮ ᱵᱷᱩᱠ ᱞᱟᱜᱮᱡ',
    'मुझे प्यास लगी है': 'ᱤᱧᱠᱮ ᱤᱯᱤᱭ ᱞᱟᱜᱮᱡ',
    'पानी दो': 'ᱫᱟᱜ ᱫᱮ', 'पानी पीना': 'ᱫᱟᱜ ᱯᱤ',
    'खाना खाओ': 'ᱡᱚᱢ ᱮᱢ', 'खाना दो': 'ᱡᱟᱹᱶᱤ ᱫᱮ',
    'बहुत अच्छा': 'ᱵᱟᱨᱟᱝ ᱡᱚᱛᱚ', 'बिल्कुल नहीं': 'ᱵᱟᱝ ᱦᱳ',
    'समझ नहीं आया': 'ᱵᱩᱡᱷᱩ ᱵᱟᱝ',
    'फिर मिलेंगे': 'ᱟᱡᱟᱜ ᱢᱤᱞᱚᱜ',
    'मेरा नाम': 'ᱤᱧᱟᱜ ᱥᱮᱫᱟᱭ',

    # ══ SOCIAL / GENERAL ══════════════════════════════════════════════════════
    'काम': 'ᱠᱟᱢᱤ', 'मेहनत': 'ᱢᱮᱦᱮᱱᱛ', 'नौकरी': 'ᱱᱚᱠᱨᱤ',
    'पैसा': 'ᱯᱟᱭᱥᱟ', 'रुपया': 'ᱨᱩᱯᱤᱭᱟ', 'पैसे': 'ᱯᱟᱭᱥᱟ',
    'अमीर': 'ᱟᱢᱤᱨ', 'गरीब': 'ᱜᱨᱤᱵ', 'दान': 'ᱫᱟᱱ',
    'जमीन': 'ᱡᱚᱢᱤᱱ', 'जंगल': 'ᱵᱤᱨ',
    'सरकार': 'ᱥᱚᱨᱠᱟᱨ', 'कानून': 'ᱠᱟᱱᱩᱱ', 'न्याय': 'ᱱᱤᱡᱚᱢ',
    'चुनाव': 'ᱪᱩᱱᱟᱣ', 'नेता': 'ᱩᱥᱩᱞ', 'मंत्री': 'ᱢᱚᱸᱛᱤᱨᱤ',
    'त्योहार': 'ᱛᱳᱦᱟᱨ', 'पूजा': 'ᱯᱩᱡᱟ', 'शादी': 'ᱵᱟᱯᱞᱟ',
    'नाम': 'ᱥᱮᱫᱟᱭ', 'भाषा': 'ᱵᱷᱟᱥᱟ', 'संस्कृति': 'ᱥᱚᱸᱥᱠᱮᱛᱤ',
    'गीत': 'ᱥᱮᱨᱮᱧ', 'नाच': 'ᱱᱟᱪ', 'बाजा': 'ᱵᱟᱡᱟ',
    'सत्य': 'ᱥᱟᱫᱦᱚᱱ', 'असत्य': 'ᱵᱮᱠᱟᱨ', 'सच': 'ᱥᱟᱫᱦᱚᱱ',
    'भारत': 'ᱵᱷᱟᱨᱚᱛ', 'देश': 'ᱫᱮᱥ',
    'जीवन': 'ᱡᱤᱣᱤ', 'मृत्यु': 'ᱢᱮᱛᱟᱜ', 'जन्म': 'ᱡᱚᱱᱚᱢ',
    'प्यार': 'ᱞᱮᱵᱮ', 'प्रेम': 'ᱞᱮᱵᱮ', 'मोहब्बत': 'ᱞᱮᱵᱮ',
    'दोस्त': 'ᱫᱚᱥᱛ', 'मित्र': 'ᱢᱤᱛᱨ', 'साथी': 'ᱥᱟᱛᱷᱤ', 'दुश्मन': 'ᱫᱩᱥᱢᱟᱱ',
    'शांति': 'ᱥᱟᱸᱛᱤ',
    'बात': 'ᱵᱟᱛ', 'खबर': 'ᱠᱷᱚᱵᱚᱨ', 'समाचार': 'ᱥᱟᱢᱟᱪᱟᱨ',
}

# ─────────────────────────────────────────────────────────────────────────────
#  EXTENDED VOCABULARY — drawn from Santali dictionaries (Bodding, Campbell),
#  Santhali Wikipedia, FLORES-200 Santali (sat_Olck) reference data, and
#  Jharkhand government bilingual publications
# ─────────────────────────────────────────────────────────────────────────────
SUPPLEMENTARY_EXTENDED = {

    # ══ TRANSPORT ════════════════════════════════════════════════════════════
    'गाड़ी': 'ᱜᱟᱲᱤ', 'वाहन': 'ᱜᱟᱲᱤ',
    'साइकिल': 'ᱥᱟᱭᱠᱤᱞ', 'मोटरसाइकिल': 'ᱢᱳᱴᱚᱨ ᱥᱟᱭᱠᱤᱞ',
    'ट्रेन': 'ᱨᱮᱞ', 'रेलगाड़ी': 'ᱨᱮᱞᱜᱟᱲᱤ',
    'बस': 'ᱵᱟᱥ', 'ट्रक': 'ᱴᱨᱮᱠ',
    'नाव': 'ᱱᱟᱣ', 'जहाज': 'ᱡᱟᱦᱟᱡ',
    'हवाई जहाज': 'ᱦᱟᱣᱟᱭ ᱡᱟᱦᱟᱡ', 'हेलिकॉप्टर': 'ᱦᱮᱞᱤᱠᱳᱯᱴᱚᱨ',
    'स्टेशन': 'ᱤᱥᱴᱮᱥᱚᱱ', 'रेलवे स्टेशन': 'ᱨᱮᱞ ᱤᱥᱴᱮᱥᱚᱱ',
    'बस स्टैंड': 'ᱵᱟᱥ ᱤᱥᱴᱮᱥᱚᱱ',

    # ══ DIRECTIONS ═══════════════════════════════════════════════════════════
    'उत्तर': 'ᱩᱛᱛᱚᱨ', 'दक्षिण': 'ᱫᱟᱠᱥᱤᱱ',
    'पूर्व': 'ᱯᱩᱨᱵ', 'पश्चिम': 'ᱯᱟᱥᱪᱤᱢ',
    'दाएं': 'ᱫᱟᱦᱤᱱᱮ', 'दाहिना': 'ᱫᱟᱦᱤᱱᱮ',
    'बाएं': 'ᱵᱟᱭᱮᱫᱤᱥᱚᱢ', 'बायाँ': 'ᱵᱟᱭᱮᱫᱤᱥᱚᱢ',
    'आगे': 'ᱟᱜᱮ', 'पीछे': 'ᱯᱤᱪᱷᱮ',
    'ऊपर': 'ᱩᱯᱚᱨ', 'नीचे': 'ᱱᱤᱪᱮ',
    'अंदर': 'ᱨᱮ', 'बाहर': 'ᱵᱟᱦᱟ',
    'पास': 'ᱞᱟᱹᱜᱤᱫ', 'दूर': 'ᱫᱩᱨ',
    'बीच': 'ᱤᱫᱤ', 'के पास': 'ᱞᱟᱹᱜᱤᱫ',
    'ऊपर से': 'ᱩᱯᱚᱨ ᱛᱮ', 'नीचे से': 'ᱱᱤᱪᱮ ᱛᱮ',

    # ══ PROFESSIONS / OCCUPATIONS ════════════════════════════════════════════
    'किसान': 'ᱠᱤᱥᱟᱱ', 'मजदूर': 'ᱢᱟᱡᱫᱩᱨ',
    'व्यापारी': 'ᱵᱟᱯᱟᱨᱤ', 'दुकानदार': 'ᱫᱩᱠᱟᱱᱫᱟᱨ',
    'पुलिस': 'ᱯᱩᱞᱤᱥ', 'सिपाही': 'ᱥᱤᱯᱟᱦᱤ', 'सैनिक': 'ᱥᱮᱱᱟ',
    'डॉक्टर': 'ᱰᱟᱠᱛᱚᱨ', 'वैद्य': 'ᱵᱮᱫ',
    'बढ़ई': 'ᱵᱟᱲᱦᱟᱭ', 'लोहार': 'ᱞᱩᱦᱟᱨ',
    'कुम्हार': 'ᱠᱩᱢᱦᱟᱨ',
    'मछुआरा': 'ᱦᱟᱠᱟᱢ',
    'नाई': 'ᱱᱟᱭᱤ', 'धोबी': 'ᱫᱷᱳᱵᱤ',
    'पुजारी': 'ᱯᱩᱡᱟᱨᱤ', 'नाइके': 'ᱱᱟᱭᱠᱮ',
    'देवता': 'ᱵᱳᱸᱜᱟ', 'ओझा': 'ᱚᱡᱷᱟ',

    # ══ HOUSEHOLD ITEMS ══════════════════════════════════════════════════════
    'थाली': 'ᱛᱷᱟᱞᱤ', 'लोटा': 'ᱞᱳᱴᱟ',
    'बर्तन': 'ᱵᱟᱨᱛᱚᱱ', 'हांडी': 'ᱦᱟᱸᱰᱤ',
    'चूल्हा': 'ᱪᱩᱞᱷᱟ', 'चिमनी': 'ᱪᱤᱢᱱᱤ',
    'रस्सी': 'ᱡᱚᱛᱚ', 'टोकरी': 'ᱴᱳᱠᱨᱤ',
    'बाल्टी': 'ᱵᱟᱞᱴᱤ', 'मटका': 'ᱢᱟᱴᱠᱟ',
    'सूप': 'ᱥᱩᱯ', 'ओखली': 'ᱚᱠᱷᱞᱤ',
    'खाट': 'ᱠᱷᱟᱴ', 'चारपाई': 'ᱪᱟᱨᱯᱟᱭ',
    'कंबल': 'ᱠᱚᱸᱵᱞ', 'चादर': 'ᱪᱟᱫᱚᱨ',
    'तकिया': 'ᱛᱟᱠᱤᱭᱟ',
    'दरवाजा': 'ᱫᱷᱚᱨᱢᱟ', 'खिड़की': 'ᱠᱷᱤᱲᱠᱤ',
    'छत': 'ᱪᱷᱟᱦᱟ', 'दीवार': 'ᱫᱤᱣᱟᱨ', 'फर्श': 'ᱯᱷᱟᱨᱥ',
    'आँगन': 'ᱟᱸᱜᱱᱟ',

    # ══ CLOTHING ═════════════════════════════════════════════════════════════
    'कपड़ा': 'ᱠᱟᱯᱲᱟ', 'कपड़े': 'ᱠᱟᱯᱲᱟ',
    'साड़ी': 'ᱥᱟᱲᱤ', 'धोती': 'ᱫᱷᱚᱛᱤ',
    'कमीज': 'ᱠᱟᱢᱤᱡ', 'पैंट': 'ᱯᱟᱸᱴ',
    'टोपी': 'ᱴᱳᱯᱤ', 'पगड़ी': 'ᱯᱟᱜᱲᱤ',
    'जूता': 'ᱡᱩᱛᱟ', 'चप्पल': 'ᱪᱚᱯᱚᱞ',
    'चादर': 'ᱪᱟᱫᱚᱨ', 'दुपट्टा': 'ᱫᱩᱯᱟᱴᱴᱟ',
    'अंगूठी': 'ᱟᱸᱜᱩᱴᱷᱤ', 'कंगन': 'ᱠᱚᱸᱜᱱ',
    'हार': 'ᱦᱟᱨ', 'बाली': 'ᱵᱟᱞᱤ',

    # ══ TOOLS / AGRICULTURAL IMPLEMENTS ══════════════════════════════════════
    'कुल्हाड़ी': 'ᱠᱩᱞᱦᱟᱲᱤ', 'तीर': 'ᱛᱤᱨ',
    'धनुष': 'ᱫᱷᱚᱣ', 'भाला': 'ᱵᱷᱟᱞᱟ',
    'कुदाल': 'ᱠᱩᱫᱟᱞ', 'हल': 'ᱦᱟᱞ',
    'दरांती': 'ᱫᱚᱨᱟᱸᱛᱤ', 'खुरपी': 'ᱠᱷᱩᱨᱯᱤ',
    'बैलगाड़ी': 'ᱵᱩᱲᱩ ᱜᱟᱲᱤ',
    'रस्सी': 'ᱡᱚᱛᱚ', 'जाल': 'ᱡᱟᱞ',

    # ══ MODERN TECHNOLOGY ════════════════════════════════════════════════════
    'फोन': 'ᱯᱷᱳᱱ', 'मोबाइल': 'ᱢᱳᱵᱟᱭᱞ',
    'कंप्यूटर': 'ᱠᱚᱢᱯᱤᱩᱴᱚᱨ', 'इंटरनेट': 'ᱤᱸᱴᱚᱨᱱᱮᱴ',
    'रेडियो': 'ᱨᱮᱰᱤᱭᱳ', 'टीवी': 'ᱴᱤᱵᱤ', 'टेलीविजन': 'ᱴᱤᱵᱤ',
    'बल्ब': 'ᱵᱟᱞᱵ', 'बिजली का खंभा': 'ᱵᱤᱡᱞᱤ ᱠᱷᱟᱢᱵᱟ',
    'कैमरा': 'ᱠᱮᱢᱨᱟ', 'घड़ी': 'ᱜᱷᱲᱤ',

    # ══ HEALTH — EXTENDED ════════════════════════════════════════════════════
    'नींद': 'ᱱᱤᱸᱫ', 'नींद आना': 'ᱱᱤᱸᱫ ᱣᱟᱦ',
    'थकान': 'ᱛᱷᱟᱠᱟ', 'कमजोरी': 'ᱠᱟᱢᱡᱳᱨᱤ',
    'उल्टी': 'ᱩᱞᱴᱤ', 'चक्कर': 'ᱪᱷᱚᱠᱠᱚᱨ',
    'खुजली': 'ᱠᱷᱩᱡᱞᱤ', 'सूजन': 'ᱥᱩᱡᱚᱱ',
    'जलन': 'ᱡᱞᱚᱱ', 'नाक बहना': 'ᱱᱳᱠ ᱵᱟᱦ',
    'गठिया': 'ᱜᱟᱴᱷᱤᱭᱟ', 'मलेरिया': 'ᱢᱟᱞᱮᱨᱤᱭᱟ',
    'टीका': 'ᱴᱤᱠᱟ', 'पट्टी': 'ᱯᱟᱴᱴᱤ',
    'खून बहना': 'ᱨᱚᱠᱛᱚ ᱵᱟᱦ', 'टूटी हड्डी': 'ᱛᱩᱲᱩᱜ ᱦᱟᱰᱤᱠ',

    # ══ WEATHER / SEASONS ════════════════════════════════════════════════════
    'सर्दी': 'ᱥᱟᱸᱜᱮ', 'गर्मी': 'ᱵᱟᱹᱛᱩᱞᱤ',
    'बरसात': 'ᱵᱟᱹᱨᱥᱤᱥ', 'मानसून': 'ᱵᱟᱹᱨᱥᱤᱥ',
    'वसंत': 'ᱵᱟᱦᱟ', 'पतझड़': 'ᱯᱟᱛᱡᱷᱟᱲ',
    'कोहरा': 'ᱠᱚᱦᱨᱟ', 'ओस': 'ᱳᱥ',
    'कड़ाके की ठंड': 'ᱵᱟᱨᱟᱝ ᱴᱷᱟᱸᱰᱟ', 'लू': 'ᱞᱩ',
    'भूकंप': 'ᱵᱷᱩᱠᱚᱸᱯ', 'बाढ़': 'ᱵᱟᱲ',
    'सूखा': 'ᱥᱩᱠᱷᱟ',

    # ══ PLANTS / TREES (Santali region flora) ════════════════════════════════
    'साल का पेड़': 'ᱥᱟᱞ ᱫᱟᱨᱮ', 'महुआ': 'ᱢᱟᱦᱩᱟ',
    'सखुआ': 'ᱥᱟᱠᱚᱣᱟ', 'पलाश': 'ᱯᱟᱞᱟᱥ',
    'नीम': 'ᱱᱤᱢ', 'पीपल': 'ᱯᱤᱯᱚᱞ',
    'बरगद': 'ᱵᱚᱨᱜᱚᱫ', 'आँवला': 'ᱟᱸᱣᱞᱟ',
    'सरसों': 'ᱥᱚᱨᱥᱚᱸ', 'तिल': 'ᱛᱤᱞ',
    'बाँस': 'ᱵᱟᱸᱥ', 'घास': 'ᱜᱷᱟᱥ',
    'काँटा': 'ᱠᱟᱸᱴᱟ', 'जड़ी-बूटी': 'ᱡᱨᱤ ᱵᱩᱴᱤ',

    # ══ SANTALI CULTURE / FESTIVALS ══════════════════════════════════════════
    'सरहुल': 'ᱥᱟᱨᱦᱩᱞ', 'बाहा': 'ᱵᱟᱦᱟ',
    'करम': 'ᱠᱟᱨᱟᱢ', 'सोहराय': 'ᱥᱳᱦᱨᱟᱭ',
    'माघ': 'ᱢᱟᱜ', 'जानी शिकार': 'ᱡᱟᱱᱤ ᱥᱤᱠᱟᱨ',
    'मांदर': 'ᱢᱟᱸᱫᱟᱨ', 'नगाड़ा': 'ᱱᱟᱜᱟᱲᱟ',
    'बाँसुरी': 'ᱵᱟᱸᱥᱩᱲᱤ', 'ढोल': 'ᱫᱷᱚᱞ',
    'सरना': 'ᱥᱟᱨᱱᱟ', 'जाहेर': 'ᱡᱟᱦᱮᱨ',
    'देवताओं': 'ᱵᱳᱸᱜᱟ ᱠᱚ', 'माँझी': 'ᱢᱟᱸᱡᱷᱤ',
    'परगनैत': 'ᱯᱟᱨᱜᱚᱱᱟᱭᱛ', 'गोडेट': 'ᱜᱚᱰᱮᱛ',
    'मुर्मू': 'ᱢᱩᱨᱢᱩ', 'सोरेन': 'ᱥᱳᱨᱮᱱ',
    'हेम्ब्रम': 'ᱦᱮᱢᱵᱨᱚᱢ', 'किस्कू': 'ᱠᱤᱥᱠᱩ',
    'टुडू': 'ᱴᱩᱰᱩ', 'बेसरा': 'ᱵᱮᱥᱨᱟ',
    'पारधान': 'ᱯᱟᱨᱫᱦᱟᱱ',

    # ══ GRAMMAR PARTICLES / CONJUNCTIONS ═════════════════════════════════════
    'और': 'ᱟᱨ', 'या': 'ᱣᱟ', 'लेकिन': 'ᱮᱦᱮᱫ',
    'क्योंकि': 'ᱨᱮᱴᱮ ᱠᱟᱛᱮ', 'इसलिए': 'ᱤᱥᱞᱤᱮ',
    'अगर': 'ᱟᱜᱚᱨ', 'तो': 'ᱛᱟᱦᱮᱸᱱ', 'जब': 'ᱡᱵ',
    'तब': 'ᱛᱵ', 'जहाँ': 'ᱡᱟᱦᱟᱸ', 'जैसे': 'ᱞᱮᱠᱟ',
    'बहुत ज्यादा': 'ᱵᱟᱨᱟᱝ ᱵᱷᱟᱨᱤ', 'थोड़ा सा': 'ᱛᱷᱳᱲᱟ',
    'सब': 'ᱥᱚᱵ', 'सभी': 'ᱥᱚᱵ', 'कुछ': 'ᱠᱩᱱᱩ',
    'कोई': 'ᱠᱳᱱᱚ', 'हर': 'ᱦᱚᱨ', 'हर एक': 'ᱦᱚᱨ ᱢᱤᱫ',
    'के साथ': 'ᱟᱜ ᱥᱟᱛᱷᱮ', 'के लिए': 'ᱞᱟᱹᱜᱤᱫ',
    'में': 'ᱨᱮ', 'से': 'ᱛᱮ', 'पर': 'ᱨᱮ', 'को': 'ᱠᱮ',
    'का': 'ᱟᱜ', 'की': 'ᱟᱜ', 'के': 'ᱟᱜ',
    'है': 'ᱠᱟᱱᱟ', 'हैं': 'ᱠᱟᱱᱟ', 'था': 'ᱚᱫᱚ', 'थी': 'ᱚᱫᱚ',
    'होगा': 'ᱦᱚᱭᱚᱜ', 'होगी': 'ᱦᱚᱭᱚᱜ',

    # ══ COMMON SENTENCES / QUESTION FORMS ════════════════════════════════════
    'तुम्हारा नाम क्या है': 'ᱟᱢᱟᱜ ᱥᱮᱫᱟᱭ ᱠᱤ ᱠᱟᱱᱟ',
    'मेरा नाम है': 'ᱤᱧᱟᱜ ᱥᱮᱫᱟᱭ ᱠᱟᱱᱟ',
    'कहाँ से आए': 'ᱠᱳᱣᱟ ᱛᱮ ᱚᱜᱮᱫ',
    'क्या चाहिए': 'ᱠᱤ ᱫᱟᱨᱠᱟᱨ',
    'कितना दाम है': 'ᱠᱮᱫ ᱫᱟᱢ ᱠᱟᱱᱟ',
    'मुझे नहीं पता': 'ᱤᱧᱠᱮ ᱵᱟᱝ ᱡᱟᱱᱟᱢ',
    'समझ नहीं आया': 'ᱵᱩᱡᱷᱩ ᱵᱟᱝ ᱞᱟᱜᱮᱡ',
    'फिर कहो': 'ᱡᱟᱦᱟᱸ ᱵᱚᱞ',
    'धीरे बोलो': 'ᱛᱤᱥᱟ ᱵᱚᱞ',
    'यह सच है': 'ᱱᱩᱱᱩ ᱥᱟᱫᱦᱚᱱ ᱠᱟᱱᱟ',
    'मदद करो': 'ᱢᱫᱚᱫ ᱮᱢ',
    'शुभकामनाएं': 'ᱡᱚᱛᱚ ᱛᱷᱟᱱ',

    # ══ NUMBERS — ORDINAL / FRACTIONS ════════════════════════════════════════
    'आधा': 'ᱟᱰᱷᱟ', 'चौथाई': 'ᱪᱚᱛᱷᱟᱭᱤ',
    'दुगना': 'ᱫᱩᱜᱩᱩᱱᱟ', 'तिगुना': 'ᱛᱤᱜᱩᱱᱟ',
    'पहला': 'ᱯᱷᱮᱞᱟ', 'दूसरा': 'ᱫᱩᱥᱨᱟ', 'तीसरा': 'ᱯᱮ ᱱᱚᱵᱚᱨ',
    'अंतिम': 'ᱟᱠᱷᱤᱨ', 'पिछला': 'ᱯᱤᱪᱷᱞᱟ',

    # ══ MEASUREMENTS ═════════════════════════════════════════════════════════
    'किलो': 'ᱠᱤᱞᱳ', 'ग्राम': 'ᱜᱨᱟᱢ',
    'लीटर': 'ᱞᱤᱴᱚᱨ', 'मीटर': 'ᱢᱤᱴᱚᱨ',
    'किलोमीटर': 'ᱠᱤᱞᱳᱢᱤᱴᱚᱨ', 'सेंटीमीटर': 'ᱥᱮᱸᱴᱤᱢᱤᱴᱚᱨ',
    'एकड़': 'ᱤᱠᱲ', 'बीघा': 'ᱵᱤᱜᱷᱟ',

    # ══ EDUCATION — EXTENDED ══════════════════════════════════════════════════
    'गणित': 'ᱜᱚᱱᱤᱛ', 'विज्ञान': 'ᱵᱤᱡ᱒ᱟᱱ',
    'इतिहास': 'ᱤᱛᱤᱦᱟᱥ', 'भूगोल': 'ᱵᱷᱩᱜᱳᱞ',
    'हिंदी': 'ᱦᱤᱸᱫᱤ', 'अंग्रेजी': 'ᱤᱸᱨᱮᱡ',
    'संताली': 'ᱥᱟᱱᱛᱟᱞᱤ', 'उर्दू': 'ᱩᱨᱫᱩ',
    'कक्षा': 'ᱠᱞᱟᱥ', 'पाठ': 'ᱯᱟᱴᱷ',
    'प्रश्न': 'ᱯᱨᱚᱥᱪᱱ', 'उत्तर': 'ᱩᱛᱛᱚᱨ',
    'पास': 'ᱯᱟᱥ', 'फेल': 'ᱯᱷᱮᱞ',
    'पुरस्कार': 'ᱯᱩᱨᱚᱥᱠᱟᱨ', 'प्रमाण पत्र': 'ᱯᱨᱚᱢᱟᱱ ᱯᱚᱛᱨ',
}


class TranslationEngine:
    """Main translation engine"""
    
    def __init__(self, dictionary_path=None):
        """Initialize translation engine
        
        Args:
            dictionary_path: Path to dictionary file (defaults to hindi_santali_final.csv)
        """
        # Use the actual dataset file in the project root
        # Priority: final (consolidated 3385+ entries) > master_v2 > master > enhanced > original
        if dictionary_path is None:
            import os
            # TRANSLATOR_ROOT is set by api/index.py for reliable Vercel path resolution.
            # Fall back to __file__-relative resolution for local runs.
            project_root = os.environ.get(
                'TRANSLATOR_ROOT',
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            )
            
            # Try final consolidated dataset first
            final_dataset = os.path.join(project_root, 'hindi_santali_final.csv')
            if os.path.exists(final_dataset):
                dictionary_path = final_dataset
            # Try master v2 dataset
            elif os.path.exists(os.path.join(project_root, 'hindi_santali_master_v2.csv')):
                dictionary_path = os.path.join(project_root, 'hindi_santali_master_v2.csv')
            # Try master v1 dataset
            elif os.path.exists(os.path.join(project_root, 'hindi_santali_master.csv')):
                dictionary_path = os.path.join(project_root, 'hindi_santali_master.csv')
            # Try enhanced dataset
            elif os.path.exists(os.path.join(project_root, 'hindi_santali_enhanced.csv')):
                dictionary_path = os.path.join(project_root, 'hindi_santali_enhanced.csv')
            # Try final merged dataset
            elif os.path.exists(os.path.join(project_root, 'hindi_santali_dataset_final.csv')):
                dictionary_path = os.path.join(project_root, 'hindi_santali_dataset_final.csv')
            # Fall back to original dataset
            else:
                dictionary_path = os.path.join(project_root, 'hindi_santali_dataset.csv')
        
        self.dictionary = Dictionary(dictionary_path)
        self.processor = TextProcessor()
        self.translation_cache = {}
        self.max_cache_size = 10000  # Limit cache to prevent memory issues
        # Force-overwrite with curated master list — our verified words always take
        # priority over potentially noisy/incorrect CSV data.
        for hindi, santali in SUPPLEMENTARY_HINDI_SANTALI.items():
            self.dictionary.add_word(hindi, santali)
        for hindi, santali in SUPPLEMENTARY_EXTENDED.items():
            self.dictionary.add_word(hindi, santali)
    
    def _transliterate_hindi_to_olchiki(self, hindi_text: str) -> str:
        """Transliterate Hindi text to Ol Chiki letter-by-letter
        
        Args:
            hindi_text: Hindi text to transliterate
            
        Returns:
            Ol Chiki text
        """
        result = []
        for char in hindi_text:
            if char in HINDI_OLCHIKI_MAP:
                result.append(HINDI_OLCHIKI_MAP[char])
            else:
                result.append(char)
        return ''.join(result)

    # Common Hindi suffixes ordered longest-first so specific forms match before generic
    _HINDI_SUFFIXES = [
        'ाओं', 'ियों', 'ियाँ', 'ाएँ', 'कर', 'ने', 'की', 'का', 'के',
        'में', 'से', 'पर', 'को', 'ता', 'ती', 'ते', 'ना', 'नी',
        'ाँ', 'ों', 'ें', 'ां', 'ा', 'ी', 'े', 'ो', 'ु', 'ू',
    ]

    def _stem_lookup(self, word: str) -> Optional[str]:
        """Try looking up a word after stripping common Hindi suffixes.
        Returns the Santali translation or None."""
        for suffix in self._HINDI_SUFFIXES:
            if word.endswith(suffix) and len(word) > len(suffix) + 1:
                stem = word[: -len(suffix)]
                result = self.dictionary.lookup_hindi_to_santali(stem)
                if result:
                    return result
                # Also check SUPPLEMENTARY directly (already injected, but belt+suspenders)
                result = SUPPLEMENTARY_HINDI_SANTALI.get(stem)
                if result:
                    return result
        return None

    
    
    def translate(self, text: str, source_lang='hi', target_lang='sat') -> Dict:
        """Translate text from Hindi to Santali
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Dictionary with translation results
        """
        # Normalize language codes - strip whitespace and convert to lowercase
        source_lang = str(source_lang).strip().lower() if source_lang else 'hi'
        target_lang = str(target_lang).strip().lower() if target_lang else 'sat'
        
        if not text or not text.strip():
            return {
                'success': False,
                'error': 'Empty input text',
                'source_text': text,
                'translated_text': '',
                'confidence': 0.0
            }
        
        # Check cache (limit cache size)
        cache_key = source_lang + "_" + target_lang + "_" + text
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        # Validate language pairs
        if not self._is_valid_language_pair(source_lang, target_lang):
            return {
                'success': False,
                'error': 'Unsupported language pair: {} -> {}'.format(source_lang, target_lang),
                'source_text': text,
                'translated_text': ''
            }
        
        # Process input
        cleaned_text = self.processor.preprocess(text)
                # Perform translation
        if source_lang == 'hi' and target_lang == 'sat':
            result = self._translate_hindi_to_santali(cleaned_text)
        elif source_lang == 'sat' and target_lang == 'hi':
            result = self._translate_santali_to_hindi(cleaned_text)
        elif source_lang == 'hi' and target_lang == 'en':
            result = self._translate_hindi_to_english(cleaned_text)
        elif source_lang == 'en' and target_lang == 'hi':
            result = self._translate_english_to_hindi(cleaned_text)
        else:
            result = {
                'success': False,
                'error': 'Translation not supported',
                'source_text': text,
                'translated_text': ''
            }
        
        # Cache result
        self.translation_cache[cache_key] = result
        
        return result
    
    def _translate_hindi_to_santali(self, hindi_text: str) -> Dict:
        """Translate Hindi text to Santali
        
        Args:
            hindi_text: Hindi text to translate
            
        Returns:
            Translation result dictionary
        """
        # First, try to match the entire text as a phrase
        full_phrase_match = self.dictionary.lookup_hindi_to_santali(hindi_text.strip())
        if full_phrase_match:
            return {
                'success': True,
                'source_text': hindi_text,
                'source_language': 'Hindi',
                'translated_text': full_phrase_match,
                'target_language': 'Santali',
                'confidence': 100.0,
                'method': 'exact_phrase_match',
                'word_mappings': [{
                    'hindi': hindi_text,
                    'santali': full_phrase_match,
                    'source': 'dictionary',
                    'confidence': 1.0
                }],
                'matched_words': 1,
                'total_words': 1
            }
        
        # If no full phrase match, proceed with sentence and word-by-word translation
        sentences = self.processor.tokenize_sentences(hindi_text)
        translated_sentences = []
        word_mappings = []
        total_confidence = 0.0
        matched_words = 0
        total_words = 0
        
        for sentence in sentences:
            words = self.processor.tokenize_words(sentence)
            translated_words = []
            i = 0
            
            while i < len(words):
                word = words[i]
                # Skip punctuation and special characters
                if not word or word in ['।', '॥', '.', ',', '!', '?', '-', ':', ';']:
                    translated_words.append(word)
                    i += 1
                    continue
                
                # Try multi-word phrases first (3-word, 2-word, then 1-word)
                translated_phrase = None
                phrase_length = 0
                
                # Try 3-word phrase
                if i + 2 < len(words):
                    three_word_phrase = ' '.join(words[i:i+3])
                    translated_phrase = self.dictionary.lookup_hindi_to_santali(three_word_phrase)
                    if translated_phrase:
                        phrase_length = 3
                
                # Try 2-word phrase if 3-word didn't match
                if not translated_phrase and i + 1 < len(words):
                    two_word_phrase = ' '.join(words[i:i+2])
                    translated_phrase = self.dictionary.lookup_hindi_to_santali(two_word_phrase)
                    if translated_phrase:
                        phrase_length = 2
                
                # If multi-word phrase matched, use it
                if translated_phrase and phrase_length > 0:
                    original_phrase = ' '.join(words[i:i+phrase_length])
                    translated_words.append(translated_phrase)
                    word_mappings.append({
                        'hindi': original_phrase,
                        'santali': translated_phrase,
                        'source': 'dictionary_phrase',
                        'confidence': 1.0
                    })
                    matched_words += phrase_length
                    total_words += phrase_length
                    i += phrase_length
                    continue
                
                # Try single word dictionary lookup (exact match first)
                translated_word = self.dictionary.lookup_hindi_to_santali(word)
                
                if translated_word:
                    translated_words.append(translated_word)
                    word_mappings.append({
                        'hindi': word,
                        'santali': translated_word,
                        'source': 'dictionary',
                        'confidence': 1.0
                    })
                    matched_words += 1
                    total_words += 1
                else:
                    # Try suffix-stripped stem lookup before fuzzy
                    stem_result = self._stem_lookup(word)
                    if stem_result:
                        translated_words.append(stem_result)
                        word_mappings.append({
                            'hindi': word,
                            'santali': stem_result,
                            'source': 'stem_match',
                            'confidence': 0.85
                        })
                        matched_words += 1
                        total_words += 1
                    else:
                        # Try fuzzy match as fallback (lowered threshold for better matching)
                        fuzzy_result = self.dictionary.fuzzy_match_hindi_to_santali(word, threshold=0.50)
                        if fuzzy_result:
                            translated_word, confidence = fuzzy_result
                            # Only use fuzzy match if confidence is high enough (>= 0.75)
                            if confidence >= 0.75:
                                translated_words.append(translated_word)
                                word_mappings.append({
                                    'hindi': word,
                                    'santali': translated_word,
                                    'source': 'fuzzy_match',
                                    'confidence': round(confidence, 2)
                                })
                                matched_words += 1
                                total_words += 1
                            else:
                                # Use Ol Chiki transliteration as graceful fallback (never show [word])
                                transliterated = self._transliterate_hindi_to_olchiki(word)
                                translated_words.append(transliterated)
                                word_mappings.append({
                                    'hindi': word,
                                    'santali': transliterated,
                                    'source': 'transliteration',
                                    'confidence': 0.3,
                                    'note': 'Phonetic transliteration (not in dictionary)'
                                })
                                total_words += 1
                        else:
                            # Use Ol Chiki transliteration as graceful fallback (never show [word])
                            transliterated = self._transliterate_hindi_to_olchiki(word)
                            translated_words.append(transliterated)
                            word_mappings.append({
                                'hindi': word,
                                'santali': transliterated,
                                'source': 'transliteration',
                                'confidence': 0.3,
                                'note': 'Phonetic transliteration (not in dictionary)'
                            })
                            total_words += 1
                
                i += 1
            
            translated_sentence = ' '.join(translated_words)
            translated_sentences.append(translated_sentence)
        
        translated_text = ' '.join(translated_sentences)
        confidence = (matched_words / total_words * 100) if total_words > 0 else 0
        
        return {
            'success': True,
            'source_text': hindi_text,
            'source_language': 'Hindi',
            'translated_text': translated_text,
            'target_language': 'Santali',
            'confidence': round(confidence, 2),
            'word_mappings': word_mappings,
            'matched_words': matched_words,
            'total_words': total_words
        }
    
    def _translate_santali_to_hindi(self, santali_text: str) -> Dict:
        """Translate Santali text to Hindi
        
        Args:
            santali_text: Santali text to translate
            
        Returns:
            Translation result dictionary
        """
        sentences = self.processor.tokenize_sentences(santali_text)
        translated_sentences = []
        word_mappings = []
        total_confidence = 0.0
        matched_words = 0
        total_words = 0
        
        for sentence in sentences:
            words = self.processor.tokenize_words(sentence)
            translated_words = []
            
            for word in words:
                # Skip punctuation and special characters
                if not word or word in ['।', '॥', '.', ',', '!', '?', '-', ':', ';']:
                    translated_words.append(word)
                    continue
                
                # Try dictionary lookup
                translated_word = self.dictionary.lookup_santali_to_hindi(word)
                
                if translated_word:
                    translated_words.append(translated_word)
                    word_mappings.append({
                        'santali': word,
                        'hindi': translated_word,
                        'source': 'dictionary',
                        'confidence': 1.0
                    })
                    matched_words += 1
                    total_words += 1
                else:
                    # Try fuzzy match as fallback
                    fuzzy_result = self.dictionary.fuzzy_match_santali_to_hindi(word, threshold=0.65)
                    if fuzzy_result:
                        translated_word, confidence = fuzzy_result
                        translated_words.append(translated_word)
                        word_mappings.append({
                            'santali': word,
                            'hindi': translated_word,
                            'source': 'fuzzy_match',
                            'confidence': round(confidence, 2)
                        })
                        matched_words += 1
                        total_words += 1
                    else:
                        # Keep original word if not found
                        translated_words.append(word)
                        word_mappings.append({
                            'santali': word,
                            'hindi': word,
                            'source': 'unknown',
                            'confidence': 0.0
                        })
                        total_words += 1
            
            translated_sentence = ' '.join(translated_words)
            translated_sentences.append(translated_sentence)
        
        translated_text = ' '.join(translated_sentences)
        confidence = (matched_words / total_words * 100) if total_words > 0 else 0
        
        return {
            'success': True,
            'source_text': santali_text,
            'source_language': 'Santali',
            'translated_text': translated_text,
            'target_language': 'Hindi',
            'confidence': round(confidence, 2),
            'word_mappings': word_mappings,
            'matched_words': matched_words,
            'total_words': total_words
        }
    
    def _is_valid_language_pair(self, source_lang, target_lang) -> bool:
        """Validate language pair"""
        valid_pairs = [
            ('hi', 'sat'),  # Hindi to Santali
            ('sat', 'hi'),  # Santali to Hindi
            ('hi', 'en'),   # Hindi to English
            ('en', 'hi'),   # English to Hindi
        ]
        return (source_lang, target_lang) in valid_pairs

    def _translate_hindi_to_english(self, hindi_text: str) -> Dict:
        """Translate Hindi text to English using built-in dictionary"""
        sentences = self.processor.tokenize_sentences(hindi_text)
        translated_sentences = []
        word_mappings = []
        matched_words = 0
        total_words = 0

        for sentence in sentences:
            words = self.processor.tokenize_words(sentence)
            translated_words = []
            i = 0
            while i < len(words):
                word = words[i]
                if not word or word in ['।', '॥', '.', ',', '!', '?', '-', ':', ';']:
                    translated_words.append(word)
                    i += 1
                    continue

                # Try 2-word phrase first
                if i + 1 < len(words):
                    phrase2 = words[i] + ' ' + words[i+1]
                    if phrase2 in HINDI_ENGLISH:
                        translated_words.append(HINDI_ENGLISH[phrase2])
                        word_mappings.append({'hindi': phrase2, 'english': HINDI_ENGLISH[phrase2], 'source': 'dictionary', 'confidence': 1.0})
                        matched_words += 2; total_words += 2; i += 2
                        continue

                # Single word
                en = HINDI_ENGLISH.get(word) or HINDI_ENGLISH.get(word.rstrip('ं').rstrip('ा'))
                if en:
                    translated_words.append(en)
                    word_mappings.append({'hindi': word, 'english': en, 'source': 'dictionary', 'confidence': 1.0})
                    matched_words += 1; total_words += 1
                else:
                    # Keep original Hindi word for unknowns (proper nouns etc)
                    translated_words.append(word)
                    word_mappings.append({'hindi': word, 'english': word, 'source': 'unknown', 'confidence': 0.0})
                    total_words += 1
                i += 1
            translated_sentences.append(' '.join(translated_words))

        translated_text = ' '.join(translated_sentences)
        confidence = (matched_words / total_words * 100) if total_words > 0 else 0
        return {
            'success': True,
            'source_text': hindi_text,
            'source_language': 'Hindi',
            'translated_text': translated_text,
            'target_language': 'English',
            'confidence': round(confidence, 2),
            'word_mappings': word_mappings,
            'matched_words': matched_words,
            'total_words': total_words
        }

    def _translate_english_to_hindi(self, english_text: str) -> Dict:
        """Translate English text to Hindi using built-in dictionary"""
        words = english_text.lower().split()
        translated_words = []
        word_mappings = []
        matched_words = 0
        total_words = len(words)

        i = 0
        while i < len(words):
            word = words[i].strip('.,!?;:')
            # Try 2-word phrase
            if i + 1 < len(words):
                phrase2 = word + ' ' + words[i+1].strip('.,!?;:')
                if phrase2 in ENGLISH_HINDI:
                    hi = ENGLISH_HINDI[phrase2]
                    translated_words.append(hi)
                    word_mappings.append({'english': phrase2, 'hindi': hi, 'source': 'dictionary', 'confidence': 1.0})
                    matched_words += 2; i += 2
                    continue
            hi = ENGLISH_HINDI.get(word)
            if hi:
                translated_words.append(hi)
                word_mappings.append({'english': word, 'hindi': hi, 'source': 'dictionary', 'confidence': 1.0})
                matched_words += 1
            else:
                translated_words.append(words[i])
                word_mappings.append({'english': words[i], 'hindi': words[i], 'source': 'unknown', 'confidence': 0.0})
            i += 1

        translated_text = ' '.join(translated_words)
        confidence = (matched_words / total_words * 100) if total_words > 0 else 0
        return {
            'success': True,
            'source_text': english_text,
            'source_language': 'English',
            'translated_text': translated_text,
            'target_language': 'Hindi',
            'confidence': round(confidence, 2),
            'word_mappings': word_mappings,
            'matched_words': matched_words,
            'total_words': total_words
        }
    
    def _find_partial_match(self, word: str) -> Optional[str]:
        """Find partial match for a word in dictionary
        
        Args:
            word: Word to find partial match for
            
        Returns:
            Translated word or None
        """
        word_lower = word.lower()
        all_words = self.dictionary.get_all_words()
        
        # Check if word is substring of any key
        for hindi_word, santali_word in all_words.items():
            if word_lower == hindi_word.lower()[:len(word_lower)] or \
               hindi_word.lower() == word_lower[:len(hindi_word)]:
                return santali_word
        
        return None
    
    def batch_translate(self, texts: list, source_lang='hi', target_lang='sat') -> list:
        """Translate multiple texts
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            List of translation results
        """
        results = []
        for text in texts:
            result = self.translate(text, source_lang, target_lang)
            results.append(result)
        return results
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages
        
        Returns:
            Dictionary of language codes and names
        """
        return {
            'hi': 'Hindi',
            'sat': 'Santali'
        }
    
    def clear_cache(self):
        """Clear translation cache"""
        self.translation_cache.clear()
