import sys
import re
import csv
import json
from pprint import pprint

NB_TO_METRIQUE = {
  "nb_suspensions": "nombre de suspensions",
  "votes_par_consentement": "votes par consentement",
  "votes_par_mise_aux_voix": "votes par mise aux voix",
  "amendements_adoptes": "amendements adoptés",
  "amendements_rejetes": "amendements rejetés",
  "nb_intervenants": "nombre d'intervenants",
  "nb_interventions_secretaire": "interventions secrétaire",
  "nb_interventions_fonctionnaire": "interventions fonctionnaire",
  "nb_interventions_ministre": "interventions ministre",
  "nb_interventions_gouvernement": "interventions gouvernement",
  "nb_interventions_opposition": "interventions opposition",
  "nb_interventions_presidence": "interventions présidence",
  "nb_interventions_PLQ": "interventions PLQ",
  "nb_interventions_QS": "interventions QS",
  "nb_interventions_PQ": "interventions PQ"
}

rows = []
rows_breakdown = []
for NUMERO in range(1, 20):
    with open("Jour-%s.csv" % NUMERO) as f:
        reader = csv.DictReader(f)
        for row in reader:
          rows.append(row)
          # nb_suspensions,votes_par_consentement,votes_par_mise_aux_voix,amendements_adoptes,amendements_rejetes,nb_intervenants,nb_interventions_secretaire,nb_interventions_fonctionnaire,nb_interventions_ministre,nb_interventions_gouvernement,nb_interventions_opposition,nb_interventions_presidence,nb_interventions_PLQ,nb_interventions_QS,nb_interventions_PQ
          for key, value in NB_TO_METRIQUE.items():
            
            rows_breakdown.append({
              "jour": NUMERO,
              "metrique": value,
              "valeur": int(row[key])
            })

with open('donnees-aggregees-tous-jours.csv', 'w', newline='') as csvfile:
    fieldnames = rows[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

with open('donnees-aggregees-tous-jours-categoriees.csv', 'w', newline='') as csvfile:
    fieldnames = rows_breakdown[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_breakdown)