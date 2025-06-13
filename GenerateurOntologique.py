import os
import json
import requests
from tqdm import tqdm
import time
import openai
import sys

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
    COLOR = True
except ImportError:
    COLOR = False

def cprint(text, color=None, bold=False, end="\n"):
    if COLOR:
        c = getattr(Fore, color.upper(), "") if color else ""
        b = Style.BRIGHT if bold else ""
        print(f"{b}{c}{text}{Style.RESET_ALL}", end=end)
    else:
        print(text, end=end)

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
    "est_equivalent": "Relation d'équivalence : ce concept a la même signification ou valeur qu'un autre.",
    "est_un": "Relation d'appartenance à une catégorie (is_a) : ce concept est un exemple ou un cas particulier d'une catégorie plus générale.",
    "fait_partie_de": "Relation de méronomie (part_of) : ce concept est une partie constituante d'un tout.",
    "a_comme_propriete": "Relation attributive : ce concept possède une propriété ou caractéristique particulière.",
    "cause": "Relation causale : ce concept produit ou engendre un autre concept.",
    "permet": "Relation d'activation ou de permission : ce concept rend possible ou facilite un autre concept.",
    "empeche": "Relation d'empêchement ou d'inhibition : ce concept rend impossible ou bloque un autre concept.",
    "definit": "Relation de définition : ce concept sert à définir ou à préciser un autre concept.",
    "explique": "Relation d'explication : ce concept éclaire ou justifie un autre concept.",
    "atteste": "Relation d'évidence ou de preuve : ce concept sert de preuve ou d'indication pour un autre concept.",
    "precede": "Relation temporelle ou logique de précédence : ce concept vient avant un autre dans le temps ou la logique.",
    "suit": "Relation temporelle ou logique de succession : ce concept vient après un autre dans le temps ou la logique.",
    "s_oppose_a": "Relation d'opposition ou d'antagonisme : ce concept est en tension ou en conflit avec un autre.",
    "complemente": "Relation de complémentarité : ce concept complète ou s'associe harmonieusement à un autre concept.",
    "subsume": "Relation de subsomption : ce concept englobe, contient ou subsume une catégorie de concepts plus spécifiques.",
    "est_analogue_a": "Relation d'analogie ou de similarité : ce concept présente des ressemblances ou une structure comparable à un autre.",
    "depend_de": "Relation de dépendance : ce concept n'existe ou ne fonctionne qu'en relation avec un autre.",
    "est_compose_de": "Relation de composition : ce concept est constitué de plusieurs éléments ou parties.",
    "necessite": "Relation de nécessité : ce concept requiert absolument un autre pour exister ou fonctionner.",
    "possible_si": "Relation de possibilité conditionnelle : ce concept n'est réalisable que si un autre est présent ou réalisé.",
    "instance_de": "Relation d'instanciation : ce concept est un cas particulier ou un exemple concret d'une catégorie.",
    "constitue": "Relation de constitution : ce concept forme la base ou la substance d'un autre concept.",
    "vise": "Relation de finalité, de but (téléologie) : ce concept tend vers un objectif ou une fin.",
    "membre_de": "Relation d'appartenance à un ensemble/groupe : ce concept appartient à un groupe ou une collection.",
    "identique_a": "Relation d'identité : ce concept est exactement le même qu'un autre.",
    "personnalisee": "Pour toute relation spécifique non prévue dans la liste des relations standards.",
}

# ---------- PARAMÈTRES DE COÛT OPENAI ----------
COST_PER_1M_INPUT = 1.10  # $/1M tokens input
COST_PER_1M_OUTPUT = 4.40  # $/1M tokens output
AVG_INPUT_TOKENS = 300  # estimation grossière par requête
AVG_OUTPUT_TOKENS = 50  # estimation grossière par requête

def estimate_cost_per_request():
    input_cost = (AVG_INPUT_TOKENS / 1_000_000) * COST_PER_1M_INPUT
    output_cost = (AVG_OUTPUT_TOKENS / 1_000_000) * COST_PER_1M_OUTPUT
    return input_cost + output_cost

