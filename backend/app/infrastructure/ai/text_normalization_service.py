"""
infrastructure/ai/text_normalization_service.py — Text Normalization Service
"""

from __future__ import annotations

import re
import string


class TextNormalizationService:
    """
    Cleans, tokenizes, and lemmatizes text for synonym-aware keyword matching.
    """

    def lemmatize_word(self, word: str) -> str:
        """
        Applies basic rule-based stemming/lemmatization to convert plurals,
        verb forms, and common suffixes to their root forms.
        """
        word = word.lower().strip()
        if not word:
            return ""

        # Suffix/verb root mapping dictionary
        manual_map = {
            "orbiting": "orbit",
            "revolving": "revolve",
            "revolves": "revolve",
            "revolved": "revolve",
            "orbits": "orbit",
            "orbited": "orbit",
            "pumps": "pump",
            "pumping": "pump",
            "pumped": "pump",
            "filters": "filter",
            "filtering": "filter",
            "filtered": "filter",
            "leaves": "leaf",
            "doing": "do",
            "does": "do",
            "did": "do",
            "done": "do",
            "going": "go",
            "goes": "go",
            "went": "go",
            "gone": "go",
            "having": "have",
            "has": "have",
            "had": "have",
            "making": "make",
            "makes": "make",
            "made": "make",
            "using": "use",
            "uses": "use",
            "used": "use",
            "producing": "produce",
            "produces": "produce",
            "produced": "produce",
            "releasing": "release",
            "releases": "release",
            "released": "release",
            "delivering": "deliver",
            "delivers": "deliver",
            "delivered": "deliver",
            "removing": "remove",
            "removes": "remove",
            "removed": "remove",
            "pulled": "pull",
            "pulling": "pull",
            "pulls": "pull",
            "keeps": "keep",
            "keeping": "keep",
            "kept": "keep",
            "falls": "fall",
            "falling": "fall",
            "fell": "fall",
            "states": "state",
            "stating": "state",
            "stated": "state",
            "follows": "follow",
            "following": "follow",
            "followed": "follow",
            "performing": "perform",
            "performs": "perform",
            "performed": "perform",
        }

        if word in manual_map:
            return manual_map[word]

        # Rule-based suffix transformations
        # Noun Plurals (singularization)
        if word.endswith("sses"):
            return word[:-2]
        if word.endswith("ies") and len(word) > 4:
            return word[:-3] + "y"
        if word.endswith("es") and len(word) > 4:
            # e.g., branches -> branch, boxes -> box, matches -> match
            if word.endswith("sches") or word.endswith("shes") or word.endswith("xes") or word.endswith("ches"):
                return word[:-2]
            return word[:-1]
        if word.endswith("s") and not word.endswith("ss") and len(word) > 2:
            return word[:-1]

        # Verb forms -ing
        if word.endswith("ing") and len(word) > 5:
            # Check double consonant e.g., running -> run
            if len(word) > 6 and word[-4] == word[-5] and word[-4] in "bdfglmnprst":
                return word[:-4]
            return word[:-3]

        # Verb forms -ed
        if word.endswith("ed") and len(word) > 4:
            if word.endswith("ied"):
                return word[:-3] + "y"
            # e.g., created -> create
            if word.endswith("ated") or word.endswith("uted") or word.endswith("ited") or word.endswith("eted"):
                return word[:-1]
            return word[:-2]

        return word

    def normalize_text(self, text: str) -> list[str]:
        """
        Normalizes a string: lowercases, strips punctuation, tokenizes, and lemmatizes.
        Returns a list of root tokens.
        """
        if not text:
            return []

        # Convert to lowercase
        text = text.lower()

        # Remove punctuation, replacing with spaces to keep word boundaries
        translator = str.maketrans(string.punctuation, " " * len(string.punctuation))
        cleaned = text.translate(translator)

        # Split into tokens
        tokens = cleaned.split()

        # Lemmatize each word
        normalized_tokens = [self.lemmatize_word(w) for w in tokens if w.strip()]
        return normalized_tokens
