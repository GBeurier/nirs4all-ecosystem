# Roadmap parallele du refactoring multimodal nirs4all

**Date:** 2026-06-30
**Statut:** plan de lancement pour agents, re-baseline apres review critique
du 2026-06-30
**Document de synchro:** `PARALLEL_REFACTORING_SYNC.md`
**Questions a trancher:** `REFACTORING_DECISIONS_TO_ARBITRATE.md`
**Prompts agents:** `PARALLEL_AGENT_PROMPT_PROGRAM.md`

## 1. But

Ce document transforme `SYNTHESE_MULTIMODALE_NIRS4ALL.md` en plan d'execution
massivement parallelisable. Il est fait pour lancer plusieurs agents de haut
niveau, chacun autorise a spawn des agents locaux, tout en gardant:

- une source de verite partagee;
- des contrats inter-repos explicites;
- des gates executables;
- des limites de responsabilite strictes;
- une parite mesurable avec la librairie Python `nirs4all` actuelle;
- une integration progressive sans big-bang.

La cible n'est pas "tout en meme temps". La cible est "tout ce qui ne partage
pas une interface instable peut avancer en parallele, et tout ce qui partage une
interface passe d'abord par un mini-contrat ecrit".

## 2. Prerequis de lancement

La review critique `REFACTORING_ROADMAP_CRITICAL_REVIEW.md` a corrige un point
important: une partie du chantier n'est plus future/greenfield dans ce checkout.
`nirs4all` expose deja un backend `dag-ml` selectionnable, Studio main est clean
localement, et un oracle de parite existe deja sous
`nirs4all/tests/integration/parity/`. Les prerequis servent donc a ratifier et
figer l'evidence, pas a attendre une implementation de zero.

Apres mise a jour locale du 2026-06-30, les hashes de la review ne sont plus
tous actuels. La base directe a utiliser pour les agents est: `nirs4all`
`e41362b4`, `dag-ml` `f58d7bf` sur `main`, `dag-ml-data` `347c15f`,
`nirs4all-io` `84ab189`, `nirs4all-methods` `7602eb08`, `nirs4all-studio`
`2ccbf68`, `nirs4all-web` `745eef8`, `nirs4all-cluster` `dcced30`. Les
conclusions structurelles de la review restent a traiter, mais tout agent doit
verifier le code local directement avant d'agir.

| Gate | Sortie attendue | Pourquoi c'est bloquant |
|---|---|---|
| `PRE-1` Backend `dag-ml` selectionnable dans `nirs4all` | Ratifier l'etat local: `nirs4all/pipeline/engine.py` garde `DEFAULT_ENGINE = "legacy"` mais `engine="dag-ml"` / `N4A_ENGINE=dag-ml` dispatchent vers `nirs4all/pipeline/dagml`. | Toute extraction runtime/UI depend d'un backend stable et observable; le vrai travail restant est hardening + cutover, pas branchement initial. |
| `PRE-2` Studio pristine | Ratifier le head Studio propre, la baseline tests/screenshots utile, et le contrat backend/workspace courant. | Studio est le principal consommateur; une base sale rend les regressions indiagnostiquables. |
| `PRE-3` Oracle Python actuel disponible | Adopter l'oracle existant `nirs4all/tests/integration/parity/`, importer son registre d'incompatibilites acceptees, puis combler les surfaces non couvertes: `.n4a`, workspace cross-engine, methods-installed lane. | La librairie Python actuelle reste la reference Tier 1; les agents doivent savoir quand le Python legacy fait autorite, quand `dag-ml` fait autorite, et quand la comparaison n'est pas valide. |
| `PRE-4` Branch strategy choisie | une branche par lane et un protocole de merge inter-repos. | Le refactoring touche des repos independants, pas un monorepo. |

Si un prerequis est partiellement vrai, le coordinateur doit l'enregistrer dans
`PARALLEL_REFACTORING_SYNC.md` avec la liste exacte de tests verts et de zones
encore instables.

## 3. Contraintes non negociables

Ces contraintes viennent des docs existantes et doivent etre repetees aux agents:

- `nirs4all-core` est l'aggregate public canonique; l'ancien nom de chantier
  `nirs4all-lite` ne doit plus etre publie ni maintenu comme alias public.
- Le futur `core` agrege. Il ne devient pas un second moteur.
- Les parsers vendor restent dans `nirs4all-formats`.
- L'assemblage dataset reste dans `nirs4all-io`.
- Le vocabulaire data multimodal reste dans `dag-ml-data`.
- L'orchestration ML, OOF, replay, scores/predictions et leakage safety restent
  dans `dag-ml`.
- Les kernels numeriques portables restent dans `nirs4all-methods`.
- `nirs4all` Python conserve l'API riche et les controllers Python.
- Le nom public `nirs4all` V1 couvre explicitement trois surfaces a piloter
  ensemble: le package Python historique/oracle, l'aggregate R `nirs4all`, et
  la distribution browser/WASM `nirs4all`/`@nirs4all/*`. Une lane ne peut pas
  conclure "nirs4all done" si elle n'a verifie que Python.
- La version Python actuelle de `nirs4all` est l'oracle Tier 1 de parite: un
  pipeline actuel execute avec des operators sklearn doit produire les memes
  splits, predictions, scores, artifacts et erreurs attendues apres migration,
  sauf incompatibilite acceptee dans le registre `PYREF-000`. Pour certains cas
  deja mesures (`rep_to_*`, `best_X`, `num_predictions` winner-only), `dag-ml`
  est la reference V1 parce que le legacy est faux ou que le contrat a change.
- Les shapes RNG non deterministes ne doivent pas etre "corrigees" par une
  tolerance large: elles doivent etre classees `rng_nondeterministic`,
  `skip_unknown_semantics` ou fixees a la source.
- Les tests unitaires/integration existants de `nirs4all` sont portes comme
  gates de migration avec seulement des adaptations de signatures minimales.
- Le code legacy de lecture des anciens workspaces/bundles ne reste pas dans le
  runtime V1: il vit dans un outil de migration standalone, versionne et borne.
- Studio et Web consomment des runtimes/capabilities, pas des details internes.
- `nirs4all-ui` ne contient ni appels backend, ni persistence, ni parser, ni ML.
- Un bundle doit etre inspectable partout, executable seulement si le runtime
  declare les capabilities necessaires.
- Aucune promesse cross-runtime sans fixture de conformance et diagnostic
  `unsupported` explicite.

## 4. Plafond de parallelisme reel

Le programme peut occuper beaucoup d'agents, mais seulement si les contrats
suivants sont serialises au debut:

