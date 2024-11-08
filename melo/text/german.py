import pickle
import os
import re
from g2p_de import G2p  # This is a placeholder; use a German g2p library

from . import symbols

from .german_utils.abbreviations import expand_abbreviations
from .german_utils.time_norm import expand_time_german
from .german_utils.number_norm import normalize_numbers
from .japanese import distribute_phone  # If needed for phoneme distribution

from transformers import AutoTokenizer

current_file_path = os.path.dirname(__file__)
GERMAN_DICT_PATH = os.path.join(current_file_path, "german_utils/germandict.rep")
CACHE_PATH = os.path.join(current_file_path, "germandict_cache.pickle")
_g2p = G2p()  

arpa = {
    # Consonants
    "p", "b", "t", "d", "k", "ɡ", "f", "v", "s", "z", "ʃ", "ʒ", "ç", "x", "h",
    "pf", "ts", "tʃ", "m", "n", "ŋ", "l", "ʁ", "j", "ʋ", "w",

    # Vowels
    "i", "iː", "y", "yː", "u", "uː", "e", "eː", "ø", "øː", "o", "oː",
    "ɛ", "ɛː", "œ", "ɔ", "a", "aː", "ə", "ɐ", "ɪ", "ʊ", "ʏ",

    # Diphthongs
    "aɪ", "aʊ", "ɔʏ",

    # Additional Symbols
    "ʔ", "ɜ"
}


def post_replace_ph(ph):
    # Map for specific replacements, mainly for punctuation or non-phonetic symbols.
    rep_map = {
        "：": ",",
        "；": ",",
        "，": ",",
        "。": ".",
        "！": "!",
        "？": "?",
        "\n": ".",
        "·": ",",
        "、": ",",
        "...": "…",
        "v": "V",  # Example of a specific replacement
        "–": "-",
    }

    # Replace based on the map if the phoneme exists in the map
    ph = rep_map.get(ph, ph)

    # If ph is a valid phoneme or a replacement from the map, return it as-is.
    # Only convert to "UNK" if it's genuinely unrecognized, like a non-phonetic symbol.
    return ph if ph != "" else "UNK"

import re

def read_dict():
    g2p_dict = {}
    start_line = 0  # Adjust if you want to start processing earlier
    with open(GERMAN_DICT_PATH, encoding="utf-8") as f:
        line = f.readline()
        line_index = 1
        while line:
            if line_index >= start_line:
                line = line.strip()

                # Split using spaces or tabs, and handle common variations in transcription files
                word_split = re.split(r"\s{2,}|\t+", line)
                
                # Ensure there are exactly two parts (word and phonetic transcription)
                if len(word_split) == 2:
                    word = word_split[0].strip().upper()
                    transcription = word_split[1].strip()
                    
                    # Handle cases where the transcription contains unexpected characters like '?'
                    transcription = transcription.replace("?", "")
                    syllable_split = transcription.split(" - ")
                    
                    # Convert each phoneme group to a list
                    g2p_dict[word] = [s.split() for s in syllable_split]
                else:
                    print(f"Skipping malformed line {line_index}: {line}")

            line_index += 1
            line = f.readline()

    return g2p_dict


def cache_dict(g2p_dict, file_path):
    with open(file_path, "wb") as pickle_file:
        pickle.dump(g2p_dict, pickle_file)

def get_dict():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "rb") as pickle_file:
            g2p_dict = pickle.load(pickle_file)
    else:
        g2p_dict = read_dict()
        cache_dict(g2p_dict, CACHE_PATH)

    return g2p_dict

#eng_dict = get_dict()

def refine_ph(phn):
    tone = 0
    if re.search(r"\d$", phn):
        tone = int(phn[-1]) + 1
        phn = phn[:-1]
    return phn.lower(), tone

def text_normalize(text):
    text = text.lower()
    text = expand_time_german(text)
    text = normalize_numbers(text)
    text = expand_abbreviations(text)
    return text

model_id = 'dbmdz/bert-base-german-europeana-cased'
tokenizer = AutoTokenizer.from_pretrained(model_id)

def g2p(text, pad_start_end=True, tokenized=None):

    
    if tokenized is None:
        tokenized = tokenizer.tokenize(text)
    phs = []
    ph_groups = []
    for t in tokenized:
        if not t.startswith("#"):
            ph_groups.append([t])
        else:
            ph_groups[-1].append(t.replace("#", ""))
    
    phones = []
    tones = []
    word2ph = []
    for group in ph_groups:
        w = "".join(group)
        phone_len = 0
        word_len = len(group)
        
        # Use the g2p_de model directly for phoneme conversion
        phone_list = _g2p(w)
       
        for ph in phone_list:
            if ph in arpa:
                ph, tn = refine_ph(ph)
                phones.append(ph)
                tones.append(tn)
            else:
                phones.append(ph)
                tones.append(0)
            phone_len += 1
        
        # Map word lengths to phoneme lengths
        word2ph += distribute_phone(phone_len, word_len)
    
    # Replace special symbols and finalize
    phones = [post_replace_ph(i) for i in phones]

    # Optionally add start and end padding
    if pad_start_end:
        phones = ["_"] + phones + ["_"]
        tones = [0] + tones + [0]
        word2ph = [1] + word2ph + [1]
    
    return phones, tones, word2ph


def get_bert_feature(text, word2ph, device=None):
    from text import german_bert

    return german_bert.get_bert_feature(text, word2ph, device=device)
