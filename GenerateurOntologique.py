import os
import json
import requests
from tqdm import tqdm
import time
import openai

# ---------- CONFIGURATION ----------
OPENAI_API_KEY = ""  # Mets ta clé directe ici
openai.api_key = OPENAI_API_KEY

API_URL = "https://philo-lycee.fr/api/dictionnaire.php?id="
OUTFILE = "concepts_ontologie.json"

types_relations = [
    "IMPLIQUE", "CONTREDIT", "EST_EQUIVALENT", "EST_UN", "FAIT_PARTIE_DE",
    "A_COMME_PROPRIETE", "CAUSE", "PERMET", "EMPECHE", "DEFINIT", "EXPLIQUE",
    "ATTESTE", "PRECEDE", "SUIT", "S_OPPOSE_A", "COMPLEMENTE", "SUBSUME",
    "EST_ANALOGUE_A", "DEPEND_DE", "EST_COMPOSE_DE", "NECESSITE", "POSSIBLE_SI",
    "INSTANCE_DE", "CONSTITUE", "VISE", "MEMBRE_DE", "IDENTIQUE_A", "PERSONNALISEE"
]

# ---------- EXPLICATIONS DES RELATIONS ----------
relation_explications = {
    "implique": "Relation d'implication logique ou conceptuelle : ce concept entraîne nécessairement ou logiquement un autre.",
    "contredit": "Relation de contradiction : ce concept est incompatible ou s'oppose logiquement à un autre.",
    "est_équivalent": "Relation d'équivalence : ce concept a la même signification ou valeur qu'un autre.",
    "est_un": "Relation d'appartenance à une catégorie (is_a) : ce concept est un exemple ou un cas particulier d'une catégorie plus générale.",
    "fait_partie_de": "Relation de méronomie (part_of) : ce concept est une partie constituante d'un tout.",
    "a_comme_propriété": "Relation attributive : ce concept possède une propriété ou caractéristique particulière.",
    "cause": "Relation causale : ce concept produit ou engendre un autre concept.",
    "permet": "Relation d'activation ou de permission : ce concept rend possible ou facilite un autre concept.",
    "empêche": "Relation d'empêchement ou d'inhibition : ce concept rend impossible ou bloque un autre concept.",
    "définit": "Relation de définition : ce concept sert à définir ou à préciser un autre concept.",
    "explique": "Relation d'explication : ce concept éclaire ou justifie un autre concept.",
    "atteste": "Relation d'évidence ou de preuve : ce concept sert de preuve ou d'indication pour un autre concept.",
    "précède": "Relation temporelle ou logique de précédence : ce concept vient avant un autre dans le temps ou la logique.",
    "suit": "Relation temporelle ou logique de succession : ce concept vient après un autre dans le temps ou la logique.",
    "s'oppose_à": "Relation d'opposition ou d'antagonisme : ce concept est en tension ou en conflit avec un autre.",
    "complémente": "Relation de complémentarité : ce concept complète ou s'associe harmonieusement à un autre concept.",
    "subsombe": "Relation de subsomption : ce concept englobe, contient ou subsume une catégorie de concepts plus spécifiques.",
    "est_analogue_à": "Relation d'analogie ou de similarité : ce concept présente des ressemblances ou une structure comparable à un autre.",
    "dépend_de": "Relation de dépendance : ce concept n'existe ou ne fonctionne qu'en relation avec un autre.",
    "est_composé_de": "Relation de composition : ce concept est constitué de plusieurs éléments ou parties.",
    "nécessite": "Relation de nécessité : ce concept requiert absolument un autre pour exister ou fonctionner.",
    "possible_si": "Relation de possibilité conditionnelle : ce concept n'est réalisable que si un autre est présent ou réalisé.",
    "instance_de": "Relation d'instanciation : ce concept est un cas particulier ou un exemple concret d'une catégorie.",
    "constitue": "Relation de constitution : ce concept forme la base ou la substance d'un autre concept.",
    "vise": "Relation de finalité, de but (téléologie) : ce concept tend vers un objectif ou une fin.",
    "membre_de": "Relation d'appartenance à un ensemble/groupe : ce concept appartient à un groupe ou une collection.",
    "identique_a": "Relation d'identité : ce concept est exactement le même qu'un autre.",
    "personnalisée": "Pour toute relation spécifique non prévue dans la liste des relations standards.",
}

# ---------- FONCTIONS UTILES ----------
def get_mot_def(id):
    """Récupère le mot et la définition pour un id donné."""
    try:
        r = requests.get(API_URL + str(id))
        data = r.json()
        if data.get('success'):
            return data['mot'], data['defmot']
        else:
            return None, None
    except Exception:
        return None, None

def openai_concepts(mot, definition, relation, explication):
    """Demande à OpenAI des concepts reliés via une relation donnée, explication incluse."""
    system = (
        "Tu es un expert en philosophie. Pour chaque relation conceptuelle proposée, "
        "donne entre 5 et 10 concepts français UNIQUEMENT EN MAJUSCULES, séparés par des virgules, "
        "qui sont liés au mot selon la relation, sans explication. Un concept = 1 mot."
    )
    prompt = (
        f"Mot : {mot}\n"
        f"Définition : {definition}\n"
        f"Relation : {relation}\n"
        f"Explication de la relation : {explication}\n"
        "Quels concepts sont liés à ce mot par cette relation ?"
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # ou un autre si tu as le budget pour ;) mais prof bon voilà quoi...
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        text = response.choices[0].message.content.strip()
        # Nettoyage : liste de concepts
        concepts = [c.strip() for c in text.replace('.', '').split(',') if c.strip()]
        return concepts
    except Exception as e:
        print(f"Erreur OpenAI : {e}")
        return []

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------- SCRIPT PRINCIPAL ----------
def main(start_id=471, end_id=6120):
    data = load_json(OUTFILE)

    for idx in tqdm(range(start_id, end_id + 1)):
        if str(idx) in data:
            continue  # Déjà traité

        mot, definition = get_mot_def(idx)
        if not mot:
            continue

        entry = {
            "mot": mot,
            "definition": definition,
            "relations": {}
        }

        for relation in types_relations:
            # La clé du dictionnaire d'explication doit être en minuscules et sans accent pour la cohérence
            relation_key = relation.lower().replace("é", "e").replace("à", "a").replace("è", "e").replace("ê", "e").replace("ù", "u").replace("û", "u").replace("ç", "c").replace("'", "_").replace(" ", "_")
            explication = relation_explications.get(relation_key, "")
            concepts = openai_concepts(mot, definition, relation, explication)
            entry["relations"][relation] = {
                "explication": explication,
                "concepts": concepts
            }
            time.sleep(1.3)  # Pour éviter le rate limit

        data[str(idx)] = entry
        save_json(data, OUTFILE)
        time.sleep(1)  # Être gentil avec l’API

if __name__ == "__main__":
    main()  # Tu peux changer les bornes pour tester sur moins de mots