| Lock | Contrat a figer | Bloque |
|---|---|---|
| `LOCK-GOV` | noms publics, ownership des repos, politique no-legacy-alias | `CORE-*`, docs publiques, releases |
| `LOCK-CAP` | vocabulaire capability/unsupported/portability | runtimes, UI, core aggregate, Studio/Web |
| `LOCK-PYREF` | oracle de parite Python: corpus, comparateurs, tolerances, commandes de test | `dag-ml`, runtime Python, controllers, Studio, methods |
| `LOCK-MIG` | politique et schema de migration legacy -> V1: inputs supportes, target store, rapport, verification, refus | `nirs4all-tools`, `dag-ml`, Studio, support utilisateurs |
| `LOCK-DROP` | criteres de cutover legacy-DROP: `DEFAULT_ENGINE="dag-ml"`, fallback vide, export natif, suites vertes | `nirs4all`, `dag-ml`, Studio/Web runtime, release notes |
| `LOCK-LOCKSTEP` | obligation CI byte-identical `dag-ml` <-> `dag-ml-data` pour schemas/fixtures/contract manifests | `dag-ml`, `dag-ml-data`, release train |
| `LOCK-REL` | manifest + lockfile d'aggregation minimal | core aggregate, release train, cockpit |
| `LOCK-IO` | `DatasetSpec v2`, `DatasetPackage`, payload manifest | profils IO, datasets, providers, UI dataset views |
| `LOCK-RT` | API runtime commune | Studio backend, Web runtime, CLI runtime |
| `LOCK-UI` | scope package `nirs4all-ui`, taxonomy composants, tokens/build deps, composants initiaux, baseline visuelle Studio, decision primitives canoniques | extraction Studio, adaptation Web |

Avant ces locks, lancer surtout des agents d'audit, de spec, de fixtures et de
prototypage isole. Apres ces locks, les lanes peuvent avancer avec peu de
coordination synchrone.

## 5. Architecture du programme

```text
PRE ratified backend+Studio+Python oracle
        |
        v
GOV/CAP/PYREF/MIG/DROP/LOCKSTEP/REL/IO/RT/UI locks
        |
        +-------------------+-------------------+-------------------+
        |                   |                   |                   |
   Core aggregate      Multimodal IO       Runtime contracts     UI package
        |                   |                   |                   |
        +---------+---------+---------+---------+---------+---------+
                  |                   |                   |
                  v                   v                   v
           Studio Python        Web WASM/browser       datasets/proof
                  \                   |                   /
                   \                  |                  /
                    +----- Python oracle + conformance --+
                              |
                              v
                     release train + public proof
```

## 6. Lanes d'agents

Une lane est un flux de travail durable avec un owner. Chaque lane peut lancer
des sous-agents, mais elle rend compte dans le document de synchro commun.

### `L0` Coordination et arbitrage

**Repo principal:** `nirs4all-ecosystem`
**Dependances:** `PRE-1`, `PRE-2`
**Role:** maintenir le DAG, les locks, les decisions et la synchronisation.

Livrables:

- `PARALLEL_REFACTORING_SYNC.md` tenu a jour;
- table d'ownership par repo/lane;
- decision register;
- conflict map des fichiers/contrats partages;
- weekly integration branch checklist.

Gates:

- aucune lane ne modifie une interface cross-repo sans decision `DEC-*`;
- toutes les PRs cross-repo declarent le manifest/lockfile impacte;
- les blockers ont un owner et une prochaine action.

### `L1` Governance, naming, ADR

**Repos:** `nirs4all-ecosystem`, puis docs publiques selon decision
**Dependances:** `PRE-1` pour verrouiller le statut de l'aggregate canonique
**Role:** retirer l'ambiguite `lite/core/python/web/runtime/ui`.

Taches:

- `GOV-001`: ADR statut de `nirs4all-core` comme aggregate canonique.
- `GOV-002`: ADR final applique: l'aggregate public est `nirs4all-core`.
- `GOV-003`: table source-of-truth repo/package/import par langage.
- `GOV-004`: politique aliases/deprecations: aucun alias public legacy pour
  l'ancien nom `nirs4all-lite`.
- `GOV-005`: matrice licence par repo/runtime/artifact.

Sortie:

- `LOCK-GOV` signe;
- aucune collision de nom restante;
- decision sur les packages publies: Python, Rust crate, npm/WASM, R, MATLAB.

### `L2` Capabilities, portability, conformance

**Repos:** `nirs4all-ecosystem`, `dag-ml`, `dag-ml-data`, `nirs4all-core`,
`nirs4all`, `nirs4all-studio`, `nirs4all-web`
**Dependances:** `PRE-3`, puis `LOCK-GOV`, coordination avec `L17`
**Role:** fournir le langage commun que tous les produits consomment.

Taches:

- `CAP-001`: spec capability minimale: `inspect`, `validate`, `plan`, `run`,
  `predict`, `replay`, `explain`, `export`, `portable_level`, `unsupported`.
- `CAP-002`: taxonomy des niveaux de portabilite: non portable, contract
  portable, numerically portable, artifact portable, host-specific, full
  train+predict.
- `CAP-003`: ledger des operators/profils/runtimes.
- `CAP-004`: diagnostics `unsupported` normalises, avec cause et mitigation.
- `CON-001`: pack de conformance cross-runtime pour le portable subset.
- `CON-002`: fixtures bundle/workspace/capability inspectables hors Python.
- `CON-003`: brancher les resultats de parite Python `L17` dans le ledger
  capability: une capability executee en runtime Python n'est verte que si le
  pipeline equivalent est vert contre l'oracle `nirs4all` actuel.

Sortie:

- `LOCK-CAP` signe;
- `LOCK-PYREF` reference comme oracle de migration quand une capability existe
  deja dans la librairie Python actuelle;
- un runtime peut refuser proprement une feature absente;
- Studio/Web peuvent afficher la portabilite sans logique custom.

### `L3` Outils d'aggregation et release train

**Repo:** `nirs4all-ecosystem` d'abord; extraction plus tard seulement si besoin
**Dependances:** `LOCK-GOV` partiel, `LOCK-CAP` pour les champs capability
**Role:** remplacer les rebuilds manuels par manifest + lockfile + commandes.

Taches:

- `REL-001`: schema `aggregation-manifest.json`.
- `REL-002`: schema `aggregation-lock.json`.
- `REL-003`: commande `plan`: detecte drift, missing pins, ABI/API mismatch.
- `REL-004`: commande `lock`: fige commits/tags/versions/ABI.
- `REL-005`: commande `matrix`: genere compat matrix par runtime/package.
- `REL-006`: commande `dry-run-release`: verifie gates, SBOM/provenance.
- `REL-007`: bridge read-only pour `nirs4all-cockpit`.
- `REL-008`: consommer les conformance packs existants (`dag-ml`,
  `dag-ml-data`, ABI snapshots) au lieu de re-pinner les memes schemas dans un
  second format concurrent.

Sortie:

- `LOCK-REL` signe;
- un aggregate se reconstruit depuis manifest + lockfile;
- le cockpit lit les manifests, mais ne devient pas moteur de rebuild.

### `L4` Core aggregate: `nirs4all-core`

**Repo:** `nirs4all-core`
**Dependances:** `LOCK-GOV`, `LOCK-REL`, `LOCK-CAP`
**Role:** faire de l'aggregate portable le `core` final sans y ajouter de
logique metier. L'ancien nom de chantier `nirs4all-lite` est retire: il ne doit
pas rester de package, workflow ou cible de release publique sous ce nom.
Exposer directement tous les upstreams reste un vrai travail d'implementation,
pas un simple rename.

Taches:

