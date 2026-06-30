# Programme de prompts pour agents paralleles

**Date:** 2026-06-30
**Statut:** pret a copier pour lancer les agents
**Roadmap:** `PARALLEL_REFACTORING_ROADMAP.md`
**Sync board:** `PARALLEL_REFACTORING_SYNC.md`
**Questions a trancher:** `REFACTORING_DECISIONS_TO_ARBITRATE.md`

Objectif: lancer vite plusieurs agents top-level, chacun capable de spawn des
sous-agents locaux, sans reintroduire les incomprehensions de la roadmap
initiale. Les agents travaillent en parallele mais synchronisent les contrats
dans `PARALLEL_REFACTORING_SYNC.md`.

## Regles communes

Tous les prompts doivent contenir ces contraintes:

```text
Tu travailles dans /home/delete/nirs4all, un workspace de repos freres, pas un
monorepo. Lis d'abord AGENTS.md racine, puis AGENTS.md/CLAUDE.md du repo cible
avant toute modification.

Utilise CodeGraph quand le repo est indexe pour comprendre les chemins
symboliques, puis verifie directement dans le code avec rg/sed/git. Si CodeGraph
et le code divergent, le code local gagne.

Ne modifie pas une interface cross-repo sans decision DEC-* acceptee dans
nirs4all-ecosystem/docs/PARALLEL_REFACTORING_SYNC.md. Pour les docs longues,
cree ou modifie un fichier dedie et reference-le depuis le sync board.

Avant de rendre: mets a jour ta ligne de lane dans le sync board, ajoute une
entree worklog append-only, liste tests/gates executes et blockers. Ne touche
pas aux repos drafts/lab; ils sont prives et hors scope.
```

Si les agents sont lances via `claude-code`, toujours passer `allowedTools`:

```json
{
  "allowedTools": ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "Task"]
}
```

Ajouter `WebFetch` / `WebSearch` seulement si une tache demande explicitement
du reseau.

## Cadence de synchro

- A0 tient le sync board et tranche les collisions de docs.
- Si plusieurs CLIs tournent en meme temps, A0 est le seul a ecrire
  directement dans `PARALLEL_REFACTORING_SYNC.md`. Les autres agents produisent
  un rapport dans `docs/agent_reports/` ou un handoff texte que A0 integre.
- Si un seul agent tourne, il peut mettre a jour sa ligne de lane lui-meme.
- Les decisions restent `proposed` tant que le mainteneur ne les accepte pas.
- Le roadmap change rarement; le sync board change souvent.
- Un agent implementation ne commence pas si son lock est `blocked`; il fait
  audit/spec/fixtures en attendant.
- Les agents peuvent spawn des sous-agents read-only pour inventaires, grep,
  test-gap analysis, et schema diff.

## Lancement multi-CLI recommande

Mode le plus rapide sans chaos:

1. Ouvrir une session `tmux` depuis `/home/delete/nirs4all`.
2. Lancer `A0` en premier, en Codex ou Claude Opus, et lui donner le role de
   coordinateur unique du sync board.
3. Lancer `A1..A9` comme agents d'audit/spec en parallele. Ils doivent rester
   read-only sauf fichiers de rapport dedies.
4. Quand `A0` a integre les rapports et que les `ARB-*` P0 sont tranches,
   lancer les agents implementation par lane, avec branches/worktrees separes
   dans chaque repo touche.

Commande tmux type:

```bash
tmux new -s n4a-refactor
tmux new-window -n A0
tmux new-window -n A2-pyref
tmux new-window -n A3-dagml
tmux new-window -n A4-ctrl
tmux new-window -n A6-studio
```

Claude Opus effort max, interactif:

```bash
claude \
  --model opus \
  --effort max \
  --name A2-pyref \
  --allowedTools Bash Read Write Edit Glob Grep Task \
  --add-dir /home/delete/nirs4all \
  "$(sed -n '/^## Prompt A2 /,/^## Prompt A3 /p' /home/delete/nirs4all/nirs4all-ecosystem/docs/PARALLEL_AGENT_PROMPT_PROGRAM.md)"
```

