# OPF - Ontologie Philosophique Formelle 

→ utilisée dans [SophIA](https://github.com/XenocodeRCE/SophIA)

## Ontologie


```py
from enum import Enum

class TypeRelation(Enum):
    IMPLIQUE = "implique"                      # Relation d'implication logique ou conceptuelle
    CONTREDIT = "contredit"                    # Relation de contradiction
    EST_EQUIVALENT = "est_équivalent"          # Relation d'équivalence
    EST_UN = "est_un"                          # Relation d'appartenance à une catégorie (is_a)
    FAIT_PARTIE_DE = "fait_partie_de"          # Relation de méronomie (part_of)
    A_COMME_PROPRIETE = "a_comme_propriété"    # Relation attributive
    CAUSE = "cause"                            # Relation causale
    PERMET = "permet"                          # Relation d'activation ou de permission
    EMPECHE = "empêche"                        # Relation d'empêchement ou d'inhibition
    DEFINIT = "définit"                        # Relation de définition
    EXPLIQUE = "explique"                      # Relation d'explication
    ATTESTE = "atteste"                        # Relation d'évidence ou de preuve
    PRECEDE = "précède"                        # Relation temporelle ou logique de précédence
    SUIT = "suit"                              # Relation temporelle ou logique de succession
    S_OPPOSE_A = "s'oppose_à"                  # Relation d'opposition ou d'antagonisme
    COMPLEMENTE = "complémente"                # Relation de complémentarité
    SUBSUME = "subsombe"                       # Relation de subsomption (englobe une catégorie)
    EST_ANALOGUE_A = "est_analogue_à"          # Relation d'analogie ou de similarité
    DEPEND_DE = "dépend_de"                    # Relation de dépendance
    EST_COMPOSE_DE = "est_composé_de"          # Relation de composition
    NECESSITE = "nécessite"                    # Relation de nécessité
    POSSIBLE_SI = "possible_si"                # Relation de possibilité conditionnelle
    INSTANCE_DE = "instance_de"                # Relation d'instanciation (un particulier d'une catégorie)
    CONSTITUE = "constitue"                    # Relation de constitution (base de)
    VISE = "vise"                              # Relation de finalité, de but (téléologie)
    MEMBRE_DE = "membre_de"                    # Relation d'appartenance à un ensemble/groupe
    IDENTIQUE_A = "identique_à"                # Relation d'identité
    PERSONNALISEE = "personnalisée"            # Pour toute relation spécifique non prévue
```