- `CORE-001`: verifier les noms package/repo et l'absence d'alias legacy public.
- `CORE-002`: exposition directe de `dag-ml`, `dag-ml-data`, `formats`, `io`,
  `methods`, `datasets` si `DEC-GOV-002` le confirme; sinon documenter le
  modele `libloading`/lazy proxy. Decider explicitement si `datasets` est dans
  l'aggregate par defaut ou seulement client optionnel.
- `CORE-003`: capability matrix executable.
- `CORE-004`: conformance pack portable subset Python/R/MATLAB/WASM/Rust.
- `CORE-005`: lecteur `.n4a` minimal inspect-only cross-runtime.
- `CORE-006`: SBOM/provenance et support window.

Sortie:

- installation core inspectable sans `nirs4all` Python complet;
- aucun parser/kernel/orchestrateur duplique dans core;
- un `.n4a` Python est inspectable dans au moins un autre runtime.

### `L5` `dag-ml` runtime de production

**Repo:** `dag-ml` + bridge in-tree `nirs4all/pipeline/dagml`
**Dependances:** backend `dag-ml` selectionnable deja present; `LOCK-CAP`;
`LOCK-PYREF`; `LOCK-RT` pour API runtime; `L16` pour controllers
**Role:** solidifier le moteur commun, migrer l'orchestration Python restante
vers `dag-ml`, et reduire les fallback legacy jusqu'au cutover.

Taches:

- `DML-001`: ratifier les schemas existants `ControllerManifest`, `NodeTask`,
  `NodeResult`, `process_adapter_*`, `score_set` et leurs limites; ne pas les
  re-specifier from scratch.
- `DML-002`: migrer progressivement `nirs4all/pipeline/dagml/run_paths.py` et
  `detect.py` DOWN dans `dag-ml`, au lieu de laisser Python orchestrer les cas
  branches/stacking/rep-fusion/augmentation/generator.
- `DML-003`: mesurer et publier la couverture native-vs-fallback du corpus
  parity; l'objectif de `LOCK-DROP` est `EXPECTED_FALLBACK == empty`.
- `DML-003b`: predictions + scores + aggregation natives, y compris projections
  compat si necessaire, sans passer par le workspace legacy.
- `DML-003c`: lifecycle: progress, cancel, retry, export, replay.
- `DML-004`: ABI/lifetime/thread-safety/panic-to-error matrix.
- `DML-005`: scheduler/n_jobs/GPU/thread oversubscription policy.
- `DML-006`: conformance pack avec `dag-ml-data`, sous `LOCK-LOCKSTEP`.
- `DML-007`: parity gate legacy: meme `PipelineSpec` logique execute par
  `nirs4all` Python actuel et par backend `dag-ml`, avec comparaison splits,
  folds, OOF, predictions, metrics, model selection et erreurs attendues selon
  le registre 3-tier `PYREF-000`.
- `DML-008`: remplacer le bridge d'export `.n4a` qui refit via legacy par un
  export natif couvrant les cas requis avant `LOCK-DROP`.

Sortie:

- `dag-ml` est executable, pas seulement validateur;
- `dag-ml` conserve la semantique des pipelines Python actuels;
- les hosts savent ce qui traverse l'ABI et ce qui reste opaque;
- Studio et CLI peuvent relayer le lifecycle sans adapter prive fragile.

### `L6` `dag-ml-data` providers et vocabulaire multimodal

**Repo:** `dag-ml-data`
**Dependances:** `LOCK-IO`, `LOCK-CAP`
**Role:** rendre les representations, axes, relations et providers productifs.

Taches:

- `DMD-001`: built-ins multimodaux et representation IDs stables.
- `DMD-002`: source/order independent schema fingerprints.
- `DMD-003`: providers in-memory pour matrices, tensors, targets, metadata:
  auditer/etendre l'existant au lieu de re-creer le provider spike.
- `DMD-004`: SampleRelationTable avec sample/observation/group/origin/repetition.
- `DMD-005`: materialization/view requests pour multimodal et folds.
- `DMD-006`: C ABI / WASM / Python smoke providers.

Sortie:

- `dag-ml-data validate-envelope` accepte les packages IO;
- les folds/view requests respectent les identities, pas les positions;
- les payload fingerprints detectent toute falsification.

### `L7` `nirs4all-io` multimodal v2

**Repo:** `nirs4all-io`
**Dependances:** `LOCK-IO`, `DMD-001` minimal, `nirs4all-formats` readers stables
**Role:** passer de `SpectroDataset` projection a `DatasetPackage` multimodal.

Taches:

- `IO-001`: `DatasetSpec v2` source model.
- `IO-002`: `DatasetPackage` / `AssembledDataset v2`.
- `IO-003`: identity/relation propagation.
- `IO-004`: integration native `nirs4all-formats` dans facade Rust.
- `IO-005`: emission multimodale `dag-ml-data` SourceDescriptor; traiter le
  bridge `nirs4all-io-dagml` existant comme evidence de depart, puis etendre aux
  profils multimodaux V2.
- `IO-006`: payload store export.
- `IO-010`: image folder profile.
- `IO-011`: native spectra + reference table profile.
- `IO-012`: hyperspectral cube profile.
- `IO-013`: time-series profile.
- `IO-014`: genotype descriptor-first profile.
- `IO-020`: CLI package commands.
- `IO-021`: binding surface Python/R/WASM/MATLAB/Rust.

Sortie:

- le legacy NIRS reste une projection;
- au moins spectra + image MVP valide `io -> dag-ml-data -> dag-ml`;
- cubes/time-series/genotype avancent par profils bornes et diagnostics clairs.

### `L8` `nirs4all-formats` readers et sidecars

**Repo:** `nirs4all-formats`
**Dependances:** demandes `L7`; contraintes WASM/package size
**Role:** fournir les lecteurs et sidecars, sans assembly dataset.

Taches:

- `FMT-001`: matrice readers utiles au premier MVP multimodal.
- `FMT-002`: sidecars HSI: ENVI/AVIRIS, ERDAS LAN, masks/ground truth.
- `FMT-003`: browser/WASM constraints par format.
- `FMT-004`: fixtures/goldens redistribuables ou private-local documentees.
- `FMT-005`: diagnostics sidecar manquant ou dialecte inconnu.

Sortie:

- pas de parser dans IO/Studio/Web;
- les profils IO peuvent referencer des readers avec provenance de fixture.

### `L9` `nirs4all-methods` kernels et parity

**Repo:** `nirs4all-methods`
**Dependances:** `LOCK-CAP`, `LOCK-PYREF`, `CON-001`; demandes runtime/core
**Role:** fournir le portable numerique par familles, gate par parity.

Taches:

- `MTH-001`: ledger methodes/operators par runtime/binding.
- `MTH-002`: ABI-skew matrix avec `dag-ml`/`dag-ml-data`/core.
- `MTH-003`: parity fixtures manquantes PLS/AOM/POP/preprocessing/splitters.
- `MTH-004`: model artifact portability: bytes n4m vs host-specific blobs.
- `MTH-005`: bindings smoke pour core aggregate.
- `MTH-006`: relier la parite kernel sklearn/native a la parite pipeline
  `L17`: un kernel peut etre juste seul mais casser un pipeline par seed,
  fold scope, preprocessing, NaN policy ou ordering.