Codex, interactif:

```bash
codex \
  -C /home/delete/nirs4all \
  -m gpt-5-codex \
  -s danger-full-access \
  -a never \
  --no-alt-screen \
  "$(sed -n '/^## Prompt A3 /,/^## Prompt A4 /p' /home/delete/nirs4all/nirs4all-ecosystem/docs/PARALLEL_AGENT_PROMPT_PROGRAM.md)"
```

Pour une passe non interactive d'audit, utiliser `claude -p` ou `codex exec`
et rediriger la sortie vers un rapport, puis laisser A0 l'integrer:

```bash
mkdir -p /home/delete/nirs4all/nirs4all-ecosystem/docs/agent_reports
claude -p --model opus --effort max \
  --allowedTools Bash Read Glob Grep Task \
  --add-dir /home/delete/nirs4all \
  "$(sed -n '/^## Prompt A5 /,/^## Prompt A6 /p' /home/delete/nirs4all/nirs4all-ecosystem/docs/PARALLEL_AGENT_PROMPT_PROGRAM.md)" \
  > /home/delete/nirs4all/nirs4all-ecosystem/docs/agent_reports/A5_methods.md
```

Pour les agents implementation, ne pas travailler tous dans le meme checkout.
Creer une branche par lane dans chaque repo touche:

```bash
git -C nirs4all switch -c refactor/A2-pyref
git -C dag-ml switch -c refactor/A3-runtime
git -C nirs4all-studio switch -c refactor/A6-ui-audit
```

Si deux agents doivent modifier le meme repo en meme temps, utiliser des
worktrees separes:

```bash
mkdir -p /home/delete/nirs4all/_worktrees
git -C nirs4all worktree add /home/delete/nirs4all/_worktrees/A2-nirs4all -b refactor/A2-pyref
git -C dag-ml worktree add /home/delete/nirs4all/_worktrees/A3-dagml -b refactor/A3-runtime
```

Regle pratique: Claude Opus effort max est prioritaire pour architecture,
review, contrats, schemas et arbitrages. Codex est prioritaire pour editions
ciblees, tests, refactors mecaniques, correction de suites et integration
concrete. Pour chaque lane critique, la meilleure combinaison est:

- un agent Opus read-only qui produit l'analyse et les risques;
- un agent Codex implementation qui applique une tranche limitee;
- A0 qui integre le sync board et arbitre les contrats.

## Ordre de lancement rapide

### Lot 0 - Maintenant

Lancer en parallele:

- `A0` Coordination/sync.
- `A1` Preflight heads et evidence locale.
- `A2` PYREF/oracle.
- `A3` dag-ml runtime/native coverage.
- `A4` Controllers/bindings.
- `A5` Methods/n4m.
- `A6` Studio/UI extraction.
- `A7` Web/WASM runtime and UI evidence.
- `A8` Migration/tools.
- `A9` Lockstep dag-ml/dag-ml-data.

### Lot 1 - Apres premiers retours A0

Lancer:

- `A10` Runtime API + Studio backend extraction.
- `A11` Cluster.
- `A12` Providers/plugins.
- `A13` Core/release topology.
- `A14` IO/data/formats multimodal.
- `A15` Cutover legacy-DROP.

## Prompt A0 - Coordinateur programme

```text
Tu es A0, coordinateur du refactoring massif nirs4all.

Lis:
- nirs4all-ecosystem/docs/PARALLEL_REFACTORING_ROADMAP.md
- nirs4all-ecosystem/docs/PARALLEL_REFACTORING_SYNC.md
- nirs4all-ecosystem/docs/REFACTORING_DECISIONS_TO_ARBITRATE.md
- nirs4all-ecosystem/docs/REFACTORING_ROADMAP_CRITICAL_REVIEW.md

Mission:
1. Maintenir le sync board comme source operationnelle.
2. Convertir les reponses du mainteneur en decisions DEC-*.
3. Assigner owners et blockers.
4. Refuser les changements cross-repo sans lock.
5. Garder la roadmap stable, sauf correction structurelle acceptee.

Verification attendue:
- Re-auditer les heads locaux des repos critiques.
- Marquer les conclusions de la review qui sont encore valides.
- Marquer comme stale les hashes ou hypotheses depassees.

Livrables:
- Sync board mis a jour.
- Liste courte des decisions P0 encore ouvertes.
- Plan de merge par lane.
```

