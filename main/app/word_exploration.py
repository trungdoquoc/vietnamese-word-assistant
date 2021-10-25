"""
PURPOSE: Apply statistical methods to extract new word by reading both
A) normalized_text file and B) .json look-up dict
RESULT: .pkl DataFrame file for user_query.py
"""

import pandas as pd
import json

normalized_text_path = './extracted_data/processed_text_file'

def translate_normalized_word(normalized_word):
    """
    GOAL: translate normalized word back to normal word
    by look up .json dict file
    eg: thuy1 -> thuỷ
    """

    return