- `MTH-007`: decision explicite V1: `dag-ml` execute-t-il seulement les
  operators sklearn via controllers Python, ou doit-il appeler `n4m` via un
  controller/ABI ? Etat verifie localement: pas d'appel source `n4m` dans
  `dag-ml/crates` ni `nirs4all/pipeline/dagml`; toute promesse "PLS/AOM via
  n4m" est donc roadmap, pas present tense.

Sortie:

- chaque capability numerique exposee a fixture, tolerance, docs et binding;
- la parite methods/sklearn reste un sous-ensemble de la parite pipeline
  complete, pas un substitut;
- aucun operator n'est marque portable sans gate.

### `L10` Runtime API commune

**Repos:** nouveau repo ou packages existants selon ADR; probablement spec dans
`nirs4all-ecosystem`, implementations dans `nirs4all`, `nirs4all-core`,
`nirs4all-web`
**Dependances:** `LOCK-CAP`, `LOCK-RT`, `DML-001`
**Role:** donner a Studio/Web/CLI une surface stable.

Taches:

- `RT-001`: spec runtime commune.
- `RT-002`: JSON schemas request/response: inspect, validate, plan, run,
  predict, replay, explain, export.
- `RT-003`: error model et unsupported diagnostics.
- `RT-PY-001`: runtime Python sur `nirs4all`.
- `RT-R-001`: runtime/binding R `nirs4all` aggregate, avec les memes schemas
  request/response et diagnostics `unsupported` que Python pour le portable
  subset.
- `RT-WASM-001`: runtime WASM/browser sur core/WASM.
- `RT-N4A-001`: matrice commune `nirs4all` Python/R/WASM indiquant pour chaque
  capability si elle est executable, inspect-only, ou unsupported avec cause.
- `RT-CLI-001`: runtime CLI smoke/automation.
- `RT-CON-001`: smokes cross-runtime sur les memes bundles/capabilities.

Sortie:

- Studio et Web ne consomment plus des internals divergents;
- les surfaces publiques `nirs4all` Python, R et WASM partagent les memes
  contrats runtime/capability pour le portable subset;
- un agent produit peut ajouter un ecran sans connaitre la pile native.

### `L11` `nirs4all-ui`

**Repo:** nouveau `nirs4all-ui` ou package initial dans Studio selon ADR
**Dependances:** `LOCK-UI`, `LOCK-CAP`; Studio pristine
**Role:** extraire et organiser les composants React reutilisables depuis
Studio, pas inventer un design-system abstrait.

Taches:

- `UI-001`: audit composants Studio stables, dependances, props, et Web
  consommateurs probables.
- `UI-002`: taxonomy d'extraction: foundation, data, pipeline, controller,
  runtime status, results, export/reproducibility.
- `UI-003`: package scaffold: React/TS/build/test/version policy.
- `UI-004`: types UI purs pour capabilities, datasets, pipelines, results,
  controller manifests et runtime events.
- `UI-005`: composants foundation: tokens, icons, buttons, forms, tabs, panels,
  table/list primitives, sans routing ni storage.
- `UI-006`: composants data: dataset summary, source list, modality inspector,
  diagnostics.
- `UI-007`: composants pipeline/controller: node cards, capability badges,
  portability panel, controller ownership display.
- `UI-008`: composants runtime/results: job status, progress, metrics tables,
  artifact/result cards, export status.
- `UI-009`: visual/contract tests: Vitest, component fixtures, Storybook ou
  equivalent si utile, screenshots Studio baseline pour les composants extraits.
- `UI-010`: adoption progressive dans Studio puis Web, sans fork de styles.

Sortie:

- Studio consomme au moins un vrai composant extrait;
- Web consomme ensuite le meme composant sans fork visuel majeur;
- le package a une organisation lisible par domaine, pas un vrac de composants;
- les composants ont des fixtures qui representent les schemas runtime/core;
- aucun hook runtime/app-state dans `nirs4all-ui`.

### `L12` Studio reassembly

**Repo:** `nirs4all-studio`
**Dependances:** Studio pristine, `RT-PY-001`, `UI-*` consomme, `LOCK-CAP`
**Role:** faire de Studio un assembleur runtime Python + UI + workflows produit.

Taches:

- `STU-001`: baseline pristine: tests, screenshots, API contract inventory.
- `STU-002`: backend runtime adapter: inspect/validate/plan/run/predict/replay.
- `STU-003`: lifecycle parity: start/progress/cancel/retry/export.
- `STU-004`: capability-aware node registry.
- `STU-005`: export wizard: portabilite du bundle et unsupported.
- `STU-006`: UI extracted components adoption.
- `STU-007`: workspace/bundle compatibility gates.

Sortie:

- l'utilisateur sait avant training si le pipeline est portable;
- raw SQL/workspace contracts restent compatibles ou migrent via gate explicite;
- le backend reste orchestration-only.

### `L13` Web/WASM reassembly

**Repo:** `nirs4all-web`
**Dependances:** `RT-WASM-001`, `CORE-*`, `UI-*`, `LOCK-CAP`
**Role:** faire de Web un assembleur runtime WASM + UI + browser-specific logic.

Taches:

- `WEB-001`: capability mapping du subset browser.
- `WEB-002`: runtime WASM adapter.
- `WEB-003`: unsupported diagnostics visibles.
- `WEB-004`: bundle inspect/replay quand possible.
- `WEB-005`: adoption `nirs4all-ui`.
- `WEB-006`: browser smokes et canvas/UI checks.

Sortie:

- aucune parite WASM surpromise;
- Web partage UI/contrats avec Studio;
- les limites browser sont explicites et testees.

### `L14` Providers et plugins ecosysteme

**Repos:** `nirs4all-datasets`, `nirs4all-repository`,
`nirs4all-benchmarks`, `nirs4all-papers`
**Hors scope:** `nirs4all-drafts`, `nirs4all-lab` restent prives et personnels.
**Dependances:** `LOCK-CAP`; `LOCK-IO` pour datasets -> IO; `LOCK-RT` pour
benchmarks/cluster execution.
**Role:** fournir des clients/providers optionnels autour du core, sans les
absorber dans le core.

Taches:

- `PROV-001`: `DatasetProvider`: adapter les APIs reelles de
  `nirs4all-datasets` et `nirs4all-io` (`to_nirs4all` aujourd'hui, futur
  `DatasetPackage`), pas inventer `to_dataset_package` comme si deja present.
- `PROV-002`: `PipelineProvider`: adapter `nirs4all-repository` autour de son
  role reel `list/get/fetch/card`; il doit fournir a terme `list pipelines` et
  `get pipeline`.
- `PROV-003`: `BenchmarkProvider`: `list_pipelines/get_pipeline/leaderboard`
  d'abord; `queue/evaluate` depend d'un runner runtime/cluster qui n'existe pas
  dans benchmarks et reste deconnecte en ecriture de repository/datasets/core.
- `PROV-004`: `PaperExportProvider`: `.n4a`/bundle -> page reproductible,
  avec APIs reelles `read_bundle/build_bibliography/build`, methodes/citations
  via `nirs4all-methods`, UI optionnelle.
- `PROV-005`: politique write: pas d'upload repository par defaut; benchmark
  disconnected-write; papers export explicite.