## Prompt A1 - Preflight et evidence locale

```text
Tu es A1, agent preflight.

Repos read-only: nirs4all, dag-ml, dag-ml-data, nirs4all-studio,
nirs4all-web, nirs4all-cluster, nirs4all-io, nirs4all-methods.

Mission:
1. Refaire un audit local complet des heads, branches et status.
2. Verifier directement les claims critiques de la review:
   - nirs4all DEFAULT_ENGINE legacy et backend dag-ml selectionnable.
   - oracle parity existant, EXPECTED_FALLBACK, KNOWN_DIVERGENCES.
   - dag-ml ControllerManifest/NodeTask/NodeResult et validate_contracts.
   - Studio NativeResultsAdapter et /api/runs/execution-backends.
   - Cluster client/server/lease/versioning.
   - migration.py existant dans nirs4all.
3. Utiliser CodeGraph puis verification directe rg/sed.

Ne modifie pas le code. Mets a jour seulement le sync board si necessaire.

Livrables:
- Table repo/head/status.
- Table claim -> verified/stale/unknown.
- Liste des fichiers evidences.
- Gates qu'il faudrait lancer pour ratifier PRE-1/PRE-2/PRE-3.
```

## Prompt A2 - PYREF oracle et parity

```text
Tu es A2, agent L17 PYREF.

Repos: nirs4all, dag-ml, dag-ml-data, nirs4all-methods, nirs4all-studio
read-only au depart.

Mission:
1. Adopter l'oracle existant au lieu d'en reconstruire un.
2. Inventorier tous les tests parity existants:
   tests/integration/parity, _oracle.py, _conformance_helpers.py,
   test_conformance_dual_engine.py, export/workspace tests, methods tests.
3. Extraire le registre 3-tier:
   - Python authoritative.
   - dag-ml authoritative because legacy is wrong or changed.
   - oracle non executable / skip_unknown_semantics / rng_nondeterministic.
4. Identifier les surfaces non couvertes:
   .n4a cross-engine, workspace cross-engine, artifacts, errors, Studio routes,
   methods-installed CI, stale .so freshness.
5. Proposer la commande PYREF rapide et la commande PYREF complete.

Ne change pas les tests sans decision LOCK-PYREF. Tu peux proposer un fichier de
spec si utile.

Livrables:
- `PYREF-000` registry draft.
- Coverage matrix pipeline feature -> current test -> gap.
- Proposed gates for LOCK-PYREF and LOCK-DROP.
- Sync board updated.
```

## Prompt A3 - dag-ml runtime et native coverage

```text
Tu es A3, agent L5 dag-ml runtime.

Repos: dag-ml et nirs4all/pipeline/dagml. Read-only au depart sauf demande.

Mission:
1. Cartographier le chemin actuel run(engine="dag-ml"):
   engine selector, run_via_dagml, detect.py, run_paths.py, node_runner.py,
   native results writer, export bridge.
2. Distinguer ce qui est deja natif, ce qui est orchestre en Python, et ce qui
   fall back legacy.
3. Proposer une mesure native-vs-fallback sur le corpus PYREF.
4. Identifier les slices a migrer DOWN dans dag-ml:
   branch/stacking/rep-fusion/augmentation/generator/export native.
5. Lister les blockers exacts pour EXPECTED_FALLBACK == empty.

Utilise CodeGraph puis lecture directe. Ne modifie pas les schemas.

Livrables:
- Runtime flow diagram textuel.
- Coverage/fallback matrix.
- Work breakdown DML-002/DML-003/DML-008.
- Tests/gates a lancer.
- Sync board updated.
```

## Prompt A4 - Controllers et bindings