def format_time(seconds):
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        m, s = divmod(int(seconds), 60)
        return f"{m}m{s:02d}s"
    else:
        h, rem = divmod(int(seconds), 3600)
        m, s = divmod(rem, 60)
        return f"{h}h{m:02d}m{s:02d}s"

def format_cost(cost):
    return f"{cost:.4f} $"

# ---------- FONCTIONS UTILES ----------
def get_mot_def(id):
    """Récupère le mot et la définition pour un id donné."""
    cprint(f"⏳ Récupération du mot et de la définition pour l'id {id}...", "cyan")
    try:
        r = requests.get(API_URL + str(id))
        data = r.json()
        if data.get('success'):
            cprint(f"✅ Mot trouvé : {data['mot']}", "green")
            return data['mot'], data['defmot']
        else:
            cprint(f"❌ Aucun mot trouvé pour l'id {id}.", "red")
            return None, None
    except Exception as e:
        cprint(f"⚠️ Erreur lors de la récupération de l'id {id} : {e}", "red")
        return None, None

def openai_concepts(mot, definition, relation, explication):
    """Demande à OpenAI des concepts reliés via une relation donnée, explication incluse."""
    cprint(f"🧠 Appel OpenAI pour '{mot}' - relation '{relation}'...", "magenta")
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
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        text = response.choices[0].message.content.strip()
        concepts = [c.strip() for c in text.replace('.', '').split(',') if c.strip()]
        cprint(f"   → Concepts trouvés : {', '.join(concepts)}", "yellow")
        return concepts
    except Exception as e:
        cprint(f"⚠️ Erreur OpenAI : {e}", "red")
        return []

def ollama_concepts(mot, definition, relation, explication, model="llama3.1:latest"):
    """Demande à Ollama des concepts reliés via une relation donnée, explication incluse."""
    cprint(f"🧠 (Ollama) Appel pour '{mot}' - relation '{relation}'...", "magenta")
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
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        data = response.json()
        # Ollama renvoie 'message' ou 'messages'
        if "message" in data:
            text = data["message"]["content"].strip()
        elif "messages" in data and data["messages"]:
            text = data["messages"][-1]["content"].strip()
        else:
            text = ""
        concepts = [c.strip() for c in text.replace('.', '').split(',') if c.strip()]
        cprint(f"   → Concepts trouvés (Ollama) : {', '.join(concepts)}", "yellow")
        return concepts
    except Exception as e:
        cprint(f"⚠️ Erreur Ollama : {e}", "red")
        return []

def load_json(filename):
    if os.path.exists(filename):
        cprint(f"📂 Chargement du fichier existant : {filename}", "cyan")
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    cprint(f"🆕 Aucun fichier existant, création d'un nouveau dictionnaire.", "cyan")
    return {}

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    cprint(f"💾 Sauvegarde dans {filename}", "green")

def print_separator():
    cprint("-" * 60, "blue")

# ---------- GLOBAL OLLAMA FLAG ----------
OLLAMA = True  # Peut être modifié manuellement ici (True/False)

