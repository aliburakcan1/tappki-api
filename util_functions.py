import re
from loguru import logger

def lower_turkish_chars(self):
    self = re.sub(r"İ", "i", self)
    self = re.sub(r"I", "ı", self)
    self = re.sub(r"Ç", "ç", self)
    self = re.sub(r"Ş", "ş", self)
    self = re.sub(r"Ü", "ü", self)
    self = re.sub(r"Ğ", "ğ", self)
    self = self.lower() # for the rest use default lower
    return self

## This part is a total unfortunate. Sorry for that.
profanity_words = ['sik', 'göt', 'zenci', 'ibne', 'piç', 'orospu', 'sıç', 'yarak', 'amcık', 'amk']

# The words starting with profanity words are censored.
# Capital letters are kept as they are.
def censor_profanity(sentence):
    words = sentence.split()
    clean_words = []
    for word in words:
        for profanity_word in profanity_words:
            if lower_turkish_chars(word).startswith(profanity_word):
                # Put a star in the middle of the word
                clean_words.append(word[0] + "*" + word[2:] if len(word) > 2 else word[0] + "*")
                break
        else:
            clean_words.append(word)
    return " ".join(clean_words)
