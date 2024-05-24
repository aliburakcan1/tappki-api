import re

# This function is a total unfortunate. Sorry for that.
def censor_profanity(s):
    profanity = ['sik', 'göt', 'zenci', 'ibne', 'piç', 'orospu', 'sıç', 'yarak', 'amcık', 'amk']

    for word in profanity:
        replacement = word[0:round(len(word)/2)] + "*" + word[round(len(word)/2)+1:]
        s = re.sub(word, replacement, s, flags=re.IGNORECASE)

    return s