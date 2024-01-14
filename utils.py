#!/usr/bin/env python
# -*- coding: utf-8 -*-


def process_text(text, stop_list):
    import re
    from nltk.tokenize import word_tokenize

    # Use a single regex to remove numbers and punctuation, and normalize whitespace
    text = re.sub(r'\d+|[^\w\s]|[\r\n\t]| +', ' ', text)
    # Lowercase and tokenize the text
    tokens = word_tokenize(text.lower())
    # Filter out stop words
    filtered_tokens = [word for word in tokens if word not in stop_list]
    return " ".join(filtered_tokens)


