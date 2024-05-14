# Construire un tableau séparant les intervention
# Reprise de l'identification des intervenants du script process_crs

import pandas as pd
import re
from pprint import pprint

def extract_intervention(text):
    """
    Extraire les interventions d'un texte
    """
    # Nettoyage
    text = text.replace("Haut de la page", "")

    # Retrait des répétitions entre < >
    text = re.sub(r"\s*<[^<>]*>\s*", " ", text)
    text = re.sub(r"\s*<[^<>]*(\n[^<>]*)*\n[^<>]*>\s*", " ", text, re.M)

    # Fin du CR
    text = text.split("(Fin de la séance")[0]

    # Début du CR
    text = text.split("Journal des débats")[-1]
    # Extraire tous les noms du document
    noms=[]
    for i in text.split("\n"):
        a = re.findall(r"^([ML][.eam]+ [A-Z][^:]{4,35} :)", i)
        noms+=a

    # Marquer les balises au début des noms
    text_modified = text
    for nom in list(set(noms)):
        text_modified = text_modified.replace(nom, "<intervention>" + nom + "<start>")

    # Construction d'un corpus des interventions
    corpus = []
    for i in text_modified.split("<intervention>")[1:]: # couper aux interventions
        try:
            tmp = i.split("<start>") # séparer le nom de l'intervention
            corpus.append([tmp[0],tmp[1]])
        except:
            print("error", tmp)

    return pd.DataFrame(corpus, columns=["nom","intervention"])

# application sur l'ensemble du corpus
total = {}
for i in range(1,21):
    with open("Jour-%s.txt" % i,"r") as f:
        text = f.read()
    total[f"jour{i}"] = extract_intervention(text)
corpus = pd.concat(total)
corpus.to_csv("corpus_total_interventions.csv")