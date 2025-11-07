import spacy
import json
import os
import lemminflect

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load spelling variants from /assets/
assets_path = os.path.join(os.path.dirname(__file__), "..", "assets", "spellingVariants.json")
with open(assets_path, "r") as f:
    variants = json.load(f)

def convert_variant(word, locale="us"):
    doc = nlp(word)
    token = doc[0]
    lemma = token.lemma_.lower()

    if lemma in variants:
        base = variants[lemma][locale]
        # Inflect the base word to match the original token's tag
        inflected = nlp(base)[0]._.inflect(token.tag_)
        return inflected if inflected else base
    return word

# Example usage
if __name__ == "__main__":
    words = ["colour", "colours", "visualised", "organising", "honour"]
    converted = [convert_variant(w, locale="us") for w in words]
    print(converted)
