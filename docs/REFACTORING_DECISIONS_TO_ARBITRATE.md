# Decisions a trancher pour le refactoring massif

**Date:** 2026-06-30
**Statut:** file d'arbitrage pour lancer les agents vite
**Roadmap:** `PARALLEL_REFACTORING_ROADMAP.md`
**Prompts agents:** `PARALLEL_AGENT_PROMPT_PROGRAM.md`

Ce document extrait les questions que le mainteneur doit trancher avant ou
pendant le lancement parallele. Il ne remplace pas le sync board: chaque
decision acceptee doit ensuite etre reportee dans
`PARALLEL_REFACTORING_SYNC.md` sous forme `DEC-*`.

## Base d'audit locale

La review critique reste structurellement valide, mais certains heads cites ont
bouge depuis. La base locale verifiee apres mise a jour est:

| Repo | Branche | Head verifie | Evidence directe |
|---|---:|---:|---|
| `nirs4all` | `main` | `e41362b4` | `DEFAULT_ENGINE="legacy"`, backend `dag-ml` selectionnable, oracle parity present |
| `dag-ml` | `main` | `f58d7bf` | contrats `ControllerManifest`, `NodeTask`, `NodeResult`; `validate_contracts.py` |
| `dag-ml-data` | `main` | `347c15f` | provider/contracts a verifier en lockstep |
| `nirs4all-io` | `main` | `84ab189` | bridge `io -> dag-ml-data` comme point de depart |
| `nirs4all-methods` | `main` | `7602eb08` | kernels/parity methods, pas encore sur le chemin dag-ml V1 |
| `nirs4all-studio` | `main` | `2ccbf68` | `NativeResultsAdapter`, `/api/runs/execution-backends`, baseline pristine |
| `nirs4all-web` | `main` | `745eef8` | runtime WASM/browser a auditer comme entree primaire |
| `nirs4all-cluster` | `main` | `dcced30` | client/server/workers beta, leasing/versioning existants |

Verification faite avec CodeGraph quand disponible, puis croisee directement
dans les fichiers par `rg`, `sed`, `git -C <repo> rev-parse`, et lectures
ciblees. Les agents ne doivent pas utiliser les hashes de la review comme
verite si le checkout local diverge.

## Reponses a donner en premier

Pour lancer vite, il faut surtout repondre a ces questions:

1. `ARB-001`: V1 doit-elle vraiment basculer `DEFAULT_ENGINE` vers `dag-ml`, ou
   garder legacy par defaut en MVP?
2. `ARB-002`: acceptez-vous le modele d'oracle 3-tier qui preload les divergences
   deja mesurees?
3. `ARB-003`: V1 dag-ml est-elle sklearn-only, ou inclut-elle l'integration n4m?
4. `ARB-004`: `ControllerManifest` devient-il la surface canonique des bindings,
   avec adapter depuis `OperatorController`?
5. `ARB-005`: `core` reste-t-il inspect/validate/capability only, avec toute
   execution dans les runtimes?
6. `ARB-006`: le convertisseur legacy vit-il dans un nouveau `nirs4all-tools` et
   sort-il tout code legacy du runtime V1?
7. `ARB-007`: quelle strategie d'extraction UI est acceptee: Studio-first,
   Web+Studio contract-first, ou nouveau package immediat?
8. `ARB-008`: impose-t-on le lockstep obligatoire `dag-ml` / `dag-ml-data`?
9. `ARB-009`: quelle branch strategy pour agents et PRs multi-repos?

Le reste peut avancer en audit parallele pendant que ces points sont tranches.

## Decisions P0

### `ARB-001` - Cutover V1: `DEFAULT_ENGINE="dag-ml"` ou legacy maintenu?

**Question:** la V1 vise-t-elle le basculement public vers `dag-ml` par defaut,
ou un MVP avec backend `dag-ml` selectionnable et legacy encore par defaut?

**Evidence:** `nirs4all/nirs4all/pipeline/engine.py` garde
`DEFAULT_ENGINE = "legacy"`. Le backend `dag-ml` existe et est selectionnable.
La roadmap a ajoute `LOCK-DROP` et `L19`, mais il faut confirmer si le drop est
dans le scope V1.

