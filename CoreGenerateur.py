import json
from enum import Enum
from collections import defaultdict, Counter
import re
import string

class TypeRelation(Enum):
    IMPLIQUE = "implique"
    CONTREDIT = "contredit"
    EST_EQUIVALENT = "est_équivalent"
    EST_UN = "est_un"
    FAIT_PARTIE_DE = "fait_partie_de"
    A_COMME_PROPRIETE = "a_comme_propriété"
    CAUSE = "cause"
    PERMET = "permet"
    EMPECHE = "empêche"
    DEFINIT = "définit"
    EXPLIQUE = "explique"
    ATTESTE = "atteste"
    PRECEDE = "précède"
    SUIT = "suit"
    S_OPPOSE_A = "s'oppose_à"
    COMPLEMENTE = "complémente"
    SUBSUME = "subsombe"
    EST_ANALOGUE_A = "est_analogue_à"
    DEPEND_DE = "dépend_de"
    EST_COMPOSE_DE = "est_composé_de"
    NECESSITE = "nécessite"
    POSSIBLE_SI = "possible_si"
    INSTANCE_DE = "instance_de"
    CONSTITUE = "constitue"
    VISE = "vise"
    MEMBRE_DE = "membre_de"
    IDENTIQUE_A = "identique_à"
    PERSONNALISEE = "personnalisée"

def clean_concept(concept):
    """Nettoie et normalise les concepts."""
    if not isinstance(concept, str):
        return None
    
    # Enlever les caractères indésirables et normaliser
    concept = concept.strip().upper()
    
    # Enlever les prefixes comme "LA ", "LE ", "LES ", etc.
    concept = re.sub(r'^(LA |LE |LES |L\'|UN |UNE |DES |DU |DE LA |DE L\')', '', concept)
    
    # Enlever les phrases explicatives qui commencent par des mots comme "VOICI"
    if any(phrase in concept for phrase in ['VOICI', 'CONCEPTS LIÉS', 'EST EXPLIQUÉ PAR', 'SONT :', 'PAR LA RELATION']):
        return None
    
    # Enlever les concepts trop longs (probablement des descriptions)
    if len(concept) > 50:
        return None
    
    # Enlever les concepts vides ou avec des caractères spéciaux indésirables
    if not concept or concept in ['', ' '] or '\n' in concept:
        return None
    
    # Enlever les concepts qui contiennent deux espaces (pas forcement consécutifs)
    if '  ' in concept:
        return None
    
    # Enleer les concepts qui contiennent un espace ET qui font plus de 22 caractères
    if ' ' in concept and len(concept) > 22:
        return None
    
    # Enlever les concepts qui sont juste des mots de liaison
    if concept in ['ET', 'OU', 'DONC', 'MAIS', 'CAR', 'PUIS', 'ALORS']:
        return None
    
    return concept

def normalize_relation_key(relation_key):
    """Normalise les clés de relations pour correspondre à l'enum."""
    mapping = {
        'IMPLIQUE': 'IMPLIQUE',
        'CONTREDIT': 'CONTREDIT', 
        'EST_EQUIVALENT': 'EST_EQUIVALENT',
        'EST_UN': 'EST_UN',
        'FAIT_PARTIE_DE': 'FAIT_PARTIE_DE',
        'A_COMME_PROPRIETE': 'A_COMME_PROPRIETE',
        'CAUSE': 'CAUSE',
        'PERMET': 'PERMET',
        'EMPECHE': 'EMPECHE',
        'DEFINIT': 'DEFINIT',
        'EXPLIQUE': 'EXPLIQUE',
        'ATTESTE': 'ATTESTE',
        'PRECEDE': 'PRECEDE',
        'SUIT': 'SUIT',
        'S_OPPOSE_A': 'S_OPPOSE_A',
        'COMPLEMENTE': 'COMPLEMENTE',
        'SUBSUME': 'SUBSUME',
        'EST_ANALOGUE_A': 'EST_ANALOGUE_A',
        'DEPEND_DE': 'DEPEND_DE',
        'EST_COMPOSE_DE': 'EST_COMPOSE_DE',
        'NECESSITE': 'NECESSITE',
        'POSSIBLE_SI': 'POSSIBLE_SI',
        'INSTANCE_DE': 'INSTANCE_DE',
        'CONSTITUE': 'CONSTITUE',
        'VISE': 'VISE',
        'MEMBRE_DE': 'MEMBRE_DE',
        'IDENTIQUE_A': 'IDENTIQUE_A',
        'PERSONNALISEE': 'PERSONNALISEE'
    }
    return mapping.get(relation_key, relation_key)

def extract_ontology_from_json(json_file_path, min_concept_frequency=2):
    """Extrait l'ontologie depuis le fichier JSON."""
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Dictionnaires pour stocker les données
    all_concepts = Counter()
    all_relations = set()
    
    # Parcourir toutes les entrées
    for entry_id, entry_data in data.items():
        mot_principal = entry_data.get('mot', '').strip().upper()
        
        if mot_principal:
            all_concepts[mot_principal] += 10  # Poids plus élevé pour les mots principaux
        
        # Parcourir les relations
        relations = entry_data.get('relations', {})
        for relation_type, relation_data in relations.items():
            if 'concepts' not in relation_data:
                continue
                
            relation_type_normalized = normalize_relation_key(relation_type)
            
            # Parcourir les concepts liés
            for concept in relation_data['concepts']:
                concept_clean = clean_concept(concept)
                if concept_clean and concept_clean != mot_principal:
                    if ' ' in concept_clean:
                        sous_concepts = [c for c in concept_clean.split(' ') if c]
                        for sous_concept in sous_concepts:
                            all_concepts[sous_concept] += 1
                            try:
                                relation_enum = TypeRelation[relation_type_normalized]
                                all_relations.add((mot_principal, relation_enum, sous_concept))
                            except KeyError:
                                print(f"Relation inconnue: {relation_type_normalized}")
                    else:
                        all_concepts[concept_clean] += 1
                        try:
                            relation_enum = TypeRelation[relation_type_normalized]
                            all_relations.add((mot_principal, relation_enum, concept_clean))
                        except KeyError:
                            print(f"Relation inconnue: {relation_type_normalized}")
    
    # Filtrer les concepts par fréquence
    core_concepts = {concept for concept, count in all_concepts.items() 
                    if count >= min_concept_frequency}
    
    # Filtrer les relations pour ne garder que celles avec des concepts fréquents ET valides
    core_relations = [
        (src, rel, dst) for src, rel, dst in all_relations
        if src in core_concepts and dst in core_concepts and is_valid_concept(src) and is_valid_concept(dst)
    ]
    
    return core_concepts, core_relations, all_concepts

