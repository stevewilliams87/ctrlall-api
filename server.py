from flask import Flask, request, jsonify
import spacy
import json
import os
import lemminflect

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

# Load spelling variants
assets_path = os.path.join(os.path.dirname(__file__), "..", "assets", "images", "spellingVariants.json")
with open(assets_path, "r") as f:
    variants = json.load(f)

def convert_variant(word, locale="us"):
    doc = nlp(word)
    token = doc[0]
    lemma = token.lemma_.lower()
    if lemma in variants:
        base = variants[lemma][locale]
        inflected = nlp(base)[0]._.inflect(token.tag_)
        return inflected if inflected else base
    return word

@app.route("/convert", methods=["POST"])
def convert():
    data = request.json
    words = data.get("words", [])
    locale = data.get("locale", "us")
    converted = [convert_variant(w, locale) for w in words]
    return jsonify({"converted": converted})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