**Options:**

- A. V1 stricte: `DEFAULT_ENGINE="dag-ml"` avant release.
- B. MVP intermediaire: legacy reste par defaut, `dag-ml` selectionnable, et le
  drop devient V1.1.
- C. V1 hybride: default `dag-ml` seulement pour certains profils.

**Recommendation actuelle:** A seulement si `LOCK-DROP` est signe avec
`EXPECTED_FALLBACK == empty`, export natif, `.n4a`/workspace cross-engine, outil
de migration, et suite PYREF verte. Sinon B, explicitement documentee.

**Debloque:** `L5`, `L17`, `L18`, `L19`, Studio/Web release notes.

### `ARB-002` - Oracle 3-tier et divergences acceptees

**Question:** l'oracle de compatibilite peut-il etre "Python actuel avec ledger",
au lieu de "meme resultat partout"?

**Evidence:** la suite existante contient `KNOWN_DIVERGENCES`,
`EXPECTED_FALLBACK`, des `legacy_bug`, et des changements voulus (`best_X`,
`num_predictions`). Certaines formes RNG ne peuvent pas etre bit-identiques.

**Options:**

- A. 3-tier: Python authoritative, dag-ml authoritative, ou oracle non
  executable/legacy wrong.
- B. Python strict partout, quitte a reproduire des bugs legacy.
- C. Pas de claim de parite V1, seulement compatibilite best effort.

**Recommendation actuelle:** A. Precharger les divergences connues dans
`PYREF-000`; ne jamais masquer les RNG par une tolerance large.

**Debloque:** `LOCK-PYREF`, `L5`, `L9`, `L12`, `L16`, `L19`.

### `ARB-003` - n4m/methods dans le chemin dag-ml V1?

**Question:** la V1 doit-elle executer les kernels `nirs4all-methods` via
`dag-ml`, ou garder V1 sklearn-only pour le runtime dag-ml?

**Evidence:** `nirs4all/operators/methods/n4m_ops.py` existe cote legacy Python.
Les recherches directes dans `dag-ml/crates` et
`nirs4all/nirs4all/pipeline/dagml` ne montrent pas de chemin source n4m. Les
controllers dag-ml existent, mais l'invocation n4m depuis un controller hote est
un travail net-new.

**Options:**

- A. V1 sklearn-only sur dag-ml; n4m reste methods/parity et legacy operator.
- B. V1 inclut un controller/adapter n4m minimal.
- C. V1 inclut n4m complet avec artifacts portables.

**Recommendation actuelle:** A pour aller vite. B seulement si un agent dedie
prend le contrat controller + ABI + fixtures + PYREF methods-installed.

**Debloque:** `L5`, `L9`, `L16`, `L19`, docs publiques.

### `ARB-004` - Surface canonique des controllers

**Question:** `ControllerManifest` est-il la surface canonique des bindings et
runtimes, avec un adapter depuis les `OperatorController` Python actuels?

**Evidence:** il y a trois objets distincts: `ControllerManifest` declaratif
dag-ml, `OperatorController` Python stateful, et le router dag-ml Python. Studio
consomme une node-registry, pas encore les manifests.

**Options:**

- A. `ControllerManifest` canonique; adapter `OperatorController -> manifest`;
  node-registry Studio reconciliee.
- B. `OperatorController` reste canonique pour Python; manifests seulement
  runtimes externes.
- C. Deux mondes separes pour V1, rapprochement post-V1.

**Recommendation actuelle:** A. Sans ca, chaque binding/langage risque de
reconstruire une surface idiomatique differente.

**Debloque:** `L10`, `L11`, `L12`, `L13`, `L16`, bindings R/MATLAB/Python.

### `ARB-005` - Role exact de `core` vs `runtime-*`

**Question:** le futur `core` execute-t-il quelque chose, ou expose-t-il
seulement inspect/validate/plan/capabilities et les facades?

**Evidence:** la review a signale que `portable_run_subset` dans core cree un
second foyer d'execution. Les runtimes existent deja comme chemins de fait:
Python in-tree, Web/WASM, cluster.

**Options:**

