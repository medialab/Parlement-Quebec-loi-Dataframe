import sys
import re
import csv
import json
from pprint import pprint


NUMERO = sys.argv[1]

with open("Jour-%s.txt" % NUMERO) as f:
    text = f.read()


# Nettoyage
text = text.replace("Haut de la page", "")

# Retrait des répétitions entre < >
text = re.sub(r"\s*<[^<>]*>\s*", " ", text)
text = re.sub(r"\s*<[^<>]*(\n[^<>]*)*\n[^<>]*>\s*", " ", text, re.M)

# Fin du CR
text = text.split("(Fin de la séance")[0]

# Début du CR
text = text.split("Journal des débats")[-1]


segments = []

new_segment = lambda : {
    "debut": "",
    "fin": "",
    "debats": "",
    "nb_suspensions": 0,
    "votes_par_consentement": 0,
    "votes_par_mise_aux_voix": 0,
    "amendements_adoptes": 0,
    "amendements_rejetes": 0,
    "intervenants": [],
    "nb_intervenants": 0,
    "nb_interventions_secretaire": 0,
    "nb_interventions_fonctionnaire": 0,
    "nb_interventions_ministre": 0,
    "nb_interventions_gouvernement": 0,
    "nb_interventions_opposition": 0,
    "nb_interventions_presidence": 0
}
current = new_segment()

def type_intervenant(interv):
    if "Président" in interv:
        return "presidence"
    if "Secrétaire" in interv:
        return "secretaire"
    if "Miville" in interv:
        return "fonctionnaire"
    if interv == "M. Caire":
        return "ministre"
    if interv in ["M. Barrette", "M. Birnbaum", "M. Tanguay", "M. Nadeau-Dubois", "M. Zanetti", "Mme Hivon", "M. Ouellet"]:
        return "opposition"
    if interv in ["M. Lévesque (Chapleau)", "M. Lemieux", "M. Martel", "M. Lefebvre", "M. Provençal", "M. Poulin", "Mme D'Amours", "Mme Lavallée", "Mme Boutin", "M. Tremblay", "M. Lamothe", "M. Asselin", "M. Caron", "Mme Lachance"]:
        return "gouvernement"
    print("WARNING: un intervenant ne semble pas correct: %s" % interv,file=sys.stderr)
    return ""


re_match_heure = re.compile(r"(\d+)\s+h\s+(\d*)")
re_match_inter = re.compile(r"^([ML][.eam]+ [A-Z][^:]{4,35}) :")
for line in text.split("\n"):
    # TODO : identifier suspensions/reprises
    # (Suspension de la séance à 10 h 02)
    # (Reprise à 15 h 51)
    if "(Suspension de la séance" in line:
        current["nb_suspensions"] += 1

    # Détection des créneaux temporels
    matches = re_match_heure.search(line)
    if matches:
        heure = matches.group(1) + ":" + (matches.group(2) or "00");
        if not current:
            current["debut"] = heure
        else:
            current["fin"] = heure
            segments.append(current)
            current = new_segment()
            current["debut"] = heure

    # TODO : gérer heure de fin de la séance "(Fin de la séance à 19 heures)"

    current["debats"] += line.strip() + " "

    match_inter = re_match_inter.search(line)
    if match_inter and not any(match_inter.group(1).startswith(x) for x in ["La CAI", "La Pinière", "Le Québec", "Le Jeune Barreau"]):
        current["intervenants"].append(match_inter.group(1))
        current["nb_intervenants"] += 1
        current["nb_interventions_%s" % type_intervenant(match_inter.group(1))] += 1

    # TODO Détection réactions
    # Une voix :
    # Des voix :

segments.append(current)

# Détection des procédures de vote
for segment in segments:
    segment["votes_par_consentement"] = len(re.findall("Président \(M. Bachand\) ?:[^:]*consentement(\.| est adopté)", segment["debats"], re.I))
    searchable_text = segment["debats"].replace("Mme la secrétaire, y a-t-il", "XXX")
    segment["votes_par_mise_aux_voix"] = len(re.findall("Mme la secrétaire", searchable_text, re.I))

    segment["amendements_adoptes"] = len(re.findall(r"amendement[^.]* est adopté", segment["debats"], re.I))
    segment["amendements_rejetes"] = len(re.findall(r"amendement[^.]* est rejeté", segment["debats"], re.I))
    #del(segment["debats"])

    # TODO: décompte amendements adoptes/rejetes

with open("Jour-%s.json" % NUMERO, "w") as f:
    json.dump(segments, f)

headers = list(new_segment().keys())
headers.remove("debats")
headers.remove("intervenants")

with open("Jour-%s.csv" % NUMERO, "w") as f:
    writer = csv.writer(f)
    writer.writerow(["jour"] + headers)
    for s in segments:
        writer.writerow([NUMERO] + [s[h] for h in headers])

full_seance = new_segment()
full_seance["jour"] = NUMERO
stats_headers = headers[2:]
for s in segments:
    for h in stats_headers:
        full_seance[h] += s[h]

with open("Jour-%s-summary.csv" % NUMERO, "w") as f:
    writer = csv.writer(f)
    writer.writerow(["jour"] + stats_headers)
    writer.writerow([NUMERO] + [full_seance[h] for h in stats_headers])



# TODO write output data
# - viz ?