Sortie:

- core/runtimes/apps peuvent lister/recuperer datasets et pipelines par une
  interface commune;
- benchmarks peut mettre des pipelines en queue sur datasets n4a sans ecrire
  dans repository/datasets/core;
- papers est traite comme un plugin d'export reproductible, pas comme draft/lab.

### `L15` Cluster distribue

**Repo:** `nirs4all-cluster`
**Dependances:** `LOCK-RT`, `LOCK-CAP`; backend Python stable
**Role:** client/server/workers pour distribuer le calcul nirs4all/DAG avec
rights, capabilities, file d'eligibilite/lease et artefacts. Le repo est deja
un beta fonctionnel; la roadmap doit le durcir, pas le specifier de zero.

Taches:

- `CLU-001`: wrapper client core optionnel autour du `/v1` existant:
  register/submit/status/cancel/artifacts, version handshake et diagnostics.
- `CLU-002`: roles/rights: submit/read/cancel/execute/admin; gap prioritaire
  car le prototype local utilise une securite minimale.
- `CLU-003`: capabilities worker: packages, GPU, labels, data locality, versions.
- `CLU-004`: job/task DAG mapping: whole run, pipelines x datasets, variants,
  puis fine-grained DAG seulement quand `dag-ml` expose le coordinateur
  necessaire; ne pas contourner `dag-ml`.
- `CLU-005`: Studio/CLI adapter: remplacer local JobManager en opt-in.
- `CLU-006`: queue benchmarks -> cluster execution path.

Sortie:

- core expose au moins un client cluster optionnel;
- cluster reste owner du server/worker/scheduler;
- aucun parser/kernel/schema ML n'est reimplemente dans cluster.

### `L16` Controllers et bindings idiomatiques

**Repos:** `dag-ml`, `nirs4all`, `nirs4all-core`,
`nirs4all-methods`, bindings langage, runtimes
**Dependances:** `LOCK-CAP`, `LOCK-RT`; `dag-ml` controller schemas stables
**Role:** rendre explicite que l'ajout d'un binding/langage passe surtout par
des controllers idiomatiques declares par manifest.

Taches:

- `CTRL-000`: definir l'adapter manquant
  `nirs4all.controllers.OperatorController -> dag-ml ControllerManifest`, puis
  classer chaque controller Python: manifestable, legacy-only, ou a remplacer.
- `CTRL-001`: rendre visibles les schemas existants
  `ControllerManifest + NodeTask + NodeResult` dans core/runtimes/docs; les
  champs additionnels proposes (`transport`, `runtime_requirements`,
  `conformance_fixtures`) sont une extension versionnee ou sidecar, pas des
  champs deja presents.
- `CTRL-002`: registry de controllers par runtime/langage avec resolution
  selectors/priorities.
- `CTRL-002b`: reconciler la node-registry consommee par Studio avec
  `ControllerManifest`, afin que les UIs affichent la vraie surface runtime.
- `CTRL-003`: matrices des familles: transform, y_transform, split, model,
  stacking/meta, augmentation, adapter, tuner/generator, explain, chart/report.
- `CTRL-004`: transport policy: JSONL process adapter, C ABI native vtable,
  WASM direct, runtime-python internal, cluster worker.
- `CTRL-005`: controller authoring guide par binding: manifest, data bridge,
  artifact policy, idiomatic method wrapper, conformance fixtures. Ce guide doit
  avoir des sections explicites pour `nirs4all` Python, `nirs4all` R et
  `nirs4all` WASM/browser, avec les differences d'artifact host-owned
  documentees.
- `CTRL-006`: unsupported diagnostics par node: missing controller, unsupported
  phase, data representation mismatch, artifact not replayable.
- `CTRL-007`: conformance pack controller: manifest validation, resolution,
  fold leakage, artifact round-trip, numerical parity, timeout/error handling.

Sortie:

- Studio/Web peuvent afficher "ce node sera execute par tel controller dans tel
  runtime" avant execution;
- chaque binding peut ajouter des methodes idiomatiques sans forker `dag-ml`;
- les limites entre operator controllers, data providers, artifact stores,
  provider plugins et cluster sont documentees.

### `L17` Oracle de parite Python actuelle

**Repos:** `nirs4all`, `dag-ml`, `dag-ml-data`, `nirs4all-methods`,
`nirs4all-studio` pour les workflows produit consommateurs
**Dependances:** `PRE-1` ratifie, `PRE-3` ratifie, `LOCK-CAP`; coordination
avec `L5`, `L9`, `L10`, `L12`, `L16`
**Role:** adopter et etendre l'oracle existant de la version full Python actuelle
de `nirs4all`, pas reconstruire une suite parallele plus faible.

Ce n'est pas la meme chose que la parite `methods`/sklearn. La parite
`methods` valide un kernel ou une famille numerique. `L17` valide un pipeline
complet: composition d'operators sklearn, preprocessing, splitters, nested CV,
OOF, stacking/meta si supporte aujourd'hui, seeds, ordering, artifacts,
workspaces, signatures publiques et erreurs attendues.

Taches:

- `PYREF-000`: importer le registre d'incompatibilites deja mesurees dans
  l'oracle: strict-xfail, legacy_bug, `num_predictions` winner-only, `best_X`
  re-ancre sur le modele selectionne, `rng_nondeterministic` et
  `skip_unknown_semantics`.
- `PYREF-001`: inventaire des tests unitaires/integration `nirs4all` existants
  qui doivent rester verts apres backend `dag-ml`.
- `PYREF-002`: adopter le corpus golden existant de pipelines Python actuels, du
  simple au complexe:
  preprocessing + sklearn estimators, splitters, CV, model selection, OOF,
  metrics, prediction/replay, persistence si deja couverte.
- `PYREF-003`: comparateurs de resultats: indices/folds exacts, schema exact,
  predictions/metrics numeriques avec tolerances, artifacts et erreurs, avec
  la logique 3-tier suivante: Python authoritative, `dag-ml` authoritative, ou
  legacy/oracle non executable.
- `PYREF-004`: adopter le harness dual-run: legacy/full Python current runner vs final
  `dag-ml`/runtime-python path sur les memes inputs.
- `PYREF-005`: adaptation minimale des signatures de tests quand necessaire,
  avec note explicite si une API publique change.
- `PYREF-006`: integration CI locale: commande unique pour l'oracle rapide et
  commande complete pour la matrice integration.
- `PYREF-007`: ledger de regression: tout ecart doit etre classe bug,
  tolerance justifiee, ou changement hors scope V1 accepte par decision.
- `PYREF-008`: evidence Studio: les workflows produit qui lancent ces pipelines
  passent par la meme route runtime et ne contournent pas l'oracle.
- `PYREF-009`: tests cross-engine `.n4a` et workspace: legacy bundle/workspace
  -> prediction/inspection via `dag-ml`/runtime V1, avec schema SQLite/Parquet
  et resultats compares. Aujourd'hui ce claim est a traiter comme non prouve.
- `PYREF-010`: methods-installed CI lane: les tests `n4m`/methods ne doivent pas
  rester des skips si une capability est declaree portable.
- `PYREF-011`: gate `.so` freshness pour eviter les faux verts quand Rust a ete
  modifie mais la lib chargee est stale.