- A. Core inspect/validate/capability only; execution uniquement runtime.
- B. Core execute un portable subset.
- C. Core agrege et delegue, mais expose une API `run()` qui choisit un runtime.

**Recommendation actuelle:** A pour eviter un second moteur. C peut etre une
facade plus tard si elle ne contient aucune logique d'execution.

**Debloque:** `LOCK-GOV`, `LOCK-CAP`, `LOCK-RT`, `L4`, `L10`.

### `ARB-006` - Migration legacy et `nirs4all-tools`

**Question:** cree-t-on un projet `nirs4all-tools` qui absorbe/supersede
`nirs4all/pipeline/storage/migration.py` et porte les convertisseurs legacy?

**Evidence:** l'in-tree migrator existe et annonce une suppression en v1. Le
besoin utilisateur est de ne pas perdre pipelines, predictions, workspaces et
bundles, sans garder de code legacy dans le runtime V1.

**Options:**

- A. Nouveau `nirs4all-tools`, offline, one-way, no in-place, support window.
- B. Garder les lecteurs legacy dans `nirs4all` V1.
- C. Convertisseur ponctuel non publie.

**Recommendation actuelle:** A. C'est le meilleur compromis entre preservation
des donnees et runtime propre.

**Debloque:** `LOCK-MIG`, `L18`, `L19`, Studio old-workspace refusal.

### `ARB-007` - Extraction UI reusable components

**Question:** comment extrait-on `nirs4all-ui` sans refaire un design system
abstrait?

**Evidence:** Studio et Web ont deja diverge au niveau primitives. La baseline
visuelle est net-new. Les composants runtime/results/export dependent de
`LOCK-RT`, pas seulement de `LOCK-UI`.

**Options:**

- A. Studio-first pour foundation/data/pipeline, contract-first pour
  runtime/results/export, avec audit Web simultane.
- B. Nouveau package UI immediat avant adoption produit.
- C. Chaque app garde sa UI jusqu'a la fin, extraction post-V1.

**Recommendation actuelle:** A. Extraire uniquement ce qui est consomme par au
moins un produit et tester par fixtures + screenshots.

**Debloque:** `LOCK-UI`, `LOCK-RT`, `L11`, `L12`, `L13`.

### `ARB-008` - Lockstep `dag-ml` / `dag-ml-data`

**Question:** toute modification de schema/fixture partage doit-elle etre
couplee entre `dag-ml` et `dag-ml-data`?

**Evidence:** des schemas miroirs et conformance packs existent deja. Les
agents paralleles peuvent facilement creer du drift si le lockstep n'est pas
une obligation CI.

**Options:**

- A. Paired commits/PRs + CI contract-equivalence obligatoire.
- B. Synchronisation manuelle par release train.
- C. Un repo devient source unique et l'autre genere.

**Recommendation actuelle:** A maintenant, C plus tard si generation
automatique devient fiable.

**Debloque:** `LOCK-LOCKSTEP`, `L5`, `L6`, `L20`, release train.

### `ARB-009` - Strategie branches, worktrees et merge

**Question:** comment les agents evitent-ils de se bloquer dans un workspace de
repos freres?

**Options:**

- A. Une branche par lane dans chaque repo touche, sync doc comme source
  commune, integration par locks.
- B. Une grosse branche ecosysteme par vague.
- C. Agents libres, rebase manuel a la fin.

**Recommendation actuelle:** A. Les contrats cross-repo passent par `DEC-*`, les
implementations locales restent par lane.

**Debloque:** tous les agents.

## Decisions P1

### `ARB-010` - Provider/plugin contracts

**Question:** repository, benchmarks, papers, datasets et cluster deviennent-ils
des providers/plugins exposes par core en extras?

**Recommendation actuelle:** oui en extras. `repository` est read-only pour
presets/pipelines au depart; `benchmarks` peut exposer `get_pipeline` et faire
queue/evaluate localement avec un runner, mais reste deconnecte en ecriture de
l'ecosysteme; `papers` est proche d'un plugin export reproductible; `datasets`
est provider de references; `cluster` est client optionnel.

**Debloque:** `L14`, `L15`, docs package/release.

