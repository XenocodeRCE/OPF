from enum import Enum
from collections import defaultdict, Counter
import itertools
import sys
import os
import importlib.util

# Importer le module ontologie_generee
spec = importlib.util.spec_from_file_location("ontologie_generee", os.path.join(os.path.dirname(__file__), "ontologie_generee.py"))
ontologie_generee = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ontologie_generee)

# UTILISER la TypeRelation du module original au lieu de la redéfinir !
TypeRelation = ontologie_generee.TypeRelation
CORE_RELATIONS = ontologie_generee.CORE_RELATIONS

class LogicalInferenceEngine:
    
    def __init__(self, relations):
        """
        Initialise le moteur d'inférence avec une liste de relations.
        relations: liste de tuples (source, TypeRelation, destination)
        """
        self.relations = set(relations)
        self.relation_graph = defaultdict(lambda: defaultdict(set))
        self.build_graph()
    
    def build_graph(self):
        """Construit un graphe des relations pour faciliter les recherches."""
        self.relation_graph.clear()
        
        for src, rel, dst in self.relations:
            self.relation_graph[src][rel].add(dst)
    
    def relation_exists(self, src, rel, dst):
        """Vérifie si une relation existe déjà."""
        return (src, rel, dst) in self.relations
    
    def apply_transitive_rules(self):
        """Applique les règles de transitivité avec les relations existantes."""
        new_relations = set()
        print("Application des règles de transitivité...")
        # Règle 1: Transitivité de IMPLIQUE
        count = 0
        for concept_a in self.relation_graph:
            if TypeRelation.IMPLIQUE in self.relation_graph[concept_a]:
                for concept_b in self.relation_graph[concept_a][TypeRelation.IMPLIQUE]:
                    if concept_b in self.relation_graph and TypeRelation.IMPLIQUE in self.relation_graph[concept_b]:
                        for concept_c in self.relation_graph[concept_b][TypeRelation.IMPLIQUE]:
                            # OPTIMISATION: accès direct à self.relations (évite l'appel de fonction)
                            if concept_c != concept_a and (concept_a, TypeRelation.IMPLIQUE, concept_c) not in self.relations:
                                new_relations.add((concept_a, TypeRelation.IMPLIQUE, concept_c))
                                count += 1
                                if count <= 5:
                                    print(f"    Nouveau: {concept_a} IMPLIQUE {concept_c} (via {concept_b})")
        print(f"  IMPLIQUE transitif: {count} nouvelles relations")
        # Règle 2: Transitivité de EST_UN
        count = 0
        for concept_a in self.relation_graph:
            if TypeRelation.EST_UN in self.relation_graph[concept_a]:
                for concept_b in self.relation_graph[concept_a][TypeRelation.EST_UN]:
                    if concept_b in self.relation_graph and TypeRelation.EST_UN in self.relation_graph[concept_b]:
                        for concept_c in self.relation_graph[concept_b][TypeRelation.EST_UN]:
                            if concept_c != concept_a and (concept_a, TypeRelation.EST_UN, concept_c) not in self.relations:
                                new_relations.add((concept_a, TypeRelation.EST_UN, concept_c))
                                count += 1
                                if count <= 5:
                                    print(f"    Nouveau: {concept_a} EST_UN {concept_c} (via {concept_b})")
        print(f"  EST_UN transitif: {count} nouvelles relations")
        # Règle 3: Transitivité de FAIT_PARTIE_DE
        count = 0
        for concept_a in self.relation_graph:
            if TypeRelation.FAIT_PARTIE_DE in self.relation_graph[concept_a]:
                for concept_b in self.relation_graph[concept_a][TypeRelation.FAIT_PARTIE_DE]:
                    if concept_b in self.relation_graph and TypeRelation.FAIT_PARTIE_DE in self.relation_graph[concept_b]:
                        for concept_c in self.relation_graph[concept_b][TypeRelation.FAIT_PARTIE_DE]:
                            if concept_c != concept_a and (concept_a, TypeRelation.FAIT_PARTIE_DE, concept_c) not in self.relations:
                                new_relations.add((concept_a, TypeRelation.FAIT_PARTIE_DE, concept_c))
                                count += 1
                                if count <= 5:
                                    print(f"    Nouveau: {concept_a} FAIT_PARTIE_DE {concept_c} (via {concept_b})")
        print(f"  FAIT_PARTIE_DE transitif: {count} nouvelles relations")
        # Règle 4: Transitivité de PRECEDE
        count = 0
        for concept_a in self.relation_graph:
            if TypeRelation.PRECEDE in self.relation_graph[concept_a]:
                for concept_b in self.relation_graph[concept_a][TypeRelation.PRECEDE]:
                    if concept_b in self.relation_graph and TypeRelation.PRECEDE in self.relation_graph[concept_b]:
                        for concept_c in self.relation_graph[concept_b][TypeRelation.PRECEDE]:
                            if concept_c != concept_a and (concept_a, TypeRelation.PRECEDE, concept_c) not in self.relations:
                                new_relations.add((concept_a, TypeRelation.PRECEDE, concept_c))
                                count += 1
                                if count <= 5:
                                    print(f"    Nouveau: {concept_a} PRECEDE {concept_c} (via {concept_b})")
        print(f"  PRECEDE transitif: {count} nouvelles relations")
        # Règle 5: Transitivité de CAUSE
        count = 0
        for concept_a in self.relation_graph:
            if TypeRelation.CAUSE in self.relation_graph[concept_a]:
                for concept_b in self.relation_graph[concept_a][TypeRelation.CAUSE]:
                    if concept_b in self.relation_graph and TypeRelation.CAUSE in self.relation_graph[concept_b]:
                        for concept_c in self.relation_graph[concept_b][TypeRelation.CAUSE]:
                            if concept_c != concept_a and (concept_a, TypeRelation.CAUSE, concept_c) not in self.relations:
                                new_relations.add((concept_a, TypeRelation.CAUSE, concept_c))
                                count += 1
                                if count <= 5:
                                    print(f"    Nouveau: {concept_a} CAUSE {concept_c} (via {concept_b})")
        print(f"  CAUSE transitif: {count} nouvelles relations")
        return new_relations
    
    def apply_equivalence_rules(self):
        """Applique les règles d'équivalence et symétrie."""
        new_relations = set()
        print("Application des règles d'équivalence...")
        # Règle 6: Symétrie de EST_EQUIVALENT
        count = 0
        for concept_a in self.relation_graph:
            if TypeRelation.EST_EQUIVALENT in self.relation_graph[concept_a]:
                for concept_b in self.relation_graph[concept_a][TypeRelation.EST_EQUIVALENT]:
                    if (concept_b, TypeRelation.EST_EQUIVALENT, concept_a) not in self.relations:
                        new_relations.add((concept_b, TypeRelation.EST_EQUIVALENT, concept_a))
                        count += 1
                        if count <= 5:
                            print(f"    Nouveau: {concept_b} EST_EQUIVALENT {concept_a}")
        print(f"  EST_EQUIVALENT symétrique: {count} nouvelles relations")
        # Règle 7: Transitivité de EST_EQUIVALENT
        count = 0
        for concept_a in self.relation_graph:
            if TypeRelation.EST_EQUIVALENT in self.relation_graph[concept_a]:
                for concept_b in self.relation_graph[concept_a][TypeRelation.EST_EQUIVALENT]:
                    if concept_b in self.relation_graph and TypeRelation.EST_EQUIVALENT in self.relation_graph[concept_b]:
                        for concept_c in self.relation_graph[concept_b][TypeRelation.EST_EQUIVALENT]:
                            if concept_c != concept_a and (concept_a, TypeRelation.EST_EQUIVALENT, concept_c) not in self.relations:
                                new_relations.add((concept_a, TypeRelation.EST_EQUIVALENT, concept_c))
                                count += 1
                                if count <= 5:
                                    print(f"    Nouveau: {concept_a} EST_EQUIVALENT {concept_c} (via {concept_b})")
        print(f"  EST_EQUIVALENT transitif: {count} nouvelles relations")
        # Règle 8: Symétrie de IDENTIQUE_A
        count = 0
        for concept_a in self.relation_graph:
            if TypeRelation.IDENTIQUE_A in self.relation_graph[concept_a]:
                for concept_b in self.relation_graph[concept_a][TypeRelation.IDENTIQUE_A]:
                    if (concept_b, TypeRelation.IDENTIQUE_A, concept_a) not in self.relations:
                        new_relations.add((concept_b, TypeRelation.IDENTIQUE_A, concept_a))
                        count += 1
                        if count <= 5:
                            print(f"    Nouveau: {concept_b} IDENTIQUE_A {concept_a}")
        print(f"  IDENTIQUE_A symétrique: {count} nouvelles relations")
        return new_relations
    
    def apply_opposition_rules(self):
        """Applique les règles d'opposition."""
        new_relations = set()
        print("Application des règles d'opposition...")
        # Règle 9: Symétrie de S_OPPOSE_A
        count = 0
        for concept_a in self.relation_graph:
            if TypeRelation.S_OPPOSE_A in self.relation_graph[concept_a]:
                for concept_b in self.relation_graph[concept_a][TypeRelation.S_OPPOSE_A]:
                    if (concept_b, TypeRelation.S_OPPOSE_A, concept_a) not in self.relations:
                        new_relations.add((concept_b, TypeRelation.S_OPPOSE_A, concept_a))
                        count += 1
                        if count <= 5:
                            print(f"    Nouveau: {concept_b} S_OPPOSE_A {concept_a}")
        print(f"  S_OPPOSE_A symétrique: {count} nouvelles relations")
        # Règle 10: Symétrie de CONTREDIT
        count = 0
        for concept_a in self.relation_graph:
            if TypeRelation.CONTREDIT in self.relation_graph[concept_a]:
                for concept_b in self.relation_graph[concept_a][TypeRelation.CONTREDIT]:
                    if (concept_b, TypeRelation.CONTREDIT, concept_a) not in self.relations:
                        new_relations.add((concept_b, TypeRelation.CONTREDIT, concept_a))
                        count += 1
                        if count <= 5:
                            print(f"    Nouveau: {concept_b} CONTREDIT {concept_a}")
        print(f"  CONTREDIT symétrique: {count} nouvelles relations")
        return new_relations
    
    def apply_causal_rules(self):
        """Applique les règles causales et logiques."""
        new_relations = set()
        print("Application des règles causales...")
        # Règle 11: De la cause à la permission
        count = 0
        for concept_a in self.relation_graph:
            if TypeRelation.CAUSE in self.relation_graph[concept_a]:
                for concept_b in self.relation_graph[concept_a][TypeRelation.CAUSE]:
                    if (concept_a, TypeRelation.PERMET, concept_b) not in self.relations:
                        new_relations.add((concept_a, TypeRelation.PERMET, concept_b))
                        count += 1
                        if count <= 5:
                            print(f"    Nouveau: {concept_a} PERMET {concept_b} (car CAUSE)")
        print(f"  CAUSE → PERMET: {count} nouvelles relations")
        # Règle 12: De la nécessité à la dépendance
        count = 0
        for concept_a in self.relation_graph:
            if TypeRelation.NECESSITE in self.relation_graph[concept_a]:
                for concept_b in self.relation_graph[concept_a][TypeRelation.NECESSITE]:
                    if (concept_a, TypeRelation.DEPEND_DE, concept_b) not in self.relations:
                        new_relations.add((concept_a, TypeRelation.DEPEND_DE, concept_b))
                        count += 1
                        if count <= 5:
                            print(f"    Nouveau: {concept_a} DEPEND_DE {concept_b} (car NECESSITE)")
        print(f"  NECESSITE → DEPEND_DE: {count} nouvelles relations")
        # Règle 13: De empêche à s'oppose
        count = 0
        for concept_a in self.relation_graph:
            if TypeRelation.EMPECHE in self.relation_graph[concept_a]:
                for concept_b in self.relation_graph[concept_a][TypeRelation.EMPECHE]:
                    if (concept_a, TypeRelation.S_OPPOSE_A, concept_b) not in self.relations:
                        new_relations.add((concept_a, TypeRelation.S_OPPOSE_A, concept_b))
                        count += 1
                        if count <= 5:
                            print(f"    Nouveau: {concept_a} S_OPPOSE_A {concept_b} (car EMPECHE)")
        print(f"  EMPECHE → S_OPPOSE_A: {count} nouvelles relations")
        return new_relations
    
    def apply_hierarchical_rules(self):
        """Applique les règles hiérarchiques."""
        new_relations = set()
        print("Application des règles hiérarchiques...")
        # Règle 14: Héritage de propriétés par classification
        count = 0
        for concept_a in self.relation_graph:
            if TypeRelation.EST_UN in self.relation_graph[concept_a]:
                for concept_b in self.relation_graph[concept_a][TypeRelation.EST_UN]:
                    if concept_b in self.relation_graph and TypeRelation.A_COMME_PROPRIETE in self.relation_graph[concept_b]:
                        for propriete in self.relation_graph[concept_b][TypeRelation.A_COMME_PROPRIETE]:
                            if (concept_a, TypeRelation.A_COMME_PROPRIETE, propriete) not in self.relations:
                                new_relations.add((concept_a, TypeRelation.A_COMME_PROPRIETE, propriete))
                                count += 1
                                if count <= 5:
                                    print(f"    Nouveau: {concept_a} A_COMME_PROPRIETE {propriete} (héritage via {concept_b})")
        print(f"  Héritage EST_UN → A_COMME_PROPRIETE: {count} nouvelles relations")
        # Règle 15: Héritage de propriétés par instanciation
        count = 0
        for concept_a in self.relation_graph:
            if TypeRelation.INSTANCE_DE in self.relation_graph[concept_a]:
                for concept_b in self.relation_graph[concept_a][TypeRelation.INSTANCE_DE]:
                    if concept_b in self.relation_graph and TypeRelation.A_COMME_PROPRIETE in self.relation_graph[concept_b]:
                        for propriete in self.relation_graph[concept_b][TypeRelation.A_COMME_PROPRIETE]:
                            if (concept_a, TypeRelation.A_COMME_PROPRIETE, propriete) not in self.relations:
                                new_relations.add((concept_a, TypeRelation.A_COMME_PROPRIETE, propriete))
                                count += 1
                                if count <= 5:
                                    print(f"    Nouveau: {concept_a} A_COMME_PROPRIETE {propriete} (instance via {concept_b})")
        print(f"  Héritage INSTANCE_DE → A_COMME_PROPRIETE: {count} nouvelles relations")
        # Règle 16: De fait_partie_de à dépend_de
        count = 0
        for concept_a in self.relation_graph:
            if TypeRelation.FAIT_PARTIE_DE in self.relation_graph[concept_a]:
                for concept_b in self.relation_graph[concept_a][TypeRelation.FAIT_PARTIE_DE]:
                    if (concept_a, TypeRelation.DEPEND_DE, concept_b) not in self.relations:
                        new_relations.add((concept_a, TypeRelation.DEPEND_DE, concept_b))
                        count += 1
                        if count <= 5:
                            print(f"    Nouveau: {concept_a} DEPEND_DE {concept_b} (car FAIT_PARTIE_DE)")
        print(f"  FAIT_PARTIE_DE → DEPEND_DE: {count} nouvelles relations")
        return new_relations
    
    def apply_complementarity_rules(self):
        """Applique les règles de complémentarité."""
        new_relations = set()
        print("Application des règles de complémentarité...")
        # Règle 17: Symétrie de COMPLEMENTE
        count = 0
        for concept_a in self.relation_graph:
            if TypeRelation.COMPLEMENTE in self.relation_graph[concept_a]:
                for concept_b in self.relation_graph[concept_a][TypeRelation.COMPLEMENTE]:
                    if (concept_b, TypeRelation.COMPLEMENTE, concept_a) not in self.relations:
                        new_relations.add((concept_b, TypeRelation.COMPLEMENTE, concept_a))
                        count += 1
                        if count <= 5:
                            print(f"    Nouveau: {concept_b} COMPLEMENTE {concept_a}")
        print(f"  COMPLEMENTE symétrique: {count} nouvelles relations")
        # Règle 18: Symétrie de EST_ANALOGUE_A
        count = 0
        for concept_a in self.relation_graph:
            if TypeRelation.EST_ANALOGUE_A in self.relation_graph[concept_a]:
                for concept_b in self.relation_graph[concept_a][TypeRelation.EST_ANALOGUE_A]:
                    if (concept_b, TypeRelation.EST_ANALOGUE_A, concept_a) not in self.relations:
                        new_relations.add((concept_b, TypeRelation.EST_ANALOGUE_A, concept_a))
                        count += 1
                        if count <= 5:
                            print(f"    Nouveau: {concept_b} EST_ANALOGUE_A {concept_a}")
        print(f"  EST_ANALOGUE_A symétrique: {count} nouvelles relations")
        return new_relations
    
    def apply_all_rules(self, max_iterations=3):
        """Applique toutes les règles d'inférence de manière itérative."""
        all_new_relations = set()
        iteration = 0
        
        print(f"Début de l'inférence avec {len(self.relations)} relations initiales")
        
        while iteration < max_iterations:
            print(f"\n=== Itération {iteration + 1} ===")
            new_relations = set()
            
            # Appliquer toutes les règles
            new_relations.update(self.apply_transitive_rules())
            new_relations.update(self.apply_equivalence_rules())
            new_relations.update(self.apply_opposition_rules())
            new_relations.update(self.apply_causal_rules())
            new_relations.update(self.apply_hierarchical_rules())
            new_relations.update(self.apply_complementarity_rules())
            
            # Filtrer les relations déjà existantes
            truly_new = new_relations - self.relations
            
            print(f"Nouvelles relations trouvées: {len(truly_new)}")
            
            if not truly_new:
                print("Aucune nouvelle relation trouvée, arrêt des itérations")
                break
            
            # Ajouter les nouvelles relations
            all_new_relations.update(truly_new)
            self.relations.update(truly_new)
            
            # Reconstruire le graphe avec les nouvelles relations
            self.build_graph()
            
            iteration += 1
        
        print(f"\nTerminé après {iteration} itérations")
        print(f"Total nouvelles relations dérivées: {len(all_new_relations)}")
        print(f"Total relations finales: {len(self.relations)}")
        
        return all_new_relations

