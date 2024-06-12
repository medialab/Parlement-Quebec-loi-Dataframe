import re
import sys
import csv
import json
import nltk.data
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
from transformers import pipeline
from tensorflow.python.framework.errors_impl import InvalidArgumentError as TensorFlowError


NUMERO = sys.argv[1]

thresholds = [0.9, 0.925, 0.95, 0.96, 0.97, 0.98, 0.99]

# prepare XML versions with:
# ls Jour-*.pdf | while read f; do pdftohtml -xml $f; done

with open("Jour-%s.xml" % NUMERO) as f:
    xml = f.read()


# Remove everything not debate:

xml = xml.split("<i>(Fin de la séance")[0]
xml = xml.split("Journal des débats</b></text>")[-1]

fulltext = ""
re_clean_balises = re.compile(r"<\/?[a-z][^>]*>", re.I)
for line in xml.split("\n"):
    if ' font="1">' not in line:
        continue
    line = re_clean_balises.sub("", line)
    fulltext = fulltext.strip() + " " + line.strip()

re_clean_edits = re.compile(r"\s*&lt;[^&]*&gt;\s*")
fulltext = re_clean_edits.sub(" ", fulltext.strip())


sentencer = nltk.data.load('tokenizers/punkt/french.pickle')
tokenizer = AutoTokenizer.from_pretrained("tblard/tf-allocine")
model = TFAutoModelForSequenceClassification.from_pretrained("tblard/tf-allocine")
sentiment = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)

init_counts = lambda _: {
    "total": 0,
    "positive": 0,
    "negative": 0
}
counts = {}
for t in thresholds:
    counts[t] = init_counts(t)

with open("Jour-%s_sentiment.csv" % NUMERO, "w") as f:
    writer = csv.writer(f)
    writer.writerow(["Jour", "Phrase", "Position", "Score"])
    for sent in sentencer.tokenize(fulltext):
        # Do not analyse sentences with only one word
        if " " not in sent:
            continue
        try:
            analysis = sentiment(sent)
        except TensorFlowError:
            continue
        for t in thresholds:
            counts[t]["total"] +=1
            if analysis[0]["score"] > t:
                counts[t][analysis[0]["label"].lower()] += 1
        if analysis[0]["score"] > 0.9:
            writer.writerow([NUMERO, sent, analysis[0]["label"], analysis[0]["score"]])
            print(analysis, sent)
            print()

with open("Jour-%s_sentiment_scores.csv" % NUMERO, "w") as f:
    writer = csv.writer(f)
    writer.writerow(["Jour", "Seuil", "Nb phrases", "Nb Positif", "% Positif", "Nb Négatif", "% Négatif"])
    for t in thresholds:
        writer.writerow([NUMERO, t, counts[t]["total"], counts[t]["positive"], 100 * counts[t]["positive"] / counts[t]["total"], counts[t]["negative"], 100 * counts[t]["negative"] / counts[t]["total"]])