Sortie:

- `LOCK-PYREF` signe: corpus, tolerances, comparateurs et commandes sont fixes;
- aucun remplacement backend/controller n'est merge sans green sur l'oracle
  concerne;
- les tests existants restent la reference, pas une suite parallele affaiblie;
- la V1 peut affirmer la compatibilite pipeline Python actuelle avec evidence.

### `L18` `nirs4all-tools` et convertisseur legacy

**Repo:** nouveau `nirs4all-tools`
**Dependances:** `LOCK-MIG`, `LOCK-REL`; schemas `dag-ml`/runtime V1
suffisamment stables; coordination avec `L3`, `L5`, `L12`, `L17`
**Role:** fournir une trousse a outils standalone pour l'ecosysteme, hors
runtime produit, avec le convertisseur legacy workspace/bundle comme premier
outil critique.

Ce projet evite deux mauvaises options:

- garder des lecteurs legacy dans le runtime V1;
- abandonner les anciens workspaces, predictions, pipelines, scores et bundles.

Le principe est un outil offline, one-way, non destructif:

```text
old_workspace_or_bundle/
        |
        v
nirs4all-tools migrate legacy-to-dagml
        |
        +--> new_workspace_or_bundle/
        +--> migration_manifest.json
        +--> migration_report.json
```

Taches:

- `TOOL-001`: creer le repo/projet `nirs4all-tools` avec packaging Python, CLI,
  tests et politique de support.
- `TOOL-002`: spec `LegacyMigrationManifest`: source format, source version,
  target schema, old->new ID mapping, checksums, provenance, tool version.
- `TOOL-003`: spec `LegacyMigrationReport`: converted, preserved-opaque,
  unsupported, skipped, warnings, verification summary.
- `TOOL-004`: convertisseur `legacy-to-dagml-workspace`: SQLite/Parquet
  workspaces actuels -> store natif V1 `dag-ml`; il doit absorber/superseder
  explicitement `nirs4all/pipeline/storage/migration.py` qui existe deja en
  in-tree migrator pre-V1.
- `TOOL-005`: convertisseur `.n4a`/bundle legacy -> bundle/archive V1 quand les
  artifacts le permettent.
- `TOOL-006`: preservation policy pour artifacts Python/joblib: copie opaque
  hashee, marquage `legacy_python_artifact`, replay natif refuse sauf bridge
  explicitement disponible.
- `TOOL-007`: modes `dry-run`, `verify-only`, `copy-only`, `strict`, `best-effort`.
- `TOOL-008`: verification: row counts, prediction IDs, y_true/y_pred/y_proba
  checksums, metrics, folds, partitions, pipeline canonicalization, artifact
  hashes.
- `TOOL-009`: fixtures de migration: workspaces v0/v1/v2, DuckDB legacy,
  SQLite+Parquet, Studio workspace reel anonymise si disponible.
- `TOOL-010`: integration Studio/CLI: detecter "legacy workspace", proposer
  migration externe, ne pas ouvrir en ecriture dans Studio V1.
- `TOOL-011`: support window: l'outil migre les anciens formats pendant une
  duree annoncee; le runtime V1 ne porte pas ce code.

Sortie:

- `nirs4all-tools` publie au moins un CLI de migration standalone;
- aucune migration in-place: l'ancien workspace reste intact;
- un rapport dit exactement ce qui est converti, preserve opaque ou refuse;
- Studio/V1 peut refuser proprement un ancien workspace avec une commande de
  migration claire;
- les utilisateurs ne perdent pas leurs predictions/pipelines existants, meme
  quand certains artifacts ne sont plus rejouables nativement.

### `L19` Cutover legacy-DROP

**Repos:** `nirs4all`, `dag-ml`, `dag-ml-data`, Studio/Web release docs
**Dependances:** `LOCK-PYREF`, `LOCK-DROP`, `LOCK-LOCKSTEP`, `L5`, `L17`,
`L18` preview disponible
**Role:** posseder le vrai point de bascule V1: passer de `DEFAULT_ENGINE =
"legacy"` a `DEFAULT_ENGINE = "dag-ml"` et retirer le chemin legacy produit sans
perdre les donnees utilisateur.

Taches:

- `DROP-001`: figer le critere de cutover: `EXPECTED_FALLBACK == empty`,
  export `.n4a` natif pour les cas supportes, 3-tier oracle vert, no stale `.so`,
  Studio/Web sur route runtime, migration tool disponible.
- `DROP-002`: branch cutover: changer `DEFAULT_ENGINE`, retirer les commentaires
  metadata contradictoires, et executer la suite complete sous default `dag-ml`.
- `DROP-003`: audit des fallback legacy restants: chaque fallback est supprime,
  transforme en unsupported explicite, ou accepte comme bridge post-V1 borne par
  decision.
- `DROP-004`: release notes et guide migration: ce qui reste inspectable,
  executable, migrable ou opaque.
- `DROP-005`: smoke utilisateurs: pipelines sklearn existants, Studio workflows,
  Web subset, `.n4a` export/import, old workspace refusal + command
  `nirs4all-tools`.

Sortie:

- `DEFAULT_ENGINE="dag-ml"` est le comportement par defaut release;
- aucun claim V1 ne repose sur un fallback legacy implicite;
- les anciens artifacts passent par `nirs4all-tools` ou sont refuses avec
  diagnostic clair.

### `L20` Lockstep `dag-ml` / `dag-ml-data`

**Repos:** `dag-ml`, `dag-ml-data`, release train
**Dependances:** `LOCK-REL`, `LOCK-IO`, `L5`, `L6`
**Role:** faire de la coherence schema/fixture/contract entre `dag-ml` et
`dag-ml-data` une obligation permanente, pas une note de review.

Taches:

- `LOCKSTEP-001`: documenter les schemas miroirs et fixtures devant rester
  byte-identical hors `$id` specifique repo.
- `LOCKSTEP-002`: commande CI unique autour de `dag-ml/scripts/validate_contracts.py`
  et du sibling `dag-ml-data`.
- `LOCKSTEP-003`: policy de PR: toute modification de schema partage est une
  paire de commits/PRs ou un blocage explicite.
- `LOCKSTEP-004`: inclure les hashes du conformance pack dans
  `aggregation-lock.json`.

Sortie:

- aucune release `dag-ml` ou `dag-ml-data` ne part avec contracts divergents;
- le release train consomme les conformance packs existants au lieu de les
  dupliquer.

## 7. DAG des lots principaux