### `ARB-011` - Cluster V1 scope

**Question:** le cluster V1 est-il un client optionnel + beta hardening, ou un
full scheduler DAG fin?

**Recommendation actuelle:** client/server/workers existants durcis, RBAC,
Studio/CLI adapter, distributed==local parity. Le fine-grained DAG attend que
`dag-ml` soit coordinateur plus complet.

**Debloque:** `L15`, `L10`, Studio.

### `ARB-012` - Web/WASM parity target

**Question:** Web doit-il executer tout ce que Python execute, ou seulement un
subset inspect/validate/run portable?

**Recommendation actuelle:** inspect/validate largement, execution subset avec
`unsupported` explicite. Ne pas promettre les artifacts Python ou controllers
host-only dans WASM.

**Debloque:** `L13`, `LOCK-CAP`, `LOCK-RT`, `LOCK-UI`.

### `ARB-013` - `nirs4all-lite` vers `nirs4all-core`

**Question:** le scaffold `nirs4all-lite` devient-il le futur aggregate public
`nirs4all-core`, et avec quels extras?

**Recommendation actuelle:** oui seulement apres clarification du clone
temporaire `nirs4all-core`. `datasets` devrait etre optionnel par defaut sauf
decision contraire.

**Debloque:** `L1`, `L4`, release inventory.

### `ARB-014` - Namespaces Python/R/npm

**Question:** garde-t-on les distributions explicites (`nirs4all-methods`,
etc.) et introduit-on `n4a.*` uniquement comme facade ergonomique?

**Recommendation actuelle:** oui. En Python, garder `nirs4all.*` compatible et
ajouter `n4a.*` graduellement. En R, preferer des packages explicites
(`nirs4allmethods`, `nirs4allio`, etc.) pour les surfaces publiques.

**Debloque:** `LOCK-GOV`, docs publiques, bindings.

### `ARB-015` - AOM placement

**Question:** `nirs4all-aom` reste-t-il un projet separe, est-il absorbe par
`nirs4all-methods`, ou devient-il surtout un plugin papers/methods?

**Recommendation actuelle:** trancher avant de promettre AOM dans methods ou
papers. Tant que ce n'est pas tranche, AOM reste hors chemin V1 critique.

**Debloque:** `L9`, `L14`, papers export.

### `ARB-016` - Cross-engine `.n4a` et workspace comme gate V1

**Question:** exige-t-on que legacy bundle/workspace soit inspectable et/ou
predictable sur runtime V1 avant legacy-DROP?

**Recommendation actuelle:** oui pour les cas declares supportes; sinon
diagnostic `unsupported` + chemin `nirs4all-tools`. Ne pas marquer ce claim
comme deja prouve.

**Debloque:** `L4`, `L5`, `L17`, `L18`, `L19`.

### `ARB-017` - First public multimodal proof

**Question:** quel cas public donne assez de pression reelle sur identities,
relations, leakage, UI et reproducibility?

**Recommendation actuelle:** choisir tot un cas data-real redistribuable ou
documenter un proof prive non release. Sans proof, les schemas multimodaux
risquent d'etre trop abstraits.

**Debloque:** `L6`, `L7`, `L8`, `L11`, docs publiques.

### `ARB-018` - Methods-installed CI

**Question:** les tests `nirs4all-methods` doivent-ils etre obligatoires dans
les gates V1 des capabilities portables?

**Recommendation actuelle:** oui pour toute capability marquee portable. Les
skips "methods missing" sont acceptables en dev local, pas en release gate.

**Debloque:** `L9`, `L17`, release train.

## Format de reponse rapide

Pour aller vite, le mainteneur peut repondre avec:

```text
ARB-001: A/B/C + note
ARB-002: A/B/C + note
ARB-003: A/B/C + note
ARB-004: A/B/C + note
ARB-005: A/B/C + note
ARB-006: A/B/C + note
ARB-007: A/B/C + note
ARB-008: A/B/C + note
ARB-009: A/B/C + note
```

Tout ce qui n'est pas repondu reste `proposed` et les agents doivent travailler
en audit/spec, pas modifier des interfaces cross-repo.