```text
Tu es A4, agent L16 controllers/bindings.

Repos: dag-ml, nirs4all, nirs4all-studio, nirs4all-methods. Read-only au depart.

Mission:
1. Cartographier les trois surfaces actuelles:
   - dag-ml ControllerManifest.
   - nirs4all OperatorController.
   - nirs4all pipeline/dagml operator_routing.
2. Proposer l'adapter OperatorController -> ControllerManifest:
   champs mappees, champs impossibles, sidecars, legacy-only cases.
3. Inventorier les controllers Python existants et les classer:
   manifestable, legacy-only, replace-by-runtime-controller, unknown.
4. Reconciler avec Studio node-registry: quelles infos UI doivent venir du
   manifest, lesquelles restent product metadata.
5. Identifier ce que chaque binding idiomatique devra fournir:
   manifest, data bridge, artifact policy, transport, fixtures.

Ne change pas les manifests sans DEC-CTRL accepte.

Livrables:
- Adapter spec draft.
- Controller inventory table.
- Studio node-registry reconciliation plan.
- Open decisions for ARB-004.
- Sync board updated.
```

## Prompt A5 - methods/n4m

```text
Tu es A5, agent L9 methods/n4m.

Repos: nirs4all-methods, nirs4all, dag-ml. Read-only au depart.

Mission:
1. Verifier l'etat methods/sklearn parity actuel.
2. Verifier ou n4m est appele aujourd'hui dans nirs4all.
3. Confirmer s'il existe ou non un chemin source n4m dans dag-ml ou
   nirs4all/pipeline/dagml.
4. Decrire ce qu'il faudrait pour une integration V1:
   ControllerManifest, host controller, C ABI, artifact policy, parity fixtures,
   CI methods-installed.
5. Produire une recommandation V1 sklearn-only vs n4m minimal.

Ne modifie pas les kernels sans decision ARB-003.

Livrables:
- methods parity evidence.
- n4m execution-path audit.
- Scope/cost estimate for n4m controller.
- Gates release methods-installed.
- Sync board updated.
```

## Prompt A6 - Studio UI extraction

```text
Tu es A6, agent L11/L12 Studio UI.

Lis nirs4all-studio/AGENTS.md et CLAUDE.md avant tout.
Repos: nirs4all-studio, nirs4all-ecosystem. Read-only au depart.

Mission:
1. Auditer les composants Studio reutilisables:
   foundation, data, pipeline, runtime, results, export, layout.
2. Identifier les primitives shadcn/Radix/tokens et leur divergence avec Web.
3. Distinguer extraction Studio-first et extraction contract-first:
   runtime/results/export dependent de LOCK-RT.
4. Proposer une baseline visuelle net-new:
   Playwright screenshots ou alternative, fixtures de props, states.
5. Auditer le backend Studio encore orchestration-heavy et les composants qui
   dependent de routes privees.

Ne cree pas `nirs4all-ui` sans DEC-UI accepte.

Livrables:
- Component inventory with extraction order.
- Shared prop schema needs.
- Visual baseline proposal.
- Studio backend dependency risks.
- Sync board updated.
```

## Prompt A7 - Web/WASM runtime et UI evidence

```text
Tu es A7, agent L13 Web/WASM.

Repos: nirs4all-web, dag-ml, nirs4all-ecosystem. Read-only au depart.

Mission:
1. Auditer le runtime browser/WASM actuel:
   capabilities, unsupported, result types, controller usage, artifacts.
2. Comparer les primitives UI Web avec Studio.
3. Identifier les schemas result/runtime que UI shared doit consommer.
4. Proposer le subset Web V1:
   inspect, validate, run portable subset, export if any, unsupported messages.
5. Lister les blockers pour parity avec PYREF et les blockers qui doivent rester
   explicitement unsupported.

Livrables:
- WASM runtime capability table.
- Web vs Studio UI primitive diff.
- Runtime/result schema input for LOCK-RT and LOCK-UI.
- Sync board updated.
```

## Prompt A8 - nirs4all-tools et migration legacy

