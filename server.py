from flask import Flask, request, jsonify
import spacy
import json
import os
import lemminflect
from collections import defaultdict

app = Flask(__name__)

@app.route("/")
def home():
    return "API is running"

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load base spelling variants
assets_path = os.path.join(os.path.dirname(__file__), "spellingVariants.json")
with open(assets_path, "r") as f:
    variants = json.load(f)

# Convert a single word using lemma + inflection
def convert_variant(word, locale="us"):
    doc = nlp(word)
    token = doc[0]
    lemma = token.lemma_.lower()
    if lemma in variants:
        base = variants[lemma][locale]
        inflected = nlp(base)[0]._.inflect(token.tag_)
        return inflected if inflected else base
    return word

# POST endpoint for converting a list of words
@app.route("/convert", methods=["POST"])
def convert():
    data = request.json
    words = data.get("words", [])
    locale = data.get("locale", "us")
    converted = [convert_variant(w, locale) for w in words]
    return jsonify({"converted": converted})

# GET endpoint to return full inflected dictionary
@app.route("/api/spelling-variants")
def get_spelling_variants():
    inflected_dict = defaultdict(dict)

    for lemma, forms in variants.items():
        for locale in ["us", "gb"]:
            base = forms[locale]
            doc = nlp(base)
            token = doc[0]

            # Generate common inflections
            inflections: set[str] = set()
            inflections.add(base)

            # Add plural manually for adjectives like "colour"
            if base.endswith("our") and locale == "gb":
                inflections.add(base + "s")  # e.g., colours
            elif base.endswith("or") and locale == "us":
                inflections.add(base + "s")  # e.g., colors

            for tag in ["NNS", "VBD", "VBG", "VBN", "VBZ"]:
                inflected = token._.inflect(tag)
                if inflected:
                    inflections.add(inflected)

            for form in inflections:
                inflected_dict[form.lower()][locale] = form

    return jsonify(inflected_dict)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