```text
PRE-1 backend selectable ratified
PRE-2 studio pristine ratified
PRE-3 python oracle adopted
        |
        v
GOV-001 GOV-002 GOV-003 GOV-005
        |
        +--> LOCK-GOV ------------------> CORE-001 CORE-002
        |                                  |
        |                                  v
        |                            CORE-003 CORE-004 CORE-005
        |
        +--> PYREF-000..011 ---------> LOCK-PYREF
        |                                  |
        |                                  +--> DML-007 RT-PY-001 STU-002 CTRL-007 MTH-006 DROP-001
        |
        +--> TOOL-002 TOOL-003 --------> LOCK-MIG
        |                                  |
        |                                  +--> TOOL-004..011 --> STU-007 release-support
        |
        +--> CAP-001 CAP-002 CAP-003 --> LOCK-CAP
        |                                  |
        |                                  +--> RT-001 RT-002 RT-003 --> LOCK-RT
        |                                  |        |            |
        |                                  |        v            v
        |                                  |   RT-PY-001    RT-WASM-001
        |                                  |        |            |
        |                                  |        v            v
        |                                  |   STU-002       WEB-002
        |                                  |
        |                                  +--> UI-003 UI-004
        |
        +--> REL-001 REL-002 ----------> LOCK-REL --> REL-003..008
        |                                  |
        |                                  +--> LOCKSTEP-004
        |
        +--> IO-001 IO-002 IO-003 -----> LOCK-IO
                                           |
                                           +--> DMD-001..006
                                           +--> IO-004..006
                                           +--> IO-010 IO-011
                                           +--> FMT-001..005
                                           +--> PROV-001

LOCK-UI = UI-001 + UI-002 + LOCK-CAP + LOCK-RT + primitive decision + visual-baseline infra
LOCK-UI --> UI-003..010 --> STU-006 --> WEB-005

PROV-001..005 depend on LOCK-CAP and feed CORE/STU/WEB/CLI.
CLU-001..006 depend on LOCK-RT and feed STU/CLI/benchmarks.
CTRL-000..007 depend on LOCK-CAP/LOCK-RT and feed every binding/runtime.
CON-001 depends on LOCK-CAP and feeds CORE/STU/WEB/MTH/DML/IO/provider/controller gates.
LOCK-PYREF feeds every V1 claim that preserves an existing `nirs4all` Python behavior.
LOCK-MIG feeds data-preservation claims for legacy workspaces, predictions and bundles.
LOCK-LOCKSTEP gates every shared `dag-ml`/`dag-ml-data` contract release.
LOCK-DROP gates the `DEFAULT_ENGINE="dag-ml"` release cutover.
```

## 8. Vagues de lancement recommandees

Les prompts prets a copier sont dans
`PARALLEL_AGENT_PROMPT_PROGRAM.md`. Les questions P0 a trancher avant les locks
sont dans `REFACTORING_DECISIONS_TO_ARBITRATE.md`.

### Vague 0 - Preflight et gel des bases

Agents recommandes: 3 a 5.

- `A0`: coordinateur programme.
- `A1`: ratifier `PRE-1`: backend `dag-ml` selectionnable, default legacy,
  gaps fallback/export/cutover exacts.
- `A2`: ratifier `PRE-2` Studio pristine et figer les tests/screenshots utiles
  au lieu de supposer une branche sale.
- `A3`: ratifier `PRE-3`: adopter l'oracle existant, importer le registre
  d'incompatibilites, lister les surfaces manquantes.
- `A4`: preparer branches/worktrees et hygiene git.

Sortie: un sync doc qui dit "go" ou liste les prerequis manquants.

### Vague 1 - Locks de contrat

Agents recommandes: 9 a 12 en parallele.

- `GOV`: naming/ADR/licences.
- `CAP`: capabilities/portability/unsupported.
- `REL`: manifest/lockfile schema.
- `LOCKSTEP`: schemas/fixtures `dag-ml` <-> `dag-ml-data`.
- `IO-SPEC`: `DatasetSpec v2` + `DatasetPackage`.
- `RT-SPEC`: runtime API commune.
- `UI-SPEC`: scope `nirs4all-ui`, taxonomy composants, extraction order,
  baseline visuelle Studio.
- `PROV-SPEC`: contracts providers/plugins datasets/repository/benchmarks/papers.
- `CLU-SPEC`: durcissement du client/server/workers existant, droits et capabilities.
- `CTRL-SPEC`: adapter `OperatorController -> ControllerManifest`, registry,
  transports et authoring guide.
- `CON`: conformance pack skeleton.
- `PYREF`: adoption de l'oracle existant, comparateurs, registre 3-tier et commandes.
- `MIG-SPEC`: politique legacy migration, manifest/report, target schema,
  support window et refus runtime V1.
- `DROP-SPEC`: criteres de cutover `DEFAULT_ENGINE="dag-ml"` et retrait legacy.

Sortie: `LOCK-GOV`, `LOCK-CAP`, `LOCK-PYREF`, `LOCK-REL`, `LOCK-IO`,
`LOCK-MIG`, `LOCK-DROP`, `LOCK-LOCKSTEP`, `LOCK-RT`, `LOCK-UI` ou blockers explicites.

### Vague 2 - Implementation parallele a faible conflit

Agents recommandes: 10 a 14.

- `CORE`: aggregate core.
- `REL`: outils ecosystem.
- `IO`: multimodal v2 M0/M1.
- `DMD`: providers and fingerprints.
- `FMT`: readers/sidecars pour les profils choisis.
- `MTH`: parity/kernels/artifact ledger.
- `PYREF`: dual-run parity harness et port des tests Python existants.
- `RT-PY`: runtime Python.
- `RT-WASM`: runtime browser.
- `UI`: package + premiers composants extraits avec fixtures/snapshots.
- `PROV`: provider/plugin clients datasets/repository/benchmarks/papers.
- `CLU`: cluster client/server contract if in scope for the wave.
- `CTRL`: controller registry + first idiomatic binding controllers.
- `TOOLS`: scaffold `nirs4all-tools` + migrateur legacy dry-run/verify.
- `DROP`: dry-run cutover sur branche d'integration, sans release publique.
- `LOCKSTEP`: CI contract-equivalence branchee sur les deux repos.

Sortie: artefacts autonomes avec tests locaux et smokes d'integration legers.

### Vague 3 - Reassembly produit

Agents recommandes: 6 a 9.

- `STU`: runtime Python + UI + lifecycle.
- `WEB`: runtime WASM + UI + unsupported.
- `CORE`: release train + conformance pack.
- `PYREF`: suite integration complete sur les workflows Python actuels et les
  workflows Studio qui les declenchent.
- `PROV`: repository/benchmarks/papers/datasets integration.
- `CLU`: Studio/CLI optional cluster adapter.
- `CTRL`: Studio/Web controller visibility and binding conformance.
- `TOOLS`: migration de vrais workspaces/bundles legacy et integration refus
  Studio avec commande de migration.
- `REL`: dry-run release + SBOM/provenance.

Sortie: Studio/Web lisent les memes capabilities et affichent le meme langage
de portabilite.

### Vague 4 - Release et preuve publique

Agents recommandes: 4 a 6.

- release train;
- docs publiques;
- exemple scientifique;
- provider/plugin releases: datasets, repository, benchmarks, papers;
- cluster trusted-LAN or hardened release status;
- `nirs4all-tools` migration release and support docs;
- `legacy-DROP` / `DEFAULT_ENGINE="dag-ml"` release gate;
- `dag-ml`/`dag-ml-data` lockstep contract release;
- audit licence/security;
- cleanup aliases/deprecations.

Sortie: MVP ecosysteme coherent, pas seulement architecture sur papier.

## 9. Protocole agent

Pour les lancements concrets, utiliser les prompts detailles de
`PARALLEL_AGENT_PROMPT_PROGRAM.md`. Le bloc ci-dessous reste le protocole minimal
si un agent doit etre lance a la main.