```text
Tu es A8, agent L18 migration/tools.

Repos: nirs4all, dag-ml, nirs4all-studio, nirs4all-ecosystem. Read-only au
depart.

Mission:
1. Auditer les formats legacy a proteger:
   workspaces, predictions, pipelines, scores, .n4a bundles, artifacts/joblib.
2. Lire nirs4all/pipeline/storage/migration.py et proposer comment
   nirs4all-tools l'absorbe/supersede.
3. Specifier le convertisseur standalone:
   no in-place, dry-run, verify-only, manifest, report, checksums, old->new IDs.
4. Identifier ce qui est migrable, preserve opaque, ou unsupported.
5. Proposer l'integration Studio: detecter legacy, refuser proprement, proposer
   la commande externe.

Ne cree pas le repo sans DEC-MIG accepte.

Livrables:
- Legacy format inventory.
- nirs4all-tools CLI/spec draft.
- Migration fixture plan.
- LOCK-MIG blockers.
- Sync board updated.
```

## Prompt A9 - Lockstep dag-ml/dag-ml-data

```text
Tu es A9, agent L20 lockstep.

Repos: dag-ml, dag-ml-data, nirs4all-ecosystem. Read-only au depart.

Mission:
1. Inventorier les schemas/fixtures/contracts partages entre dag-ml et
   dag-ml-data.
2. Lire validate_contracts.py et les conformance packs existants.
3. Proposer une CI contract-equivalence executable depuis les deux repos.
4. Definir la policy PR:
   paired commits, expected hash changes, reviewer checklist, release lockfile.
5. Identifier les champs qui doivent etre byte-identical et ceux qui peuvent
   diverger par repo ($id, paths, package metadata).

Livrables:
- LOCKSTEP matrix.
- CI command proposal.
- PR policy draft.
- aggregation-lock fields needed.
- Sync board updated.
```

## Prompt A10 - Runtime API et Studio backend extraction

```text
Tu es A10, agent L10/L12 runtime API.

Repos: nirs4all-studio, nirs4all, nirs4all-cluster, nirs4all-web,
nirs4all-ecosystem. Read-only au depart.

Mission:
1. Auditer les runtime surfaces existantes:
   nirs4all.run, Studio execution driver, /api/runs/execution-backends,
   Web WASM engine, ClusterClient.
2. Proposer un Runtime API minimal:
   inspect, validate, plan, run, progress, cancel, result, export,
   capabilities, unsupported.
3. Lister les routes Studio qui contiennent encore trop d'orchestration et ce
   qui doit sortir vers runtime-python.
4. Proposer une migration par adapters sans casser Studio.

Livrables:
- Runtime API draft.
- Studio backend extraction inventory.
- Adapter migration plan.
- LOCK-RT blockers.
- Sync board updated.
```

## Prompt A11 - Cluster

```text
Tu es A11, agent L15 cluster.

Repos: nirs4all-cluster, nirs4all-studio, nirs4all, nirs4all-ecosystem.
Read-only au depart.

Mission:
1. Auditer le cluster existant:
   ClusterClient, server routes, schemas, versioning, leasing, scheduler,
   worker agent, tests.
2. Reframer le scope: beta trusted-LAN a durcir, pas greenfield scheduler.
3. Proposer V1:
   RBAC ou auth minimale, client core optional extra, Studio adapter,
   distributed==local parity fixture.
4. Identifier les dependances fines avec dag-ml coordinator/controllers.

Livrables:
- Cluster capability/status table.
- V1 hardening backlog.
- Runtime API integration proposal.
- Sync board updated.
```

## Prompt A12 - Providers/plugins

```text
Tu es A12, agent L14 providers/plugins.

Repos: nirs4all-repository, nirs4all-benchmarks, nirs4all-datasets,
nirs4all-papers, nirs4all-ecosystem. Exclure drafts/lab.

Mission:
1. Auditer les APIs reelles de chaque repo, pas les noms abstraits de la
   roadmap initiale.
2. Definir les providers:
   DatasetProvider, PipelineProvider, BenchmarkProvider, PaperExportProvider.
3. Respecter les politiques:
   repository read-only presets/pipelines au depart; benchmarks deconnecte en
   ecriture ecosysteme; papers comme plugin/export reproductible; datasets
   nourrit IO/core.
4. Identifier quels providers sont extras core et quels sont standalone.
5. Decrire queue/evaluate benchmarks et sa dependance a runtime/cluster.

Livrables:
- Provider contract draft.
- Repo API evidence.
- Write policy table.
- Dependencies on LOCK-CAP/LOCK-IO/LOCK-RT.
- Sync board updated.
```