def enhance_ontology(core_relations, output_file="ontologie_enrichie.py"):
    """Enrichit l'ontologie avec les règles d'inférence."""
    
    print(f"Relations initiales: {len(core_relations)}")
    
    # Créer le moteur d'inférence
    engine = LogicalInferenceEngine(core_relations)
    
    # Appliquer les règles d'inférence
    new_relations = engine.apply_all_rules()
    
    print(f"\nRésumé final:")
    print(f"Nouvelles relations dérivées: {len(new_relations)}")
    print(f"Total des relations: {len(engine.relations)}")
    
    # Statistiques détaillées des nouvelles relations
    if new_relations:
        derived_stats = Counter([rel.name for _, rel, _ in new_relations])
        print(f"\nStatistiques des nouvelles relations:")
        for rel_type, count in derived_stats.most_common():
            print(f"  {rel_type}: {count}")
    
    # Générer le fichier de sortie
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("from enum import Enum\n\n")
        
        # Enum original
        f.write("class TypeRelation(Enum):\n")
        for rel in TypeRelation:
            f.write(f'    {rel.name} = "{rel.value}"\n')
        f.write("\n\n")
        
        f.write("# Relations originales\n")
        f.write("CORE_RELATIONS_ORIGINAL = [\n")
        original_sorted = sorted(core_relations, key=lambda x: (x[0], x[1].name, x[2]))
        for src, rel, dst in original_sorted:
            f.write(f'    ("{src}", TypeRelation.{rel.name}, "{dst}"),\n')
        f.write("]\n\n")
        
        f.write("# Relations dérivées par inférence logique\n")
        f.write("DERIVED_RELATIONS = [\n")
        derived_sorted = sorted(new_relations, key=lambda x: (x[0], x[1].name, x[2]))
        for src, rel, dst in derived_sorted:
            f.write(f'    ("{src}", TypeRelation.{rel.name}, "{dst}"),\n')
        f.write("]\n\n")
        
        f.write("# Toutes les relations (originales + dérivées)\n")
        f.write("ALL_RELATIONS = CORE_RELATIONS_ORIGINAL + DERIVED_RELATIONS\n\n")
        
        # Statistiques
        original_stats = Counter([rel.name for _, rel, _ in core_relations])
        derived_stats = Counter([rel.name for _, rel, _ in new_relations])
        
        f.write("# Statistiques des relations originales:\n")
        for rel_type, count in original_stats.most_common():
            f.write(f"# {rel_type}: {count}\n")
        
        if new_relations:
            f.write("#\n# Statistiques des relations dérivées:\n")
            for rel_type, count in derived_stats.most_common():
                f.write(f"# {rel_type}: {count} (nouvelles)\n")
    
    print(f"Ontologie enrichie sauvegardée dans {output_file}")
    
    return list(engine.relations)

# Exemple d'utilisation
if __name__ == "__main__":
    # Utilisation des vraies relations extraites
    enhanced_relations = enhance_ontology(CORE_RELATIONS)