# ---------- SCRIPT PRINCIPAL ----------
def main(start_id=471, end_id=6120, use_ollama=False, ollama_model="llama3.1:latest"):
    global OLLAMA
    # Priorité à la valeur manuelle si modifiée, sinon celle du CLI
    if OLLAMA is not None:
        use_ollama = OLLAMA
    OLLAMA = use_ollama
    cprint("=== Générateur Ontologique Philosophie ===", "blue", bold=True)
    cprint(f"Traitement des IDs de {start_id} à {end_id}", "blue")
    print_separator()
    data = load_json(OUTFILE)
    total = end_id - start_id + 1
    already = sum(1 for idx in range(start_id, end_id + 1) if str(idx) in data)
    cprint(f"{already}/{total} déjà traités. Début du traitement...", "cyan")
    print_separator()

    ids_to_process = [idx for idx in range(start_id, end_id + 1) if str(idx) not in data]
    nb_relations = len(types_relations)
    total_requests = len(ids_to_process) * nb_relations
    cost_per_req = estimate_cost_per_request()
    total_cost_est = total_requests * cost_per_req

    if not use_ollama:
        cprint(f"💸 Coût estimé total pour ce run : {format_cost(total_cost_est)}", "magenta", bold=True)
    else:
        cprint(f"🦙 Mode Ollama activé (modèle : {ollama_model}) — Pas de coût estimé, usage local gratuit.", "green", bold=True)
    print_separator()

    start_time = time.time()
    processed_requests = 0

    for idx_pos, idx in enumerate(tqdm(ids_to_process, desc="Concepts", ncols=100)):
        mot, definition = get_mot_def(idx)
        if not mot:
            cprint(f"⏩ Passage de l'id {idx} (mot non trouvé).", "red")
            continue

        entry = {
            "mot": mot,
            "definition": definition,
            "relations": {}
        }

        for rel_pos, relation in enumerate(types_relations):
            relation_key = relation.lower().replace("é", "e").replace("à", "a").replace("è", "e").replace("ê", "e").replace("ù", "u").replace("û", "u").replace("ç", "c").replace("'", "_").replace(" ", "_")
            explication = relation_explications.get(relation_key, "")
            cprint(f"🔗 [{mot}] Relation : {relation}", "blue")
            if explication:
                cprint(f"   Explication : {explication}", "cyan")
            else:
                cprint("   (Pas d'explication trouvée pour cette relation)", "red")

            req_start = time.time()
            if use_ollama:
                concepts = ollama_concepts(mot, definition, relation, explication, model=ollama_model)
            else:
                concepts = openai_concepts(mot, definition, relation, explication)
            req_end = time.time()
            req_duration = req_end - req_start

            entry["relations"][relation] = {
                "explication": explication,
                "concepts": concepts
            }

            processed_requests += 1
            elapsed = time.time() - start_time
            avg_time_per_req = elapsed / processed_requests if processed_requests else 0.0
            remaining_requests = total_requests - processed_requests
            est_time_left = avg_time_per_req * remaining_requests
            est_cost_left = remaining_requests * cost_per_req

            cprint(f"   ⏱️ Temps pour cette requête : {format_time(req_duration)}", "cyan")
            if not use_ollama:
                cprint(f"   💸 Coût de cette requête : {format_cost(cost_per_req)}", "magenta")
                cprint(f"   ⏳ Temps estimé restant : {format_time(est_time_left)}", "yellow")
                cprint(f"   💰 Coût total estimé restant : {format_cost(est_cost_left)}", "yellow", bold=True)
            else:
                cprint(f"   ⏳ Temps estimé restant : {format_time(est_time_left)}", "yellow")

            cprint("   Pause pour éviter le rate limit...", "magenta")
            time.sleep(1.3)

        data[str(idx)] = entry
        save_json(data, OUTFILE)
        cprint("   Petite pause avant le prochain mot...", "magenta")
        print_separator()
        time.sleep(1)

        tqdm.write(
            f"🟦 Progression : {processed_requests}/{total_requests} requêtes | "
            f"Temps écoulé : {format_time(elapsed)} | "
            f"Temps restant estimé : {format_time(est_time_left)}"
            + (f" | Coût restant estimé : {format_cost(est_cost_left)}" if not use_ollama else "")
        )

    cprint("🎉 Traitement terminé !", "green", bold=True)
    cprint(f"Tous les résultats sont dans {OUTFILE}", "green")
    print_separator()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Générateur Ontologique Philosophie (CLI)")
    parser.add_argument("--start", type=int, default=471, help="ID de début (défaut: 471)")
    parser.add_argument("--end", type=int, default=6120, help="ID de fin (défaut: 6120)")
    parser.add_argument("--outfile", type=str, default=OUTFILE, help="Fichier de sortie JSON")
    parser.add_argument("--ollama", action="store_true", help="Utiliser Ollama local (llama3.1:latest)")
    parser.add_argument("--ollama-model", type=str, default="llama3.1:latest", help="Nom du modèle Ollama (défaut: llama3.1:latest)")
    args = parser.parse_args()

    OUTFILE = args.outfile

    main(
        start_id=args.start,
        end_id=args.end,
        use_ollama=args.ollama,
        ollama_model=args.ollama_model
    )