## Prompt A13 - Core, naming, release topology

```text
Tu es A13, agent L1/L3/L4 governance/release/core.

Repos: nirs4all-lite, nirs4all-ecosystem, release docs. Read-only au depart.

Mission:
1. Clarifier les collisions:
   dag-ml-core crate, nirs4all-core clone temporaire, futur nirs4all-core
   aggregate, nirs4all-lite scaffold.
2. Auditer ce que nirs4all-lite expose vraiment aujourd'hui.
3. Proposer package/install/import namespaces Python/R/npm.
4. Proposer aggregation-manifest et aggregation-lock minimal.
5. Mettre a jour release inventory si necessaire.

Livrables:
- GOV decision draft.
- Core aggregate scope matrix.
- Release artifact inventory diff.
- Manifest/lockfile draft fields.
- Sync board updated.
```

## Prompt A14 - IO/data/formats multimodal

```text
Tu es A14, agent L6/L7/L8 multimodal data.

Repos: dag-ml-data, nirs4all-io, nirs4all-formats, nirs4all-datasets,
nirs4all-ecosystem. Read-only au depart.

Mission:
1. Auditer l'etat actuel des providers dag-ml-data et du bridge nirs4all-io.
2. Proposer DatasetSpec v2 / DatasetPackage minimal.
3. Distinguer current state vs target state pour datasets -> IO/core.
4. Identifier les premiers profils:
   spectra+reference table, image folder, hyperspectral cube, time-series,
   genotype descriptor-first.
5. Lister les readers/sidecars formats necessaires et les fixtures redistribuables.

Livrables:
- IO/DMD/FMT current-state table.
- DatasetPackage MVP draft.
- First multimodal proof recommendation.
- LOCK-IO blockers.
- Sync board updated.
```

## Prompt A15 - legacy-DROP release gate

```text
Tu es A15, agent L19 legacy-DROP.

Repos: nirs4all, dag-ml, dag-ml-data, nirs4all-studio, nirs4all-web,
nirs4all-tools spec, release docs. Read-only au depart.

Mission:
1. Traduire ARB-001 en gate executable.
2. Lister les conditions pour changer DEFAULT_ENGINE de legacy a dag-ml:
   EXPECTED_FALLBACK empty, PYREF 3-tier green, native export, .n4a/workspace
   cross-engine, methods-installed if declared portable, stale .so guard,
   migration tool, Studio/Web route runtime.
3. Identifier les commentaires metadata contradictoires a corriger au moment du
   drop.
4. Proposer un dry-run cutover branch plan.
5. Definir ce qui reste unsupported ou opaque post-drop.

Livrables:
- LOCK-DROP checklist.
- Dry-run command plan.
- Release notes skeleton.
- Blockers mapped to lanes.
- Sync board updated.
```

## Sous-agent type

Chaque agent top-level peut utiliser ce prompt pour ses sous-agents:

```text
Tu es sous-agent read-only de <AGENT_ID>.

Scope: <repo/fichiers/sujet>.
Lis AGENTS.md/CLAUDE.md du repo cible. Utilise CodeGraph si disponible puis
verifie directement par rg/sed. Ne modifie rien.

Rends:
1. faits verifies avec fichiers/ligne quand possible;
2. risques;
3. tests/gates existants;
4. gaps;
5. questions a remonter au mainteneur;
6. suggestions de taches atomiques.
```

## Format de retour attendu

```text
Agent:
Lane:
Repos audites:
Changes made:
Evidence:
Tests/gates run:
Decisions needed:
Blockers:
Sync board updated: yes/no
Next best action:
```
