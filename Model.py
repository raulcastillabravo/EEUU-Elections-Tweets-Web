import tensorflow as tf

import pandas as pd
import numpy as np
import emoji
import re
import string

import nltk
from nltk import wordpunct_tokenize
from nltk.corpus import stopwords
from nltk import word_tokenize   
from nltk.corpus import stopwords

class Model:

    def __init__(self, path):
        self.model = tf.keras.models.load_model(path)

    def custom_standardization(self, text):
        """
        Standardize a tensor of strings by applying the 
        following rules:
            - Lower case the text.
            - Remove line breaks.
            - Remove URLs.
            - Remove emojis.
            - Remove punctuation.
        
        Return
        ------
        np.ndarray of decoded strings.
        
        """
        
        # Lower case
        lower_text = tf.strings.lower(text)

        # Remove line breaks
        lower_text = tf.strings.regex_replace(input=lower_text, 
                                            pattern='\n', 
                                            rewrite=' ')

        # Remove URLs
        free_url_text = tf.strings.regex_replace(input=lower_text, 
                                                pattern="http\S+", 
                                                rewrite=' ')

        # Remove emojis
        emoji_pattern = emoji.get_emoji_regexp().pattern
        emoji_pattern = emoji_pattern.replace('#','') # There is a # emoji
        free_emoji_text = tf.strings.regex_replace(input=free_url_text, 
                                                pattern='[%s]' % re.escape(emoji_pattern),
                                                rewrite=' ')

        # Remove punctuation
        # punctuation_pattern = string.punctuation.replace('#', '').replace('@','').replace("\'", '')
        punctuation_pattern = string.punctuation
        free_punctuation_text =  tf.strings.regex_replace(free_emoji_text,
                                                        '[%s]' % re.escape(punctuation_pattern),
                                                        ' ')
        return free_punctuation_text.numpy()
    
    def is_english(self, text):
        """
        Calculate probability of given text to be written in several languages and
        return a dictionary that looks like {'french': 2, 'spanish': 4, 'english': 0}
        
        @param text: Text whose language want to be detected
        @type text: str
        
        @return: Dictionary with languages and unique stopwords seen in analyzed text
        @rtype: dict
        """

        languages_ratios = {}

        '''
        nltk.wordpunct_tokenize() splits all punctuations into separate tokens
        
        >>> wordpunct_tokenize("That's thirty minutes away. I'll be there in ten.")
        ['That', "'", 's', 'thirty', 'minutes', 'away', '.', 'I', "'", 'll', 'be', 'there', 'in', 'ten', '.']
        '''
        
        tokens = wordpunct_tokenize(text)
        words = [word.lower() for word in tokens]

        # Compute per language included in nltk number of unique stopwords appearing in analyzed text
        for language in stopwords.fileids():
            stopwords_set = set(stopwords.words(language))
            words_set = set(words)
            common_elements = words_set.intersection(stopwords_set)

            languages_ratios[language] = len(common_elements) # language "score"
        
        most_rated_language = max(languages_ratios, key=languages_ratios.get)
        
        return most_rated_language == 'english'

    def predict(self, tweet):
        standardized_tweet = self.custom_standardization(tweet)
        standardized_tweet = standardized_tweet.decode()
        
        if not self.is_english(standardized_tweet):
            return None
        
        prediction = self.model.predict([standardized_tweet])

        return int(prediction  >= 0)