def generate_python_code(core_concepts, core_relations, concept_frequencies, output_file):
    """Génère le code Python avec les constantes."""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("from enum import Enum\n\n")
        
        # Écrire l'enum TypeRelation
        f.write("class TypeRelation(Enum):\n")
        for rel in TypeRelation:
            f.write(f'    {rel.name} = "{rel.value}"\n')
        f.write("\n\n")
        
        # Écrire CORE_PHILOSOPHICAL_CONCEPTS comme un set
        f.write("CORE_PHILOSOPHICAL_CONCEPTS = {\n")
        
        # Trier les concepts par ordre alphabétique et filtrer les concepts vides, trop courts ou non pertinents
        sorted_concepts = sorted(
            c for c in core_concepts
            if c and len(c) > 1 and any(ch.isalpha() for ch in c) and is_valid_concept(c)
        )
        
        # Formater avec 4 concepts par ligne pour une meilleure lisibilité
        for i, concept in enumerate(sorted_concepts):
            if i % 4 == 0 and i > 0:
                f.write("\n")
            if i % 4 == 0:
                f.write("    ")
            f.write(f'"{concept}"')
            if i < len(sorted_concepts) - 1:
                f.write(", ")
            if (i + 1) % 4 != 0 and i < len(sorted_concepts) - 1:
                f.write(" ")
        
        f.write("\n}\n\n")
        
        # Écrire CORE_RELATIONS
        f.write("CORE_RELATIONS = [\n")
        
        # Trier les relations en utilisant une clé personnalisée
        unique_relations = list(set(core_relations))
        sorted_relations = sorted(unique_relations, key=lambda x: (x[0], x[1].name, x[2]))
        
        for src, rel, dst in sorted_relations:
            f.write(f'    ("{src}", TypeRelation.{rel.name}, "{dst}"),\n')
        f.write("]\n\n")
        
        # Statistiques en commentaires
        f.write(f"# Statistiques:\n")
        f.write(f"# Nombre de concepts: {len(core_concepts)}\n")
        f.write(f"# Nombre de relations: {len(unique_relations)}\n")
        f.write(f"# \n")
        f.write(f"# Concepts les plus fréquents:\n")
        for concept, freq in sorted(concept_frequencies.items(), key=lambda x: x[1], reverse=True)[:15]:
            if concept in core_concepts:
                f.write(f"# - {concept}: {freq}\n")

STOP_WORDS = {
    "ET", "OU", "DONC", "MAIS", "CAR", "PUIS", "ALORS", "SI", "IL", "AU", "AUX", "DU", "DE", "DES", "EN", "UN", "UNE", "LE", "LA", "LES", "CE", "CET", "CETTE", "SON", "SA", "SES", "SUR", "PAR", "POUR", "AVEC", "SANS", "DANS", "SOUS", "VERS", "CHEZ", "FAUT"
}

def is_valid_concept(concept):
    # Exclure si dans la liste des stop words
    if concept in STOP_WORDS:
        return False
    # Exclure si commence/termine par un guillemet ou parenthèse
    if concept.startswith('"') or concept.endswith('"'):
        return False
    if concept.startswith('(') or concept.endswith('(') or concept.endswith(')'):
        return False
    # Exclure si contient des caractères non alphanumériques (hors espace et tiret)
    allowed = set(string.ascii_uppercase + " -")
    if not all(c in allowed or c.isalpha() for c in concept):
        return False
    # Exclure si moins de 2 lettres
    if sum(1 for c in concept if c.isalpha()) < 2:
        return False
    return True

def main():
    # Remplacez par le chemin vers votre fichier JSON
    json_file_path = "votre_base_donnees.json"  # Changez ce chemin
    output_file = "ontologie_generee.py"
    
    print("Extraction de l'ontologie depuis le JSON...")
    core_concepts, core_relations, concept_frequencies = extract_ontology_from_json(
        json_file_path, min_concept_frequency=2
    )
    
    print(f"Concepts extraits: {len(core_concepts)}")
    print(f"Relations extraites: {len(core_relations)}")
    
    print("Génération du code Python...")
    generate_python_code(core_concepts, core_relations, concept_frequencies, output_file)
    
    print(f"Ontologie générée dans {output_file}")
    
    # Afficher quelques statistiques
    print("\nTop 15 des concepts les plus fréquents:")
    for concept, freq in sorted(concept_frequencies.items(), key=lambda x: x[1], reverse=True)[:15]:
        if concept in core_concepts:
            print(f"  {concept}: {freq}")
    
    print(f"\nTypes de relations utilisées:")
    relation_types = Counter([rel.name for _, rel, _ in core_relations])
    for rel_type, count in relation_types.most_common():
        print(f"  {rel_type}: {count}")

if __name__ == "__main__":
    main()