Chaque agent top-level doit recevoir:

1. sa lane et ses IDs de taches;
2. les repos qu'il peut modifier;
3. les fichiers qu'il ne doit pas toucher sans lock;
4. les gates locaux a executer;
5. le format de mise a jour du sync doc.

Prompt type:

```text
Tu es l'agent de lane <LANE>. Lis d'abord AGENTS.md/CLAUDE.md du repo cible,
puis lis nirs4all-ecosystem/docs/PARALLEL_REFACTORING_ROADMAP.md et
PARALLEL_REFACTORING_SYNC.md.

Objectif: livrer <TASK_IDS>.
Ne modifie que <REPOS/FICHIERS>. Si tu dois changer un contrat cross-repo,
arrete-toi, ajoute une proposition DEC-* dans le sync doc, puis attends
l'arbitrage du coordinateur.

Avant de rendre: execute les gates locaux, mets a jour ta ligne de lane dans le
sync doc, ajoute un worklog court, liste tests et blockers.
```

Sous-agent type pour une lane:

```text
Tu es sous-agent de <LANE>. Travail read-only sauf demande explicite.
Inspecte <SCOPE>, trouve les interfaces, tests, risques et fichiers a toucher.
Rends une reponse structuree: findings, suggested tasks, gate commands,
conflicts, open questions. Ne modifie rien.
```

## 10. Regles de modification des documents partages

Pour limiter les conflits:

- `PARALLEL_REFACTORING_ROADMAP.md` change seulement par le coordinateur ou via
  decision `DEC-*`.
- `PARALLEL_REFACTORING_SYNC.md` est le document vivant.
- Un agent modifie uniquement sa ligne de lane, les blockers qui le concernent
  et ajoute un log append-only.
- Les specs longues doivent vivre dans des fichiers dedies, pas dans le sync doc.
- Les decisions de contrat ont un ID stable: `DEC-GOV-001`, `DEC-IO-001`, etc.
- Une decision est `proposed`, `accepted`, `rejected` ou `superseded`.
- Un lock est actif seulement si le sync doc indique son ID de decision source.

## 11. Gates minimum par type de changement

| Type de changement | Gates minimum |
|---|---|
| Rust core/contracts | `cargo fmt --all --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace`, CLI smoke si present |
| Python `nirs4all` | `ruff check .`, `mypy nirs4all`, `pytest tests/unit/`, integration cible |
| Migration backend `dag-ml` / runtime Python / controllers | oracle `PYREF`: tests unit/integration existants de `nirs4all`, dual-run legacy vs `dag-ml`, registre 3-tier, XPASS strict-xfail = red, boundary native/fallback jamais xfailed, exact-count pins, `.so` freshness |
| Cutover legacy-DROP | `EXPECTED_FALLBACK == empty`, export `.n4a` natif pour les cas requis, cross-engine bundle/workspace verts, default `dag-ml` suite complete, migration tool disponible |
| `dag-ml` / `dag-ml-data` contracts | `validate_contracts.py` avec sibling, conformance pack hashes, schema/fixture equivalence hors `$id` repo |
| Migration legacy data/tooling | dry-run, verify-only, no in-place writes, old->new ID manifest, prediction tensor checksums, metric parity, artifact hash preservation, unsupported report |
| Studio | `npm run lint:parallel`, `npm run test:parallel`, Playwright/screenshot si UI visible |
| Extraction `nirs4all-ui` | lint/typecheck/test composants, fixtures de props runtime/core, screenshots baseline Studio pour composants extraits, adoption reelle dans Studio |
| Web | typecheck, Vitest, build, browser smoke selon repo |
| `nirs4all` R/WASM surfaces | R package smoke si toolchain disponible ou CI exception documentee, WASM typecheck/build/browser smoke, meme capability matrix que Python |
| IO/formats/datasets | validation schemas/goldens, fixtures, binding smokes touches |
| ABI/bindings | ABI snapshot, cross-binding smoke, version matrix |
| Docs/spec only | link check manuel, consistency avec roadmap/sync, decision IDs |

Si un gate est trop lourd pour une iteration, l'agent doit documenter pourquoi
et executer le smoke le plus proche.

## 12. Definition of done programme

Le refactoring massif est "MVP done" quand:

1. le backend Python `nirs4all` converge vers `dag-ml` sans rupture publique
   non documentee, et l'oracle `PYREF` prouve la parite des pipelines Python
   actuels avec operators sklearn selon le modele 3-tier;
2. les tests unitaires/integration existants de `nirs4all` restent verts, avec
   seulement des adaptations de signatures acceptees explicitement;
3. le futur core aggregate est nomme, locke, reproductible et testable;
4. manifest + lockfile reconstruisent l'aggregate;
5. capabilities/unsupported sont consommes par core, runtimes, Studio et Web;
6. `nirs4all-ui` contient des composants extraits, organises et consommes par
   Studio, avec fixtures et baseline visuelle;
7. `nirs4all-io` produit au moins spectra + image multimodal valide de bout en
   bout, puis cube/time-series selon scope MVP;
8. Studio utilise runtime Python + premiers composants `nirs4all-ui`;
9. Web utilise runtime WASM + les memes concepts UI/capabilities;
10. les distributions publiques `nirs4all` Python, R et WASM/browser sont dans
    la matrice de release, avec gates ou exceptions explicites pour chacune;
11. un bundle Python est inspectable hors Python avec warnings portabilite;
12. un cas scientifique multimodal est reproductible ou publiable;
13. les anciens workspaces/bundles supportes migrent via `nirs4all-tools` sans
    perte silencieuse de predictions/pipelines/metrics;
14. le cutover `DEFAULT_ENGINE="dag-ml"` est possede par `LOCK-DROP`, ou sinon
    explicitement marque hors MVP avec default legacy maintenu;
15. les contrats `dag-ml`/`dag-ml-data` sont verifies en lockstep;
16. les claims publics correspondent aux gates executes.

## 13. Sources locales utilisees

- `SYNTHESE_MULTIMODALE_NIRS4ALL.md`
- `nirs4all-ecosystem/docs/REFACTORING_ROADMAP_CRITICAL_REVIEW.md`
- `nirs4all-ecosystem/docs/REFACTORING_DECISIONS_TO_ARBITRATE.md`
- `nirs4all-ecosystem/docs/PARALLEL_AGENT_PROMPT_PROGRAM.md`
- `nirs4all-ecosystem/docs/NIRS4ALL-ECOSYSTEM_VISION.md`
- `nirs4all-ecosystem/docs/MIGRATION_BACKLOG.md`
- `nirs4all-ecosystem/docs/MIGRATION_BACKLOG_CODEX_REVIEW.md`
- `nirs4all-ecosystem/docs/ECOSYSTEM_RESTRUCTURE_LOG.md`
- `ECOSYSTEM_BLUEPRINT.md`
- `LITE_CONVERGENCE_STRATEGY.md`
- `DAG-ML_SYNC.md`
- `NIRS4ALL_IO_MULTIMODAL_BACKLOG.md`
- `AGENTS.md` / `CLAUDE.md` des repos principaux consultes via inventaire local
