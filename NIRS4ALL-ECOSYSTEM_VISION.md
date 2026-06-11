# Vision et stratégie — Écosystème nirs4all

## 1. Vision en une page

L'écosystème nirs4all a trois ambitions superposées :

1. **Faire de `nirs4all` (lib Python) + `nirs4all-studio` (Electron) une option de référence open-source pour la NIRS appliquée** — visant à compléter, voire concurrencer sur certains usages, les outils propriétaires établis (PLS_Toolbox, Unscrambler, SIMCA) et les briques open-source existantes (R `prospectr`/`mdatools`/`pls`/`hyperSpec`, Python `SpectroChemPy`, Orange-Spectroscopy/Quasar, HyperSpy/Spectral Python), avec une intégration native des frameworks ML/DL modernes (sklearn, PyTorch, JAX, TabPFN) et une reproductibilité par construction.
2. **Construire en dessous une couche d'infrastructure réutilisable hors du domaine NIRS** : `dag-ml` (cœur Rust de coordination ML reproductible, OOF-safe) et `dag-ml-data` (contrats de données alignées par identité). Une fondation publiable en informatique/ML, indépendante du domaine.
3. **Porter le tout vers tous les écosystèmes scientifiques utiles** : Python léger, R, MATLAB/Octave, Julia, C/C++, WASM, Android — par bindings minces hébergés dans `nirs4all-methods` / `nirs4all-formats`, et via `nirs4all-lite` qui distribue **la chaîne des packages bas-niveau** (`nirs4all-formats` + `nirs4all-io` + `nirs4all-methods` + `dag-ml` [+ `dag-ml-data`]) en bundles installables par langage cible (PyPI sous `nirs4all-lite`, CRAN/R-universe sous `nirs4all`, MATLAB toolbox, Julia Pkg, npm sous `nirs4all`, Conda, Docker, vcpkg/Conan/Homebrew, .deb/.rpm). **Le « lite » est sémantique : hors bibliothèque Python complète `nirs4all`, on perd sklearn/PyTorch/TF/JAX, donc capability réduite ; ce n'est ni un sous-ensemble du code, ni une réécriture.** Zéro code numérique nouveau. Les recettes de build, release et supply-chain vivent dans `nirs4all-lite` tant qu'elles servent cette distribution.

À long terme : `nirs4all-studio` devient un atelier scientifique multi-modal (séries temporelles, hyperspectral, génomique, tabulaire) grâce à `dag-ml` / `dag-ml-data`, et `nirs4all-arena` devient un dépôt public de pipelines + datasets reproductibles, avec une matrice de comparaison méthodes × datasets curée en interne et publiée en lecture (pas une plateforme de compétition externe).

---

## 2. Cartographie de l'écosystème

Quatre couches logiques. Chaque dépôt vit en parallèle dans `~/nirs4all/` ; `nirs4all-ecosystem` est le parent qui les épingle en submodules.

### Couche 0 — Fondations agnostiques (Rust)

| Dépôt | Rôle | État |
|---|---|---|
| `dag-ml` | Cœur Rust : compilation de graphe, scheduling, replay, lignage, fingerprints, validation OOF, frontière C ABI. Opérateurs externes (controllers). | actif, contrats versionnés |
| `dag-ml-data` | Schémas + contrats de données alignés par identité (sample/group/origin), planificateur de représentations, fusion multi-sources, ABI host-provider. | actif, contrats partagés avec `dag-ml` |

### Couche 1 — Lecteurs et assembleurs NIRS (Rust + Python)

| Dépôt | Rôle | État |
|---|---|---|
| `nirs4all-formats` | Lecteurs Rust de ~58 formats spectroscopiques (OPUS, JCAMP, SPC, ASD, ENVI, HDF5, MATLAB v7.3…). Parsers en Rust uniquement ; bindings Python/R/WASM/C convertissent. | actif, en validation conformance |
| `nirs4all-io` | Pont d'assemblage : input arbitraire → `RESOLVE → INFER → CONFIGURE → MATERIALIZE` → `SpectroDataset`. Python (phase 1 OK, parité avec `DatasetConfigs`), Rust (phase 2 différée). | Python alpha+, Rust planifié |
| `nirs4all-methods` (`libn4m`) | Moteur PLS / NIRS portable C++17 + ABI C stable. Bindings Python (`nirs4all-methods`, `pls4all`), R (CRAN-ready build vendored), MATLAB/Octave (MEX), JS/WASM. Julia / JNI / Android encore au stade scaffold. | refactor post-merge en cours ; 4 bindings build + parité `<1e-12` documentée publiquement (CI locale rapporte plus serré) |

### Couche 2 — Bibliothèque de référence et UI

| Dépôt | Rôle | État |
|---|---|---|
| `nirs4all` | Lib Python pipeline NIRS : `SpectroDataset`, contrôleurs, opérateurs (SNV, MSC, SG, OSC, EPO, CARS, MCUVE, augmentations physiques…), PLS variants (AOM-PLS, POP-PLS, IKPLS, MBPLS, DiPLS, SparsePLS, LWPLS, KOPLS…), exécution parallèle, workspace SQLite+Parquet, bundle `.n4a`, intégration sklearn/TF/PyTorch/JAX, SHAP. | 0.9.x, API stable, riche |
| `nirs4all-studio` | App Electron + React 19 + FastAPI au-dessus de `nirs4all`. Éditeur de pipelines drag-and-drop, dashboards, runs/predictions, playground. Le backend ne réimplémente jamais la lib. | actif, en stabilisation UI |

### Couche 3 — Données, benchmarks, papiers, communauté

| Dépôt | Rôle | État |
|---|---|---|
| `nirs4all-datasets` | Catalogue + accès *pooch-style* à des datasets NIRS sur Dataverse (Recherche Data Gouv / CIRAD), cibles : DOIs, identity cards, Croissant. Réutilise `nirs4all-io`. | stub fonctionnel : 1 dataset exemple, DOIs/cards/manifests pas encore peuplés ; repo public |
| `nirs4all-arena` | Environnement de benchmarks publiables : pipelines × datasets × méthodes, runs reproductibles via fichiers `.n4a`, site de browsing. | stub (README seul) |
| `nirs4all-aom` | Code compagnon du papier AOM-PLS / POP-PLS / AOM-Ridge / FastAOM. À migrer dans `nirs4all-methods` à terme. | beta, papier en cours |
| `nirs4all-lab` | Espace privé de prototypage : NICon, FCK-PLS, synthèse (ViTnirs), TabPFN, subset analysis, harness de benchmark. | actif, privé |
| `nirs4all-org` | Landing page statique nirs4all.org. | en ligne, anciennement `nirs4all-webpage` |
| `nirs4all-papers` | Dépôt public des papiers déposés de l'écosystème + artefacts `.n4a` reproductibles. | public, README seed ; code reproductible à migrer par papier |
| `nirs4all-drafts` | Drafts et papiers privés + artefacts `.n4a`. | privé, ancien rôle de `nirs4all-papers` |
| `nirs4all-lite` | **Distribution simplifiée multi-langages** de la chaîne bas-niveau (`nirs4all-formats` + `nirs4all-io` + `nirs4all-methods` + `dag-ml` [+ `dag-ml-data`]). Bundles installables pour Python léger (PyPI `nirs4all-lite`), R (CRAN/R-universe `nirs4all`), MATLAB/Octave, JS/WASM (npm `nirs4all`), puis Julia, C/C++ (vcpkg / Conan / Homebrew / .deb / .rpm), Conda channel, Docker images. **Le « lite » est sémantique : capability réduite hors bibliothèque Python complète, pas codebase réduit.** Zéro code numérique, zéro patch upstream. Semver strict, libs amont épinglées par tag. | public, scaffold de bindings buildable et CI verte |
| `nirs4all-cluster` | Prototype public d'exécution distribuée. Sert à cadrer les risques worker/server et des spikes contrôlés ; ne remplace pas encore un backend `nirs4all.run(executor=...)` stable. | public alpha/prototype, pas produit |

### Schéma de dépendances (chemin "live" NIRS)

```
fichiers terrain
      │
      ▼
nirs4all-formats   (lecture Rust, 58 formats)
      │
      ▼
nirs4all-io       (assemblage, inférence, parité DatasetConfigs)
      │
      ▼
nirs4all          (pipelines, opérateurs, runs, predictions, bundle .n4a)
      │
      ▼
nirs4all-studio   (UI, visualisations, project management)


            indépendants mais conçus pour s'intégrer
nirs4all-methods (libn4m)  ──►  appelable depuis nirs4all (controllers) ou en standalone
dag-ml + dag-ml-data       ──►  substrat potentiel/conditionnel d'exécution + multi-modal de nirs4all-studio
                              (conditionné au couplage effectif avec `nirs4all`, item P1 §6.4)
nirs4all-aom               ──►  méthodes AOM, futurs candidats à migrer dans nirs4all-methods
nirs4all-datasets          ──►  fournisseur consommé par nirs4all-io
nirs4all-arena             ──►  consommateur de bundles .n4a publiés
```

---

## 3. État actuel (snapshot honnête)

Ce qui est **réellement en main** aujourd'hui :

- **`nirs4all` 0.9.x** : API publique stable (`run / predict / explain / retrain / session / generate`), schémas workspace SQLite+Parquet stables, bundle `.n4a` stable. Couverture d'opérateurs NIRS très large. Parallélisme via `joblib`. Intégration sklearn/PyTorch/TF/JAX/Optuna. Pipeline DSL très expressif (`_or_`, `_grid_`, `_cartesian_`, `_zip_`, `_chain_`, `_sample_`, `branch`/`merge`, `tag`/`exclude`, `concat_transform`, `rep_to_sources`/`rep_to_pp`).
- **`nirs4all-studio`** : Electron + Vite + FastAPI fonctionnel, éditeur de pipelines drag-and-drop, registre de nœuds (statique + auto-généré depuis sklearn/nirs4all/TF), WebSocket pour progrès, packaging desktop (PyInstaller bundling). Reste de la dette UX (cf. `Roadmap.md`).
- **`nirs4all-methods`** : 4 bindings BUILD + parité numérique vérifiée (publiquement : `rmse_rel < 1e-12` côté SPEC ; CI locale R `~9e-18`, Octave `~4e-16`, JS `~1e-16`). Catalog ↔ ABI : la note de travail interne `finish-lib-progress.md` rapporte 669/669 réconciliés, les docs publiques (SPEC, release_process) sont plus prudentes (catalogued 427/669, guessed 419, unmapped 662) — **delta de fraîcheur à clarifier dans le repo avant communication externe**. Reste : matrice OS wheels macOS/Windows, soumission CRAN (formulaire), publication PyPI Trusted Publishing.
- **`nirs4all-formats`** : registre Rust + readers en place, double conformance (golden summaries + comparaison à brukeropus/spc-spectra/jcamp/spectrolab/h5py). Bindings Python/R/WASM, C ABI scaffold. Workflow release tag-déclenché prêt.
- **`nirs4all-io`** : Phase 1 Python terminée + parité octets-vs-octets avec `nirs4all.DatasetConfigs`, ~200 tests, ruff+mypy clean. Phase 2 Rust gatée.
- **`dag-ml` + `dag-ml-data`** : crates actifs, contrats JSON partagés, C ABI + bindings Python ctypes smoke, fingerprints stables, validation envelope+materialize. Niveau de maturité : **scaffold + conformance pack avancés** ; les host controller adapters production, les providers production et le connecteur depuis le DSL `nirs4all` ne sont pas implémentés. Aujourd'hui aucun pipeline `nirs4all` ne s'exécute via `dag-ml`.
- **`nirs4all-aom`** : code utilisé pour le manuscrit, 3 familles (`pls` / `ridge` / `fast`). **arXiv v2 prêt** (bundle `paper/aom_arxiv_v2.tar.gz`, abstract finalisé, repo public référencé dans `main.tex`). Pour Talanta, audit benchmark récent (28 mai) : la `paper/review/paper_review.md` initiale (17 mai) surestimait les blockers compute. **Les expériences manquantes citées par la review existent déjà** dans les workspaces archivés (Blender + AutoSelect seeds 0/1/2 sur 26 datasets dans `_archive/trashed_runs/AOM_v0_legacy/Ridge/benchmark_runs/da001_*_seeds012/`, RMSEP identique entre seeds — caveat : le split SPXY3 est déterministe par protocole, donc c'est de la *protocol determinism*, pas une robustesse à partitions répétées ; baseline conventionnelle forte couverte par `pls-tabpfn-hpo-25trials` qui fait HPO sur `norm` / `smooth` / `baseline` / `osc` / composantes — à présenter comme « search space conventionnel sous HPO », pas comme recette fixe). Reste pour Talanta : (a) re-agréger workspaces archivés dans `final_stats.md` + supplement, en dédupliquant `(dataset, variant, seed)` et en cadrant le claim sur N=26 (ou re-run les 6 datasets manquants pour atteindre N_cap=32) ; (b) promouvoir l'audit de missingness en table publiée ; (c) paragraphe + table failure-modes ; (d) citations SPORT/PORTO/PROSAC + ML-bias ; (e) reflow Figure 5 ; (f) expliciter le search space PLS-HPO dans le texte ; (g) smoke test reproductibilité repo. **Effort total ~2-3 jours humains, ~0 compute supplémentaire** (ou +6 datasets si on vise N_cap=32 strict pour le multi-seed). Détail dans le header revisé de `paper/review/paper_review.md`.
- **`nirs4all-datasets`** : structure + CLI + intégration Dataverse en place, mais le catalogue local contient **un seul dataset d'exemple** avec `doi: null`, `has_card: false`, `has_manifest: false`. Statut réel : *stub fonctionnel*, pas alpha au sens publiable.
- **`nirs4all-org`** : en ligne et aligné avec les noms publics (`nirs4all-web`, `nirs4all-lite`, `nirs4all-cluster`) ; anciennement `nirs4all-webpage`.
- **`nirs4all-web`** : ancien rôle `nirs4all-lite` browser/WASM, publié sous son nom propre ; build, single-file build et smokes navigateur validés.
- **`nirs4all-papers` / `nirs4all-drafts`** : remotes alignés avec la séparation cible (`papers` public, `drafts` privé).
- **`nirs4all-lite`** : remote public ; scaffold de distribution multi-bindings en place avec CI Rust, Python, npm/WASM, R et MATLAB/Octave. Reste : remplacer les loaders fins par des intégrations upstream complètes et ajouter les fixtures de parité pipeline.
- **`nirs4all-cluster`** : remote public ; documentation cadrée comme prototype alpha, pas comme service multi-tenant prêt.

Ce qui n'est **pas** en main aujourd'hui :

- Une **publication "logicielle" citée** (JOSS / SoftwareX) qui ancre `nirs4all` dans la littérature.
- Une **présence communautaire NIRS** mesurable (présence ICNIRS, mailing-lists chemometrics, citations).
- Une **consommation effective de `dag-ml`** par `nirs4all`. Aujourd'hui les deux mondes coexistent.
- Un **benchmark public** (l'arène) avec matrice de comparaison méthode × scenario et résultats croisés.

---

## 4. Critique objective

### 4.1 Scope vs capacité de maintenance — recalibré par le pari automation

15 dépôts (planifiés inclus), chacun avec « plein de bindings + bindings idiomatiques » — si on prend `nirs4all-methods` comme référence (4 bindings actifs + Julia/JNI/Android/Native JS prévus) et qu'on multiplie par les 4 autres bibliothèques techniques (`nirs4all-formats`, `nirs4all-io`, `dag-ml`, `dag-ml-data`), c'est un produit cartésien de **~25-30 cibles binding × projet**, plus la couche applicative. Sous un modèle de maintenance artisanale classique, **cela ne tient pas**.

L'écosystème fait un pari structurel qui change l'équation : **automation systématique par agents IA (Claude Code, Codex, etc.) sur le traitement front-line des tickets, PRs, issues, demandes, releases de routine, mises à jour de dépendances, génération de changelogs et migrations cross-repo**. Détail au §7.6.

Ce qui change avec ce pari :
- Le coût marginal d'un dépôt supplémentaire baisse fortement côté *opérations routinières* (triage, dependabot-like, doc updates, release notes, PR review de premier niveau).
- La discipline de frontières déjà en place (CLAUDE.md / AGENTS.md par dépôt, parsers en Rust uniquement, backend ne réimplémente jamais, bindings sans logique numérique, core dag-ml ne touche pas les matrices) est *exactement* le terreau dont les agents ont besoin pour opérer sous supervision et gates exécutables. *Pas un substitut à la revue ;* SWE-bench et la documentation Claude Code rappellent que les agents restent faillibles sur du vrai génie logiciel et recommandent review + tests + isolation.
- Les `release trains` groupés et la *deprecation* publique des bindings non utilisés deviennent eux-mêmes des routines agent-driven.

Ce qui ne change pas :
- Les décisions d'architecture, le cadrage scientifique, les choix de licence, la réponse à un incident sécurité, la rédaction des papiers, l'arbitrage produit, le contact industriel restent humains.
- Le coût de revue *qualifiée* des changements générés par agent reste humain et croît avec le volume.
- Une priorisation explicite des bindings par ROI communautaire reste nécessaire — l'automation n'invente pas la stratégie.

Le pari est donc défendable, mais conditionné à :
1. l'investissement continu dans les CLAUDE.md / AGENTS.md / scripts de validation par dépôt (le carburant des agents),
2. une politique de revue humaine *systématique* des changements produits par agent avant merge sur `main`,
3. une discipline de claims (cf. §7.5 décision 6) — les agents ne doivent pas réintroduire les sur-affirmations corrigées dans cette passe.

### 4.2 `dag-ml` dans un marché encombré

L'idée de positionner `dag-ml` comme publication « informatique / ML » est ambitieuse mais le marché est dense : MLflow, DVC, OpenLineage, MLMD, Hamilton, Metaflow, Flyte, Kedro, ZenML, Pachyderm, Sacred, Hopsworks, RO-Crate, W3C PROV. Le différenciateur de `dag-ml` doit être **explicite et défendable** :

- **OOF-safety vérifiable mécaniquement** plutôt que par convention.
- **Cross-language par C ABI** au cœur, là où la plupart des concurrents sont Python-centric.
- **Réfutation par défaut des chemins de fuite** (train predictions as training features), opt-in explicite et tracé sinon.

Pour qu'un papier passe, il faut un *bench empirique* : faire tourner `dag-ml` sur N pipelines réels (NIRS + autres) et montrer qu'il attrape des fuites que MLflow / DVC / Hamilton ne voient pas, ou qu'il rejoue à coût moindre. Sans ce benchmark, pas de papier. Et la venue plausible est **MLOSS / JMLR open-source track**, ou un workshop ML (e.g. NeurIPS *ML4PS*), pas OSDI/EuroSys qui demanderait une évaluation systèmes lourde non envisagée.

### 4.3 `nirs4all-lite` : la chaîne des packages bas-niveau emballée pour plusieurs écosystèmes

`nirs4all-lite` est le **produit utilisateur final** qui distribue la chaîne bas-niveau de l'écosystème — `nirs4all-formats`, `nirs4all-io`, `nirs4all-methods` (`libn4m`), `dag-ml`, `dag-ml-data` — sous une forme installable dans les écosystèmes scientifiques cibles : **Python léger (PyPI `nirs4all-lite`), R (CRAN/R-universe `nirs4all`), MATLAB / Octave (FileExchange, `.mltbx`), Julia (`Pkg`), JavaScript / WASM (npm `nirs4all`), C / C++ (vcpkg / Conan / Homebrew / .deb / .rpm), Conda channel multi-langage, images Docker**.

Ce que `nirs4all-lite` *n'est pas* :
- pas une réécriture du code Python ;
- pas un sous-ensemble du code source ;
- pas un fork.

Ce qu'il *est* : un dépôt de **distribution et de release packaging**, zéro code numérique nouveau. Une release `nirs4all-lite` = un bundle immutable qui épingle des versions précises des libs amont et les expose en un produit par langage cible.

#### Le « lite » est une sémantique de capability, pas de codebase

Hors bibliothèque Python complète `nirs4all`, on perd `sklearn` / `PyTorch` / `TensorFlow` / `JAX`. Même le binding Python `nirs4all-lite` reste donc volontairement plus restreint côté ML : lecture de formats spectroscopiques, assemblage de datasets, PLS et variants (libn4m), coordination DAG reproductible. C'est *lite* par capability, pas par code. À garder en première ligne du README pour éviter toute mécompréhension.

#### Pour qui

- Utilisateurs **Python** qui veulent la stack bas-niveau sans l'armada ML/visu/DL de `nirs4all` : `pip install nirs4all-lite`.
- Communauté **R chimiométrie** (prospectr / mdatools / pls / hyperSpec / ChemoSpec) : `install.packages("nirs4all")` consomme une seule release.
- Utilisateurs **MATLAB** qui veulent quitter PLS_Toolbox : toolbox `.mltbx` packagée.
- Démos **WASM** en ligne (page nirs4all.org) avec `nirs4all-formats` + PLS côté client.
- Intégrateurs **C / C++** (pharma PAT, industriel) : headers C ABI + libs liées via `vcpkg` / `Conan` / `Homebrew`.
- **Julia**, **Octave**, packagings OS (`.deb`, `.rpm`) à instruire ensuite.

#### Précédents OSS du modèle distribution / feedstock

Le pattern existe et est mature : **conda-forge feedstocks** (recettes + CI + validation + upload, PRs humaines + automation), **Homebrew taps** (formules externes), **NixOS nixpkgs**, **vcpkg / Conan ports**, **ROS metapackages**, **CRAN feedstocks tiers** (rstanarm / cmdstanr packaging).

#### Hygiène (à écrire dès le démarrage)

- **Aucun patch upstream** dans `nirs4all-lite`. Si un binding a besoin d'un correctif, il remonte en PR dans la lib source. Cette règle protège la distribution du drift.
- **Semver strict + tags `v1`, `v2`**. Compat matrix publiée « version `lite` × versions libs amont ». Dépréciation sur ≥ 2 minor releases. Breaking changes uniquement via nouveau major.
- **Tests sur repos fixtures** : un dépôt test minimal qui consomme chaque bundle `lite` à chaque PR — sinon impossible de valider qu'un changement ne casse pas la chaîne aval.
- **SBOM + provenance + attestations supply-chain** (Sigstore / SLSA / in-toto) sur les bundles publiés. **CVE rebuild policy** explicite (upstream dep vulnérable → rebuild). **Politique de retrait** d'artefacts cassés (yank from PyPI / Conda, vidange image Docker). **Fenêtre EOL / support** des anciens bundles explicite — N versions glissantes, dates de dépréciation publiées.
- **Matrice de compatibilité** documentée (glibc / OpenSSL / R version / MATLAB version / cibles OS). Sans ça, un bundle « marche chez moi » échoue chez l'utilisateur.
- **Droits de redistribution** : tout bundle binaire qui agrège des libs avec licences hétérogènes (CeCILL, MIT, AGPL, dépendances tierces type BLAS / Eigen) impose une vérification licence par cible. Pas optionnel.
- **Périmètre d'artefacts cibles documenté** : mieux vaut 2-3 cibles bien faites (par ex. CRAN source + Conda channel + Docker images) que 10 cibles ratées. **Règle d'admission d'une nouvelle cible** : CODEOWNER nommé pour cette cible + fixture CI dédiée + politique de release/retrait écrite avant le premier artefact publié.

#### Risque résiduel

`nirs4all-lite` devient un point de centralisation critique côté distribution. Si une release casse, *tous les utilisateurs aval* voient leur installation rompue. Mitigation : politique semver stricte + tags pinés côté libs amont + tests fixtures + automation §7.6 (les bumps de refs et la regen des recettes packaging sont précisément des tâches agent-driven adaptées, cf. mention explicite §7.6).

> **Note** — les recettes de build/release des bundles `nirs4all-lite` restent dans `nirs4all-lite`.
> Si une redondance réelle apparaît dans les dépôts amont, elle doit être factorisée par petites
> briques documentées, pas par un dépôt factory séparé recréé par défaut.

### 4.4 `nirs4all-arena` : périmètre et cadrage

L'arena est un **dépôt curé de comparaisons reproductibles** méthodes × datasets × scenarios. **Pas une plateforme de compétition type Kaggle** : pas de soumission externe, pas de runs hébergés à la demande, pas de leaderboard utilisateur, pas de SaaS. Le compute reste interne (CIRAD ou équivalent) ; le résultat est public et browsable. Cela évite les coûts d'une plateforme multi-tenant (sandboxing, modération, IP, RGPD, scaling) et reste défendable scientifiquement.

Deux aspects à séparer dans la communication :

1. **Le benchmark scientifique reproductible** — un ensemble de *scenarios* (combinaisons dataset + split + métrique) qualifiés, accompagnés d'une matrice méthode × scenario exécutée en interne et publiée. Chaque run produit un bundle `.n4a` archivable et téléchargeable. Atteignable à 6-12 mois.
2. **Le site web de browsing** — pages par dataset, par méthode, par scenario ; cross-tabs ; gain plots ; lien direct vers `.n4a` ; lien vers les datasets DOI-pinés (`nirs4all-datasets`). Atteignable à 12-18 mois quand la matrice initiale est stable.

Quatre points opérationnels à expliciter dès le démarrage (sinon l'arena n'est pas défendable scientifiquement) :

- **Protocole de qualité d'un scenario** : critère d'inclusion d'un dataset (taille, qualité du label, provenance), critère d'inclusion d'une méthode (implémentation référencée, pas de hyperparameter overfit), métrique principale et secondaire explicites, traitement des échecs (NaN, fit error, timeout) avec codes documentés.
- **Politique de splits anti-leakage** : group-aware, instrument-aware, campaign-aware, temporal-aware lorsque c'est applicable. Documenté par scenario, pas implicite. C'est ce que `dag-ml` peut garantir si couplé (cf. §6.4 P1).
- **Versionnage DOI des datasets** : chaque scenario pointe vers une *version* DOI-pinée d'un dataset via `nirs4all-datasets` (et non vers un fichier mouvant). Un dataset re-publié = un nouveau scenario, pas une mise à jour silencieuse.
- **Archivage et versionnage des `.n4a`** : chaque cellule de la matrice est un bundle `.n4a` immutable, content-addressable, archivé (Zenodo / Software Heritage / institutionnel CIRAD). Re-exécution garantie tant que les dépendances majeures restent compatibles.

Le piège à éviter : promettre publiquement *« Kaggle for NIRS »*. Le marché NIRS (≈ quelques milliers de praticiens actifs mondialement, dominé par Bruker / PerkinElmer / ABB / Foss / Metrohm) ne soutient pas un SaaS dédié, et la dérive scope/maintenance serait massive (cf. R2). L'arena tire sa valeur de la **qualité de la curation** (datasets propres, splits défensifs, méthodes représentatives, métriques transparentes), pas du volume de soumissions.

### 4.5 La matrice de bindings : prioriser par communauté, pas par symétrie

Aujourd'hui le réflexe est « tout dépôt → tous bindings ». La réalité des communautés NIRS et ML :

- **R** : la communauté chimiométrique active (mdatools, prospectr, pls, ChemoSpec) est R-first. **Priorité 1.** Une suite R polished (`nirs4all-methods` + lecteur natif + studio facultatif) ouvre les portes ICNIRS et CRAN.
- **MATLAB** : reste très implanté dans l'industrie et l'académique senior (PLS_Toolbox / Eigenvector). **Priorité 2.** Un binding MATLAB propre permet de capter une part de la base PLS_Toolbox.
- **WASM / JavaScript client-side** : levier marketing énorme (démo en ligne du studio sans installation) et viable pour preprocessing + PLS, **pas** pour DL. **Priorité 3 comme outil de démonstration**, pas comme plateforme.
- **Julia / JNI / Android** : niches. Bindings à maintenir uniquement si un utilisateur dédié les pousse.
- **Octave / Python** : déjà couverts, à stabiliser pas étendre.

### 4.6 Licences et adoption industrielle

L'écosystème mélange **CeCILL-2.1**, **AGPL-3.0**, **MIT** (formats), **dual-license commercial** (`nirs4all-aom`). Pour viser le marché industriel (instrument vendors, pharma PAT, agtech, food QC), AGPL et CeCILL sont des freins documentés. À clarifier :

- Quels dépôts seront **libres d'adoption commerciale sans contagion** (Apache-2 / MIT / BSD) ?
- Quels dépôts gardent une licence **réciproque forte** (CeCILL / AGPL) ?
- Y a-t-il un **modèle commercial** explicite (offre commerciale / support / études contractuelles via CIRAD) ?

Une politique de licence à l'échelle de l'écosystème, écrite, est un prérequis pour parler à un industriel.

### 4.7 Bus factor — à reformuler depuis le pari automation

Le risque doit être lu en deux couches :

- **Couche opérationnelle (maintenance routinière)** : *fortement assistée* par le pari automation (§4.1, §7.6), mitigée sous supervision et gates exécutables. Triage d'issues, PR review premier niveau, bumps de dépendances, releases tagged, mises à jour de docs, changelogs, migrations cross-repo *bornées* se font via agents avec revue humaine obligatoire avant merge `main`. La chaîne ne fonctionne que tant que CLAUDE.md / AGENTS.md / golden gates sont à jour.
- **Couche stratégique (décisions, vision, science, sécurité)** : **non mitigée**. Une seule personne porte aujourd'hui les choix d'architecture, le cadrage scientifique des papiers (AOM, DSL, JOSS, benchmark arena), les arbitrages de licence, la réponse à un incident security, le contact industriel, la direction long-terme. Aucun agent ne couvre cette couche. CIRAD (Cornet, Rouan) figure en contributeurs, mais sans signal public d'autres décisionnaires.

Mitigations en plus de l'automation :

- **Doc d'architecture publique** — sortir les CLAUDE.md / AGENTS.md sous forme publique dans les `docs/` de chaque dépôt, pour que les agents *externes* puissent aussi opérer si quelqu'un d'autre reprend.
- **Tests + golden gates + CI verts** par dépôt comme contrat exécutable de comportement attendu — c'est ce qui permet à un repreneur (humain ou agent) de modifier sans casser.
- **CONTRIBUTING.md + bonnes premières issues** sur les 3-4 dépôts publics les plus accueillants (`nirs4all`, `nirs4all-formats`, `nirs4all-io`) pour amorcer des contributeurs humains au-delà des agents.
- **Externaliser CI/release** au-delà de la machine perso (GitHub-hosted runners, secrets organisationnels) : si la machine du mainteneur disparaît, la chaîne de release survit.
- **Recrutement d'un postdoc / ingénieur** dédié à `nirs4all-arena` (côté infra) ou à `dag-ml` (côté algorithmie) reste pertinent à moyen terme pour la couche stratégique — moins prioritaire que dans la version pré-automation, mais pas inutile.

### 4.8 Le risque "Python sans pricing"

`nirs4all` est en train de devenir une lib très large : pipelines, controllers, ML, DL, visualisations. Sans une stratégie de **scope freeze** (qu'est-ce qu'on n'ajoute plus à `nirs4all` et qu'on délègue à un autre dépôt ?), la lib gonfle, le ratio test/code baisse, et chaque refonte coûte plus cher. La règle « les méthodes vont dans `nirs4all-methods`, l'IO va dans `nirs4all-io`, les datasets dans `nirs4all-datasets` » est la bonne — encore faut-il l'appliquer rétroactivement (audit de ce qui est dans `nirs4all/operators/` et qui pourrait migrer).

---

## 5. Le cœur : ce qui est distinctif et défendable

Cinq éléments différenciants. Les claims ci-dessous sont *à démontrer comparativement* dans les papiers, pas à présenter comme acquis.

### 5.1 Le DSL de pipeline

L'API de pipeline de `nirs4all` (`_or_`, `_grid_`, `_cartesian_`, `_zip_`, `_chain_`, `_sample_`, `branch` / `merge` avec stratégies, `tag` / `exclude` séparés, `concat_transform`, `rep_to_sources` / `rep_to_pp`, `finetune_params` couplé à Optuna) est **densément expressif** pour le domaine NIRS / chimiométrie.

À ma connaissance, aucun outil NIRS open-source ne combine cet ensemble particulier (DSL plat en dict Python, exécution OOF-safe automatique, bundle d'export `.n4a` reproductible, intégration native sklearn + DL + SHAP). Des briques individuelles existent ailleurs — Kedro, Hamilton, MLflow, mlr3 / tidymodels côté ML générique ; Orange-Spectroscopy / Quasar, SpectroChemPy côté spectro. La contribution est la **combinaison** appliquée à NIRS, pas chaque pièce isolément.

À publier sous forme d'un papier *systems / software* — pas avant d'avoir une matrice comparative documentée vs Pinard, SpectroChemPy, Orange-Spectroscopy et au moins un workflow Kedro/Hamilton équivalent.

### 5.2 La famille AOM / POP

AOM-PLS / POP-PLS / AOM-Ridge / FastAOM constituent la contribution méthodologique la plus claire de l'écosystème. Résultat principal (AOM-Ridge Blender vs Ridge-default, RMSEP ratio médian 0.918 sur N_cap=32, 27/32 wins, Wilcoxon Holm-corrigé p = 2.6e-04) solide ; runtime AOM-PLS vs PLS-HPO (1.6 s vs 710 s sur le même N=32) très lisible. Le bundle arXiv v2 est prêt et le repo public.

Pour Talanta, audit benchmark récent (28 mai) : le calcul nécessaire existe déjà presque intégralement. Le master CSV `nirs4all-lab/benchmark_master_results.csv` (35 930 lignes) couvre AOM-PLS, AOM-Ridge, PLS / Ridge baselines tunés, HPO TabPFN-guided, TabPFN, CatBoost, NICON/CNN, multi-kernel, MoE, POP-PLS, FCK-PLS. Blender + AutoSelect seeds 0/1/2 sur 26 datasets uniques (union dédupliquée de `da001_audit20_seeds012` + `da001_partial_fast12_seeds012`), avec RMSEP identique entre seeds — caveat : le split SPXY3 est déterministe par protocole, donc « zero seed-variance » à reformuler en *protocol determinism* + audit multi-seed sur N=26 plutôt qu'en *« headline survives seeds »*. La baseline conventionnelle forte (SNV + SG + baseline + OSC + composantes sous HPO) est en `pls-tabpfn-hpo-25trials` × seeds 0/1/2 — à présenter comme « strong conventional preprocessing search under HPO », pas comme recette fixe. Restent (≈ 2-3 j humains, ≈ 0 compute, ou + 6 datasets pour atteindre N_cap=32 strict en multi-seed) : re-aggrégation `final_stats.md` + supplement, paragraphe failure-modes, missingness audit en table, citations SPORT / PORTO / PROSAC + Cawley-Talbot / Varma-Simon / Bergstra-Bengio, reflow Figure 5, clarification du search space PLS-HPO dans le texte, smoke test repo. Venue cohérente : Talanta ; Chemometrics & ILS reste possible pour un cadrage méthodologique pur.

### 5.3 La discipline de frontières

Cinq frontières dures, écrites, vérifiées :

- parsers seulement en Rust (`nirs4all-formats`),
- backend ne touche pas la lib (`nirs4all-studio`),
- bindings sans logique numérique (`nirs4all-methods`),
- core `dag-ml` ne voit jamais les matrices,
- `dag-ml-data` ne porte pas de logique ML.

Cette discipline n'est pas inédite dans l'open-source scientifique (NumPy/SciPy, Arrow/Parquet, PyTorch/XLA s'organisent autour de frontières analogues). Ce qui est **différenciant à l'échelle d'un écosystème NIRS / chimiométrie** : la combinaison de ces cinq frontières, écrites, et tenues par les CLAUDE.md/CONTRIBUTING.md de chaque repo. C'est un argument de soutenabilité multi-langage, pas une nouveauté CS.

### 5.4 La couverture d'opérateurs NIRS

Le catalogue (`operators/transforms`, `operators/models`, `operators/splitters`, `operators/augmentation`, `operators/filters`) couvre un éventail rare *dans Python*, surtout côté augmentation physiquement fondée (PathLength, BatchEffect, InstrumentalBroadening, DeadBand, ScatterSimulationMSC, Spline-X/Y perturbations). Une matrice comparative reste à produire vs `prospectr` (R, sample selection + preprocessing), `mdatools` (R, PLS/SIMCA diagnostics), `SpectroChemPy` (Python, IO + preprocessing + analyse), `pls` / `hyperSpec` / `ChemoSpec` (R), Orange-Spectroscopy / Quasar (UI + workflow). Sans cette matrice, le claim « couverture supérieure » n'est pas défendable. *Avec* cette matrice, un papier dédié sur l'augmentation physiquement fondée NIRS est rédigeable seul.

### 5.5 Le studio

`nirs4all-studio` n'est pas le premier studio open-source pour la spectroscopie : Orange-Spectroscopy / Quasar existe, avec une communauté installée et un éditeur de workflow visuel. Ce que `nirs4all-studio` ajoute : une orientation pipeline-reproductible NIRS-first, l'éditeur drag-and-drop branché sur le DSL `nirs4all`, et l'export `.n4a` natif. La formulation à porter publiquement est *un studio NIRS-first orienté pipeline reproductible*, pas *le studio qui manquait à PLS_Toolbox*. C'est un levier d'adoption rapide pour la communauté NIRS appliquée non-Python (lab terrain, agronomes, ingénieurs qualité), à condition d'investir la doc, les tutoriels vidéo et les exemples concrets.

### 5.6 Le pari Rust + C ABI portable

`nirs4all-methods` (`libn4m`) atteint un point rare : un cœur PLS / NIRS portable C++17 + ABI C stable + 4 bindings build verifiés (Python wheel, R CRAN-ready, Octave MEX, JS-WASM) avec parité numérique documentée publiquement à `< 1e-12`. C'est le socle qui rend crédibles les ambitions de portage R / MATLAB / WASM — sous réserve que les écarts entre la note interne « 100 % réconcilié » et les docs publiques (catalog 427/669, guessed 419, unmapped 662) soient clarifiés dans le repo avant tout communiqué externe.

---

## 6. Opportunités à viser

Liste priorisée. Les items sont notés **(P1/P2/P3)** par priorité et **(0-6m / 6-12m / 12-24m)** par horizon.

### 6.1 Publications

| # | Cible | Horizon | Pré-requis et conditions |
|---|---|---|---|
| **P1** | **JOSS paper `nirs4all`** | 6-12m | Soumission JOSS ne se fait pas à froid : il faut archive Zenodo/DOI, *statement of need*, alternatives discutées (au minimum prospectr, mdatools, SpectroChemPy, Orange-Spectroscopy, Pinard), tests + CI verts + couverture, *contribution guidelines*, *example gallery*, release stable (≥ 1.0.0). Sans cela, le reviewer JOSS demande des corrections. La rédaction est légère mais la mise à niveau du repo est non-triviale. |
| **P1** | **Papier AOM-PLS / POP-PLS** | 1-3m | arXiv v2 uploadable as-is. Pour Talanta : ~2-3 j humains de rédaction + agrégation, ~0 compute. Les expériences manquantes citées par la review (Blender/AutoSelect seeds 1/2, baseline conventionnelle SNV+SG+OSC+composantes tunées) **existent déjà** ; il reste à aggréger les workspaces archivés `da001_*_seeds012` dans `final_stats.md`, promouvoir missingness + failure-modes en tables supplément, ajouter SPORT/PORTO/PROSAC + Cawley-Talbot + Bergstra-Bengio + Varma-Simon, reflow Figure 5, expliciter le search space PLS-HPO dans le texte, et un smoke test repo. Venue Talanta. |
| **P1** | **Mise à jour `nirs4all-org`** (pas un papier, mais préalable) | 0-3m | Aligner les versions affichées (0.8.8 → 0.9.x), corriger la galerie, ajouter *statement of need* et liens packages. Conditionne crédibilité de toute publi citée. |
| **P2** | Papier formats / IO (`nirs4all-formats` + `nirs4all-io`) à JOSS ou SoftwareX | 12-18m | Conditionné à fixtures publiques propres + matrice de conformance documentée + comparaison vs `spc-spectra`, `jcamp`, `brukeropus`, `spectrolab`. SoftwareX a un APC non négligeable, à arbitrer vs JOSS gratuit. |
| **P2** | Papier DSL pipeline (Chemometrics & ILS ou SoftwareX) | 12-18m | À sortir **après** 1.0 de `nirs4all` et **après** au moins un benchmark comparatif documenté vs Kedro/Hamilton/MLflow sur ≥ 3 workflows. Sinon le claim « DSL différenciant » est non démontré. |
| **P2** | Papier `dag-ml` à MLOSS / JMLR | 12-18m | Pas OSDI/EuroSys (évaluation systèmes lourde non envisagée). MLOSS / JMLR open-source ML track est le bon couloir. **Conditionné à : (a) backend `dag-ml` effectivement consommé par `nirs4all`, (b) bench empirique sur ≥ 5 pipelines avec ≥ 2 concurrents (MLflow, DVC, Hamilton ou Metaflow), (c) démonstration concrète de cas de fuite/leakage attrapés.** Sans (a)(b)(c), pas de papier. |
| **P2** | Papier augmentation NIRS physiquement fondée | 12-18m | Rédigeable seul une fois la matrice comparative produite (cf. 5.4). |
| **P3** | Benchmark `nirs4all-arena` (Scientific Data en *data descriptor*, ou Chemometrics & ILS) | 18-24m | À sortir quand on a 5-10 datasets × 20+ pipelines avec splits group/instrument/campaign documentés, bundles `.n4a` archivés (Zenodo / Software Heritage), datasets DOI-pinés via `nirs4all-datasets`. Variante de fort intérêt : **benchmark cross-instrument / calibration transfer** — comparer DiPLS, PDS, deep DA, conformal sur paires d'instruments documentées ; bien aligné avec plant phenotyping CIRAD. |
| **P3** | Calibration transfer paper (DiPLS + extensions modernes : DANN, MMD, conformal) | 18-24m | Domaine porteur ; à coupler avec un dataset multi-instrument réel (CIRAD ?). |
| **P3** | Foundation model NIRS (`NIRS-FM` pré-entraîné sur corpus public, étend ViTnirs) | 18-30m | Visibilité forte si soumis à un workshop NeurIPS/ICLR applications spectroscopie. Conditionné à un corpus pré-train net (≥ 100k spectres publics agrégés). |

### 6.2 Standards et communauté

- **(P1, 0-6m)** Rapprochement R-side : proposer `nirs4all-formats` comme backend lecteur des paquets `prospectr` / `mdatools` / `hyperSpec` (PRs ciblées + emails aux mainteneurs). C'est la communauté NIRS la plus active et la plus accessible.
- **(P1, 6-12m)** Croissant ML metadata complet sur `nirs4all-datasets` — conditionné à un catalogue avec ≥ 5 datasets DOI + cards + manifests, **pas avant**. Aligne CIRAD avec MLCommons / Google open-data.
- **(P1, 6-12m)** Présence **ICNIRS 2027** (poster + talk + démo studio). Le calendrier se prépare à 12 mois.
- **(P2, 6-12m)** Présence **Eurosense** (food sensory + NIRS) et **Pittcon / SCIX** (chimie analytique). Communautés cibles directes pour l'adoption industrielle.
- **(P2, 6-12m)** Présence **CAC** (Chemometrics in Analytical Chemistry conference, biennale) et **IASIM** (imaging spectroscopy). CAC est l'événement chimiométrie au sens large, IASIM ouvre la porte HSI.
- **(P2, 6-12m)** Atelier / tutorial nirs4all à une école d'été chimiométrie (CHEMOMETRICS Summer School, COTAS, *Chemometrics in Analytical Chemistry* tutorials).
- **(P2, 12-18m)** Engagement communautés verticales : *NIR Forum* / *NIR News* (revue spécialisée), groupes phenotyping plant (TerraRef, G2F), *Aquaphotomics* (école montante en NIRS biomédical), *PROSPECT/PROSAIL* (remote sensing végétation).
- **(P3, 12-24m)** Workshop dédié à un congrès ML (NeurIPS workshop *Machine Learning for Physical Sciences* ou similaire). Réservoir de visibilité côté ML.

### 6.3 Industrie

- **(P1, 0-6m)** Sortir la **matrice de licence publique** de l'écosystème (cf. critique 4.6). Pré-requis à toute discussion industrielle : un vendeur ne signe pas sans clarté. Inclut une éventuelle double licence (CeCILL libre + commercial avec support CIRAD).
- **(P2, 6-12m)** Approche **vendeurs d'instruments** (Bruker, Foss, Metrohm, ABB, PerkinElmer, ASD/Malvern) — **conditionnée à** : (a) matrice de licence sortie, (b) `nirs4all` 1.0 stable et publié, (c) `nirs4all-org` à jour, (d) au moins une publi citable. Démonstration : `nirs4all-formats` lit leurs sorties natives + studio interactif sans logiciel propriétaire. Sans (a)(b)(c)(d), prématuré.
- **(P2, 12-24m)** Cible verticale **PAT pharma** (Process Analytical Technology). Audit conformité GxP, traçabilité runs, intégrité signatures électroniques (CFR 21 Part 11). Marché payant ; `nirs4all` a déjà la traçabilité par construction. Conditionné à un partenaire pharma identifié.
- **(P3, 12-24m)** Cible verticale **agronomie / breeding** (CIRAD est sur place) : NIRS + génotype SNP via `dag-ml-data`. Pilote interne CIRAD (G2F-like, breeding NIRS) → publi (e.g. *Plant Phenomics*, *G3*) → diffusion. Bon levier publication interdisciplinaire.
- **(P3, 12-24m)** Cible verticale **soil / agronomy NIRS** (mesures sol, sondes terrain) et **food quality control**. Marchés diffus mais utilisateurs nombreux.

### 6.4 Technique (R&D)

- **(P1, 0-12m)** **Backend `dag-ml` consommé par `nirs4all`** : faire en sorte qu'un pipeline `nirs4all` puisse s'exécuter via `dag-ml` (mode opt-in). Sans cela, `dag-ml` reste un scaffold. C'est l'item de couplage qui conditionne le papier `dag-ml`.
- **(P1, 0-12m)** **Protocoles de splits avancés** : au-delà de Kennard-Stone / SPXY déjà présents, expliciter et tester *group split* (échantillons groupés par lot / instrument / campagne), *repeated measurements* (déjà partiellement via `rep_to_*`), *instrument leakage*, *temporal leakage*. C'est la première chose qu'un reviewer chimiométrie ou ML méthodes vérifie.
- **(P2, 6-12m)** **Interprétabilité spectroscopique au-delà de SHAP** : VIP (Variable Importance in Projection) côté PLS, loadings et bi-plots, *stability wavelength selection* (variants stables de CARS / VIP-stable), *saliency sanity checks*, *confound detection*. C'est la lingua franca chimiométrie. SHAP seul ne suffit pas à convaincre la communauté NIRS.
- **(P2, 6-12m)** **TabPFN comme operator first-class** dans `nirs4all` : déjà exploré en lab. NIRS = small-data tabulaire = terrain idéal pour TabPFN v2 / v2.5. Papier court possible (NeurIPS workshop *Tabular ML*).
- **(P2, 6-12m)** **Calibration transfer modernisé** : étendre DiPLS avec adaptation de domaine deep (DANN, MMD), *piecewise direct standardization* (PDS), conformal prediction pour intervalles de calibration. Domaine porteur.
- **(P2, 12-24m)** **Hyperspectral imaging au-delà de NIRS** : `nirs4all-formats` lit déjà ENVI / AVIRIS, mais la stratégie pipeline doit traiter *spatial CV* (ROI-aware, block-CV pour éviter spatial leakage), gestion des cubes (H × W × λ), *region of interest* extraction, intégration avec workflows phenotyping image. Préalable au pivot multi-modal du studio.
- **(P2, 12-24m)** **Foundation model NIRS** : pré-entraînement transformer (masked spectral modeling) sur un large corpus public agrégé. Diffusion en `nirs4all.operators.models.NIRSTransformer`. Le travail ViTnirs en lab est un prototype.
- **(P2, 12-24m)** **Uncertainty quantification** : conformal prediction sur prédictions PLS/DL, bayesian PLS, comparaison rigoureuse. Domaine sous-développé en NIRS appliquée, crucial pour PAT et calibration cross-instrument.
- **(P3, 12-24m)** **Multi-modal `dag-ml-data`** consommé par `nirs4all-studio` : extension HSI, time-series, génotype SNP. Vision long-terme du studio. Conditionné aux items P1 d'abord.

### 6.5 Communications

- **(P1, 0-3m)** **Mise à niveau `nirs4all-org`** : aligner versions (0.8.8 stale → 0.9.x), corriger la galerie d'écrans, ajouter *statement of need*, lien direct vers packages (PyPI, CRAN, crates.io), citation BibTeX, état réel des projets. Préalable à toute publi qui pointe vers le site.
- **(P1, 0-6m)** Refonte progressive : démo studio en GIF / vidéo, exemples concrets « 10 lignes de code », pages dédiées par projet de l'écosystème.
- **(P1, 0-6m)** Lancer un blog technique (`posts/` dans `nirs4all-org`) avec 4-6 posts cibles : *Why we built nirs4all*, *The pipeline DSL*, *AOM-PLS in 5 minutes*, *From OPUS file to prediction in Studio*, *Reproducible NIRS bundles*, *nirs4all-formats : reading 58 vendor formats from Rust*. Visibilité long-traîne SEO.
- **(P2, 6-12m)** Démo WebAssembly en ligne : `nirs4all-formats` + PLS basique en client-side, en démo sur nirs4all.org. Démonstration concrète du pari portable, utile pour outreach R / industrie.
- **(P2, 6-12m)** Présence YouTube / chaîne CIRAD : 4-5 tutoriels vidéo (15-30 min) sur les usages typiques.
- **(P3, 12-24m)** Ouvrir un forum (Discourse ou GitHub Discussions) si la communauté grandit suffisamment.

---

## 7. Recommandations stratégiques

### 7.1 Trois axes pour les 6-12 mois prochains

L'écosystème a accumulé plus de code que de diffusion. Trois axes en parallèle :

1. **Consolider ce qui existe.** Finir le 0.9.x stable, sortir 1.0.0 de `nirs4all` avec promesses d'API publiques explicites, releaser `nirs4all-methods` sur PyPI + CRAN, releaser `nirs4all-formats` sur PyPI + crates.io, mettre `nirs4all-org` à jour. Aligner les claims publics (parité, ABI réconciliée, statuts datasets) sur la réalité documentée du repo.
2. **Deux publications cibles d'abord**, pas trois en parallèle : (a) JOSS `nirs4all` une fois 1.0 sorti + checklist JOSS remplie (cf. 7.2), (b) AOM-PLS une fois les blockers `paper_review.md` levés. DSL et `dag-ml` viennent ensuite, conditionnés à des artefacts publics et benchmarks comparatifs.
3. **`nirs4all-arena` — benchmark interne reproductible publié en lecture.** Choisir 5 datasets publics (NIRS pharma + agro + food + soil + plant phenotyping si possible), 10-15 pipelines (PLS, AOM, RF, NN, TabPFN…), splits group/instrument/campagne, matrice méthode × scenario générée en interne, pages de browsing publiques, bundles `.n4a` téléchargeables. **Pas de soumission externe, pas de plateforme de compétition.** La *version citable* (DOIs, licences, cards, Croissant complets) est un palier supplémentaire à 12-18 mois.

### 7.2 Checklist JOSS minimale pour `nirs4all`

Préalable à toute soumission :
- archive Zenodo / DOI du tag de soumission ;
- *statement of need* explicite (vs `prospectr`, `mdatools`, `Pinard`, `SpectroChemPy`, Orange-Spectroscopy / Quasar) ;
- *alternatives* discutées dans le papier, pas juste listées ;
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, *issue templates*, label *good first issue* peuplé ;
- CI verte sur Linux + macOS + Windows, couverture documentée ;
- *example gallery* exécutable (ce que `examples/` fournit déjà — à vérifier qu'il tourne sur les 3 OS) ;
- release stable taggée (≥ 1.0.0) ;
- la doc Sphinx publiée à une URL stable (ReadTheDocs ou GitHub Pages).

### 7.3 Ce qu'il faut différer (et l'écrire)

- **`nirs4all-lite` comme dépôt de code numérique / réécriture native** → **abandonné**. Le dépôt existe en tant que *distribution simplifiée multi-langages* de la chaîne bas-niveau (cf. §4.3), pas comme réécriture ou sous-ensemble. Démarrage conditionné à la politique de stabilité écrite (semver strict, tags pinés, tests fixtures, compat matrix, SBOM/CVE/redistribution).
- **`nirs4all-dist` (factory partagée build / scaffolding / supply-chain)** → **abandonné comme dépôt actif**. Son rôle est repris par les workflows, scripts et docs de `nirs4all-lite`; ne pas référencer de reusable workflows `GBeurier/nirs4all-dist`.
- **Plateforme de soumission externe / compétition type Kaggle pour l'arena** → **abandonnée**. L'arena reste curée + compute interne + browsing public. Ne pas l'annoncer comme un Kaggle-NIRS, même à long terme.
- **Exécution distribuée client/serveur/workers** (cf. *Annexe — Perspective : exécution distribuée* en fin de document) → `nirs4all-cluster` existe publiquement comme prototype alpha, mais ne doit pas être présenté comme produit stable ni endpoint multi-tenant. L'industrialisation reste conditionnée aux critères go/no-go ; un spike Dask opt-in dans `nirs4all` reste la voie courte à tester.
- **Bindings Julia / JNI / Android** de tous les projets → différer jusqu'à demande utilisateur explicite.
- **Multi-modal généralisé du studio** (HSI / SNP) → différer post-1.0.0 `nirs4all` et post-couplage `dag-ml`.

### 7.4 Ce qu'il faut couper ou geler

- **Ajouts d'opérateurs dans `nirs4all/operators/`** qui pourraient vivre dans `nirs4all-methods` ou en plugin externe : audit + migration plutôt qu'ajout.
- **Dépendances Python ML lourdes par défaut** : conserver et durcir le lazy-loading, exposer des extras `[dl-tf]`, `[dl-torch]`, `[dl-jax]` clairs.
- **Tout claim public non sourcé** : *standard*, *meilleur*, *équivalent à*, *aucun équivalent*, *change tout* — remplacer par des claims bornés et testables par une matrice comparative.

### 7.5 Décisions à prendre explicitement (à écrire dans un doc public)

1. **Politique de licence** publique de l'écosystème (matrice par dépôt × usage commercial × contagion).
2. **`nirs4all-lite`** : périmètre d'artefacts cibles prioritaires (PyPI `nirs4all-lite`, CRAN/R-universe `nirs4all`, npm `nirs4all`, MATLAB/Octave zip/toolbox en premier, puis Conda channel + Docker images + Julia Pkg + vcpkg), politique semver et compat matrix, CODEOWNERS et fréquence de release.
3. **`nirs4all-arena`** : paliers cibles (a) *benchmark interne reproductible*, (b) *site de browsing public*, (c) *ressource citable* DOIs + cards + Croissant + bundles `.n4a` versionnés, et calendrier réaliste pour chacun. **Pas de palier « plateforme de soumission externe »** (abandonné, cf. §4.4 et §7.3).
4. **Priorisation des bindings** : R = P1, MATLAB = P2, JS/WASM démo = P3, Julia/JNI/Android = sur demande.
5. **Couplage `dag-ml` ↔ `nirs4all`** : à quelle version de `nirs4all` `dag-ml` devient backend opt-in ? Conditionne le papier `dag-ml`.
6. **Politique de fraîcheur** publique : engagement à aligner les claims du repo / webpage / README sur la réalité documentée (versions, parité, ABI, datasets) avant chaque release.
7. **Politique d'automation** (cf. §7.6) : quels périmètres agents *peuvent* opérer en autonomie, lesquels exigent revue humaine systématique, comment auditer.

### 7.6 Le pari automation comme stratégie de maintenance

L'écosystème fait le choix explicite d'automatiser au maximum, par agents IA (Claude Code, Codex, …), le traitement des **tickets, PRs, issues, demandes, releases de routine, mises à jour de dépendances, génération de changelogs, migrations cross-repo, mise à jour de la documentation, propagation de schémas, vérifications de conformance**. C'est le pari qui rend défendable l'ordre de grandeur du scope (15+ dépôts, multi-bindings).

#### Périmètres agent-driven (autonomie + revue humaine légère)

- Triage et catégorisation des issues entrantes (labels, priorité, dépôt cible).
- PR de routine : bumps de dépendances, formatage, lint, doc strings, mise à jour de tests sur renommage de symbole.
- Generation et mise à jour des changelogs, release notes, citations BibTeX, versionnage SemVer.
- Propagation de schémas / contrats JSON entre dépôts liés (`dag-ml` ↔ `dag-ml-data`, `nirs4all-formats` ↔ ses bindings).
- Mise à jour des CLAUDE.md / AGENTS.md / index `MEMORY.md` sur évolution structurelle.
- Migrations cross-repo de petite/moyenne ampleur **strictement bornées** (certains agents cloud restent mono-repo par session — découper le périmètre).
- Réponses de premier niveau aux issues (clarification, demande de repro, pointage doc) avant escalade humaine.
- Build / parity / ABI snapshot diffs sur les dépôts Rust et C++ — *lecture* des diffs ; toute *modification* de l'ABI publique remonte humain.
- **`nirs4all-lite` (§4.3) — cas modèle agent-driven** : bumps de refs vers les libs amont (lock files), mise à jour des recettes packaging (Conda, Docker, R DESCRIPTION/Makevars, MATLAB toolbox), rebuild CVE déclenché sur signal supply-chain, regen des SBOM/attestations. Le périmètre est *parfait* pour l'automation parce que (a) zéro code numérique, (b) frontières claires entre configs et libs amont, (c) tests fixtures vérifient la non-régression à chaque PR.

#### Périmètres qui restent humains (revue qualifiée systématique, jamais en autonomie complète)

- Décisions d'architecture (frontière entre dépôts, ABI publique, contrat de schéma versionné).
- **Breaking changes API / ABI publique** : tout changement de signature publique ou de wire schema versionné — humain valide, agent peut préparer la PR.
- Cadrage scientifique des papiers (claims, dénominateurs, statistiques, baselines).
- Arbitrages de licence et de double licensing.
- Réponse à un **incident sécurité, vulnérabilité dépendance, fuite de secret**. Politique SCA / SBOM / provenance lue par humain, pas auto-mergée sur signal vert.
- **Credentials de release** : tokens PyPI / CRAN / npm / crates.io / GitHub secrets / organisation org-level. Aucun agent ne pousse une release tagged seul. Tokens courts, rotation documentée, provenance des artefacts publiés.
- **Modération de la communauté** (GitHub Discussions, mailing-list, futurs forums) : réponses techniques agent-assistées OK ; bans / arbitrages / conflits = humain.
- Contact industriel et partenariats.
- Choix produit du Studio (UX, priorités utilisateur).
- Communication publique (webpage, posts, papiers, talks).

#### Carburant requis pour que le pari tienne

- **CLAUDE.md / AGENTS.md à jour** dans chaque dépôt, alignés sur la réalité documentée (cf. §7.5 décision 6). Un agent qui opère sur des docs périmées propage les erreurs.
- **Tests verts + golden gates par dépôt** : c'est le contrat exécutable que les agents respectent. Sans tests, l'agent ne sait pas qu'il a cassé.
- **Schémas + fingerprints + `scripts/validate_contracts.py`** dans les dépôts à contrat cross-repo. Drift détecté → agent corrige ou ouvre une issue.
- **Tests E2E** (Studio en navigateur, golden workflows captures d'écran, smoke tests CLI par dépôt) en plus des tests unitaires. C'est le filet qui rattrape les régressions UX qu'un agent ne voit pas dans son contexte.
- **Politique dépendances** : SCA (Software Composition Analysis), SBOM (Software Bill of Materials), provenance des artefacts. Pas d'auto-update agent sur dépendance flaggée *security-critical* sans revue humaine.
- **Politique de mémoire / contexte des agents** : éviter la pollution context-window inter-sessions, isolation par tâche, *no carry-over* de claims non vérifiés entre PRs.
- **Politique de revue humaine** : chaque PR agent-driven a un humain reviewer responsable du merge. **Pas d'auto-merge sur `main`** — règle dure. Reviewer sub-agent obligatoire en *premier passage* pour pré-filtrer.
- **Audit trail** : logger les actions agent dans les PRs et issues pour traçabilité. Code Co-Authored-By approprié.
- **Dashboard d'activité** : ratio PR agent / humain, merge rate, revert rate, score de couverture E2E — visible publiquement pour pression à la qualité.
- **CI matrix « agent-friendly »** : commande unique par dépôt (`make ci` / `cargo make ci` / `npm run ci`) que l'agent exécute avant chaque PR. Pas de chaîne de commandes implicite à reconstruire.
- **Politique de claims stable** : les agents ne doivent pas réintroduire les sur-affirmations corrigées dans ce document. Référencer §7.5 décision 6 dans chaque CLAUDE.md.

#### Risque résiduel et signal d'alerte

L'automation n'est *pas* un substitut à la couche stratégique. Le bus factor stratégique (§4.7) reste élevé. Signaux d'alerte que l'automation dérive :
- Régressions silencieuses dans la doc (claims trop forts, comparatifs faux, versions obsolètes ré-écrites).
- PRs auto-mergées qui ré-introduisent du code mort ou des shims de compatibilité.
- Multiplication des dépôts sans clarification stratégique humaine préalable.
- CI verte mais comportement utilisateur final cassé — trou de couverture E2E que les agents ne peuvent pas détecter seuls.
- **Plugin MCP / dépendance / chaîne agent compromis** (supply-chain agentique) — provenance signée et SBOM obligatoires.
- **Élargissement progressif des permissions agent** (*privilege creep*) sans décision documentée.
- **Pollution contexte / mémoire** : claims non vérifiés ré-introduits d'une session à l'autre, hallucination d'API privée ou d'état repo qui n'existent pas.
- **PR qui ajoute des tests validant le bug au lieu de le corriger** — pattern connu et facile à laisser passer en revue rapide.

Mitigation : revue trimestrielle humaine de l'état réel de l'écosystème + des PRs agent-driven mergées, alignement claims/réalité, et resserrement des CLAUDE.md / AGENTS.md sur les périmètres où l'agent a dérivé.

---

## 8. Risques majeurs

| # | Risque | Impact | Mitigation |
|---|---|---|---|
| R1 | **Bus factor stratégique** (décisions d'architecture, cadrage scientifique, sécurité, partenariats, communication publique) | Élevé sur la couche stratégique ; la couche opérationnelle est *fortement assistée, mitigée sous supervision et gates exécutables* par le pari automation (§7.6) | Doc d'architecture publique, CONTRIBUTING.md, tests + golden gates comme contrat exécutable, externaliser CI/release au-delà de la machine perso, recrutement postdoc/ingénieur pour la couche stratégique. *L'automation ne couvre pas cette couche*. |
| R2 | **Scope explosion** (≥ 15 dépôts × N bindings cibles) | Moyen — le coût marginal *opérationnel* d'un dépôt est fortement réduit par §7.6 ; le coût marginal *stratégique* (revue d'architecture, décisions de produit) reste linéaire | Priorisation R = P1, MATLAB = P2, WASM démo = P3, reste = sur demande. *Release trains* groupant dépôts liés (agent-driven). *Deprecation* publique des bindings non utilisés. CLAUDE.md / AGENTS.md à jour comme prérequis au pari automation. |
| R3 | **Licences incompatibles industrie** (AGPL / CeCILL) | Élevé pour adoption industrielle | Matrice licence publique, double-licensing CIRAD-supported si pertinent. |
| R4 | **`dag-ml` reste scaffold** (jamais consommé par `nirs4all` en production) | Élevé pour publication ML | Item P1 : couplage opt-in dans `nirs4all` à 6-12 mois. Sinon le papier `dag-ml` ne sort pas. |
| R5 | **Mismatch public / privé** : `nirs4all-datasets` est privé, `nirs4all-lab` est privé, mais l'ambition « arena publique » + « benchmark public » dépend de leur ouverture. | Élevé pour communauté | Décider explicitement quels datasets / pipelines passent public, et le faire avant d'annoncer une arena publique. |
| R6 | **Stale public metadata** : webpage, READMEs, versions divergent (webpage 0.8.8 vs lib 0.9.1, finish-lib-progress 100% ABI vs SPEC 64% catalogued). | Moyen, mais nuit à la crédibilité scientifique et industrielle | Politique de fraîcheur (cf. 7.5 décision 6) ; checklist pré-release. |
| R7 | **Benchmark leakage** dans l'arena (single split, repeated samples non groupés, instrument leakage, temporal leakage). | Élevé scientifiquement (publi rejetée ou rétractée) | Splits group/instrument/campagne dès le jour 1 ; documenter la stratégie. C'est précisément ce que `dag-ml` peut garantir. |
| R8 | **`nirs4all-arena` annoncé comme plateforme de soumission / compétition** alors que le périmètre est curé + compute interne + browsing public | Moyen, réputationnel et scope | Cadrage §4.4 explicite ; communication publique limitée à *benchmark reproductible curé* et *site de browsing*, jamais *soumission externe* ni *compétition*. |
| R9 | **Concurrence R** (mdatools, prospectr, hyperSpec, ChemoSpec) qui adopte ces idées avant nous | Moyen | Sortir vite JOSS + outreach R-side (PRs, atelier ICNIRS, posts blog). |
| R10 | **Outils établis** (PLS_Toolbox, Unscrambler, SIMCA, Quasar/Orange-Spectroscopy) ignorent l'open-source ou se renforcent | Moyen | Effet réseau via *instrument vendors*, étudiants formés, plant phenotyping CIRAD. Long terme. |
| R11 | **Surcoût studio Electron** vs web pure | Moyen | Maintenir le mode web autonome ; Electron comme distribution optionnelle. |
| R12 | **AOM soumis Talanta prématurément** (sans aggréger les multi-seed déjà calculés + sans citations + sans paragraphe failure-modes) | Élevé scientifiquement | ~2-3 j humains de rédaction + agrégation sur des données existantes (cf. header revisé `paper/review/paper_review.md`). Ne pas soumettre sans cette passe. |
| R13 | **Exécution distribuée bâclée** — soit `nirs4all-cluster` sort de son rôle de prototype alpha sans cadrage sécurité, soit un prototype Dask est déployé sans modèle mTLS/secrets/isolation workspaces/quotas. Risque même si le site de browsing arena reste *read-only* : un worker mal isolé est exploitable | Très élevé pour scope *et* pour réputation (incidents data/security) | Garder `nirs4all-cluster` public mais explicitement prototype. Ne pas en faire un service multi-tenant. Pour le court terme, privilégier Option C (Dask backend opt-in dans `nirs4all`) avec critères go/no-go documentés. Modèle data + sécurité + reprise écrit avant tout déploiement. Le « public » de l'arena reste un *site de consultation*, jamais un *endpoint d'exécution accessible aux tiers*. |
| R14 | **Dérive du pari automation** : auto-merge sur `main`, sur-affirmations corrigées ré-introduites, code mort, dépôts multipliés sans clarification stratégique, CI verte mais UX cassée, supply-chain agentique compromise (MCP / plugin / dépendance), *privilege creep* sur permissions agent, pollution contexte / hallucination d'API privée, PR qui ajoute un test validant le bug | Moyen-élevé (érosion silencieuse de qualité, voire incident sécurité) | Pas d'auto-merge `main` (règle dure) ; reviewer sub-agent obligatoire + humain reviewer responsable (cf. §7.6) ; audit trimestriel agent vs humain (dashboard) ; tests E2E + couverture mesurée ; SBOM + provenance + SCA sur dépendances et plugins MCP ; permissions agent documentées et révisées ; CLAUDE.md / AGENTS.md à jour comme contrat opérationnel ; référencement explicite §7.5 décision 6 dans chaque CLAUDE.md. |
| R15 | **Distribution `nirs4all-lite` trop centrale** — si les recettes de build/release sont modifiées sans tests par cible, une release casse plusieurs bindings en cascade | Moyen-élevé pour velocity et fiabilité release | CI dédiée par cible (Rust, Python, R, JS/WASM, MATLAB/Octave), artefacts de release reconstruits à chaque tag, semver strict, tags pinés côté libs amont, CODEOWNER par cible, no autonomous merge, compat matrix publiée. |

---

## 9. Synthèse exécutive

L'écosystème nirs4all est architecturalement plus avancé que sa visibilité publique ne le suggère. Les frontières sont propres, l'infrastructure C ABI multi-langage tient sur quatre bindings, le DSL de pipeline a une expressivité large dans le périmètre NIRS/chimiométrie (à démontrer par matrice comparative), et la science (AOM-PLS / POP-PLS) repose sur un signal statistique sérieux. Plusieurs claims qui circulent encore dans certains dépôts ou pages publiques dépassent toutefois l'état documenté : parité numérique évoquée à `1e-16` quand la doc publique est à `1e-12`, ABI annoncée 100 % réconciliée en note interne quand la SPEC publique compte 427/669 catalogués, `nirs4all-datasets` qualifié d'*alpha* alors que le catalogue contient un seul exemple, webpage qui affiche une version dépassée. Inversement, certains *under-claims* internes : la `paper_review.md` AOM (17 mai) listait des blockers compute (multi-seed Ridge headline, baseline conventionnelle forte) qui sont en réalité *déjà calculés* dans des workspaces archivés ; le reste pour Talanta est de la rédaction + agrégation (~2-3 j humains). **Premier travail : aligner ces claims sur la réalité documentée — pas ajouter du nouveau code.**

Le risque principal n'est plus technique ni la maintenance brute, il est de **diffusion, focus, cohérence des claims, et tenue du pari automation** :

- **un cœur défendable** (DSL + AOM + Studio + couche Rust + frontières disciplinées) noyé dans des dépôts non encore mûrs ou stale,
- **pas assez de publication / citation** vs ce qui est déjà construit,
- **dépendances cachées** entre objectifs : `dag-ml` publiable suppose qu'il soit consommé par `nirs4all` ; AOM publiable suppose les blockers levés ; arena suppose datasets ouverts et compute interne curé,
- **trop d'ambitions parallèles vs capacité de décision et de revue *qualifiée*** : le pari automation (§7.6) recalibre la maintenance de routine mais n'absorbe pas la couche stratégique (architecture, science, sécurité, partenariats, communication), qui scale linéairement avec le nombre de dépôts et reste portée par très peu de personnes.

La période 2026-S2 / 2027-S1 devrait être une phase de **consolidation et de mise en cohérence**, *avant* la phase de diffusion : 1.0.0 de `nirs4all`, alignement des claims, deux papiers d'abord (JOSS + AOM nettoyé), arena en benchmark reproductible curé + site de browsing, présence ICNIRS 2027. `nirs4all-lite` peut démarrer en parallèle dès qu'un premier bundle multi-langage est utile (CRAN, Conda ou Docker) et porte directement ses recettes de build/release. Multi-modal studio, bindings exotiques attendent. La plateforme de soumission externe type Kaggle est explicitement abandonnée ; la réécriture native Rust/C++ n'a jamais été le projet (cf. §4.3).

L'objectif long-terme défendable n'est pas « écrire encore plus de code » : c'est **devenir une référence open-source citée en NIRS appliquée et chimiométrie**, avec une couche d'infrastructure (`dag-ml`) propre et utilisée, publiable séparément en open-source ML (MLOSS / JMLR). Les deux objectifs se servent mutuellement, à condition de tenir les claims.

---

## Annexe — Table source-de-vérité par dépôt

À tenir à jour. Toute communication externe doit refléter cette table, pas une formulation plus enthousiaste.

| Dépôt | Version | Visibilité | Release publiée | CI publique | Tests | Bindings actifs | Notes |
|---|---|---|---|---|---|---|---|
| `nirs4all` | 0.9.x | public | PyPI (en cours, viser 1.0.0) | oui (à confirmer multi-OS) | pytest unit + integration, couverture à documenter | — (lib Python) | API publique stable annoncée 0.9.x, à figer en 1.0 |
| `nirs4all-studio` | dev | public | pas de release tag | partielle | vitest + pytest + Playwright | — (app) | Lance via `npm run start:*` ; backend FastAPI + Electron |
| `nirs4all-formats` | crates dev | public | pas encore PyPI / crates.io | Rust ci OK ; release workflow tag-déclenché | cargo test + goldens + conformance | Python (PyO3), R (extendr), WASM | Conformance vs `brukeropus`, `spc-spectra`, `jcamp`, `spectrolab`, `h5py` |
| `nirs4all-io` | alpha | public | pas encore PyPI | ruff + mypy + pytest | ~200 tests, parité byte-vs-byte avec `DatasetConfigs` | Python (phase 1) | Phase 2 Rust gatée |
| `nirs4all-methods` | post-merge refactor | public | wheels prêts, CRAN vendored build prêt ; pas encore publié | partielle (R, Octave, JS-WASM en CI) | doctest `n4m_tests` + parité par binding | Python (`nirs4all-methods`, `pls4all`), R, Octave (MEX), JS-WASM | Parité publique `< 1e-12` ; ABI réconciliation : claims internes ≠ docs publiques, à clarifier |
| `dag-ml` | dev | public | pas de release | rust ci OK | cargo + validate_contracts | C ABI + Python ctypes smoke | Pas encore de host controller production ; pas encore consommé par `nirs4all` |
| `dag-ml-data` | dev | public | pas de release | rust ci OK | cargo + validate_contracts cross-repo | C ABI + Python ctypes smoke | Contrats partagés avec `dag-ml` |
| `nirs4all-aom` | beta | public | pas encore PyPI | partielle | pytest + benchmarks | Python | Papier en cours, blockers expérimentaux à lever |
| `nirs4all-datasets` | dev | public | pas de release | partielle | pytest minimal | Python | 1 dataset exemple, DOIs/cards/manifests pas encore peuplés |
| `nirs4all-lab` | dev | **privé** | n/a | n/a | n/a | Python | Espace de prototypage |
| `nirs4all-arena` | stub | public | n/a | n/a | n/a | n/a | README uniquement |
| `nirs4all-org` | en ligne | public | n/a | GitHub Actions deploy | n/a | n/a | Ancien `nirs4all-webpage`; liens publics alignés avec `nirs4all-web`, `nirs4all-lite` et `nirs4all-cluster` |
| `nirs4all-ecosystem` | dev | public | n/a (parent submodules) | n/a | n/a | n/a | Ne contient pas de code |
| `nirs4all-cluster` | alpha/prototype | public | n/a | oui | pytest + mypy + ruff | Python | Prototype distribué public ; ne pas présenter comme service stable |
| `nirs4all-papers` | seed | public | n/a | n/a | n/a | n/a | Dépôt public des papiers déposés et bundles reproductibles à migrer par papier |
| `nirs4all-drafts` | actif | privé | n/a | n/a | n/a | n/a | Drafts et artefacts de soumission en cours |
| `nirs4all-lite` | dev | public | pas encore publiée | oui | cargo fmt/clippy/test, Python build+twine, npm test/pack, R CMD build/check, Octave smoke/package | Rust, Python, R, MATLAB/Octave, JS/WASM | Agrégateur mince ; CI verte, intégrations upstream/parité pipeline à compléter |

---

## Annexe — Perspective : exécution distribuée client / serveur / workers

> *Hors recommandations à court/moyen terme.* Cette annexe consigne l'analyse d'une demande envisagée — pas une roadmap. À relire au moment d'instruire concrètement le sujet, pas avant. Référencée depuis §2 cartographie, §7.3 différer, §8 R13.

Demande envisagée : permettre à plusieurs machines de partager l'exécution de pipelines `nirs4all`, avec un serveur central qui reçoit les jobs / requêtes d'exécution et dispatche le travail à des workers distants. **À cadrer strictement avant tout investissement** : c'est la classe de scope expansion que R2 signale.

### Quatre usages possibles, contraintes très différentes

1. **Cluster de labo** — mutualisation interne sur 5-10 machines d'un groupe de recherche. Sécurité simple, datasets co-localisés.
2. **Arena en exécution interne distribuée** — l'arena reste curée (compute interne, pas de soumission externe — cf. §4.4), mais ses scenarios méthode × dataset sont assez nombreux pour bénéficier d'un dispatch multi-machine côté hôte. Sécurité simple (réseau interne CIRAD), pas de sandboxing tiers à gérer.
3. **Studio multi-tenant** — backend partagé pour plusieurs utilisateurs Studio. Ajoute auth, isolation des workspaces.
4. **Calcul fédéré** — variante intéressante : les datasets *restent* sur la machine d'origine (organismes qui ne peuvent pas partager leurs données), seul le résultat agrégé remonte.

### Ce qui existe déjà

- Parallélisme local via `joblib.Parallel(backend='loky')` dans `PipelineOrchestrator` (`nirs4all/pipeline/execution/orchestrator.py:310`) ; expansion `_grid_` / `_cartesian_` / `_or_` / `_chain_` naturellement indépendante.
- `JobManager` dans `nirs4all-studio` (`api/jobs/manager.py:94`) : **ThreadPoolExecutor in-memory** avec callbacks et dispatch WebSocket — pas une queue distribuée durable. L'écart au multi-machine est plus grand que le code laisse supposer.
- Bundle `.n4a` portable et reproductible — un worker peut le charger et l'exécuter sans état partagé *modulo* accès au dataset (store partagé / NFS / S3), environnement Python compatible (TF / Torch / JAX si requis) et provisionnement des secrets.
- `dag-ml` C ABI (`dag_ml.h`) prévoit des controllers `invoke` + replay + process-adapter, mais **pas de remote controller RPC pour l'instant** — la frontière est préparée, le transport reste à écrire.

### Quatre options architecturales

| Option | Description | Effort | Quand |
|---|---|---|---|
| **A. Worker `nirs4all` natif minimal** | `nirs4all worker --connect <url>` s'enregistre auprès du backend Studio étendu ; le coordinateur pousse `.n4a` + dataset hash, le worker récupère depuis un store partagé. Construit sur l'infrastructure FastAPI existante *mais* impose de remplacer le ThreadPoolExecutor par une vraie queue (Redis/RabbitMQ). | 3-6 mois, 1 personne | Si la demande mono-org se confirme |
| **B. Backend `dag-ml` + host controllers RPC distants** | Suppose (i) couplage `dag-ml` ↔ `nirs4all` (item P1 §6.4), **(ii) ajouter un transport remote au vtable controller dans `dag_ml.h`** (n'existe pas), (iii) provider de transport (gRPC ou similaire). On hérite alors de l'OOF-safety, lineage, replay. | 6-12 mois *après* (i) + spec (ii) | Voie architecturalement propre, conditionnée à dag-ml mûr |
| **C. Adopter un orchestrateur existant en backend** | `nirs4all.run(executor=DaskExecutor(...))` ou `RayExecutor(...)`. Dask intégré sklearn/joblib (`joblib.parallel_backend('dask')` est natif), bien adapté labo/HPC léger. Ray plus orienté ML/DL/GPU/actors mais plus lourd. Celery = task queue (pas data locality scientifique). Temporal = durable orchestration (pas un backend compute). Nextflow = batch HPC bioinfo, mais impose son propre modèle pipeline qui clasherait avec le DSL `nirs4all`. | 1-3 mois prototype | **À tester en premier** — Dask en priorité |
| **D. Industrialiser `nirs4all-cluster` complet** (server + worker + scheduler + UI + sécurité + multi-tenancy) | Équivaut à recoder Celery + Prefect + un MLOps minimal. | 12-24 mois, équipe | À **éviter** sauf financement dédié — exactement le scope que R2 met en garde |

### Sujets à traiter dès le cadrage (ne pas reporter)

- **Sécurité worker / serveur** : mTLS, authentification, secrets, nettoyage post-job.
- **Sandboxing des pipelines tiers** : applicable uniquement aux usages 3 (Studio multi-tenant) et 4 (fédéré inter-organismes) ; non requis pour l'arena puisqu'elle reste en compute interne curé (cf. §4.4). Si activé : containers, restricted env, no-network, quotas CPU/RAM/disk.
- **IP / RGPD datasets** : politique applicable aux datasets *internes à l'organisme hôte* et aux datasets DOI-pinés de `nirs4all-datasets` (rétention, lineage, ré-exécutabilité). Pas de gestion de dataset uploadé par un tiers — l'arena ne reçoit pas de dépôt externe.
- **Compatibilité environnements Python lourds** par worker : workers TF / Torch / JAX différents ? routage par capacité ?
- **Coût des transferts** : datasets et artefacts (modèles fittés peuvent peser >1 GB) — pré-positionnement vs streaming.
- **Idempotence et reprise** : worker meurt mid-job → retry sur autre worker sans corrompre le workspace.
- **Quotas et fairness** : un utilisateur ne monopolise pas le cluster.
- **Scheduling hétérogène** : GPU vs CPU, mémoire, slots dédiés.

### Cas d'usage qui justifient (et ceux qui ne justifient pas)

**Justifient** : grid search / HPO lourds (AOM × N preprocessings × seeds × datasets), pré-entraînement *foundation model* NIRS, distributed cross-validation, nightly cron arena, calcul fédéré inter-organismes, simulation extensive avec `nirs4all-lab`.

**Ne justifient pas** : usager calibration quotidien (10-1000 samples, tient sur un laptop), démo / tutoriel, single-pipeline single-dataset.

### Recommandation (pour le jour où le sujet est instruit)

**0-12 mois** : ne pas étendre `nirs4all-cluster` au-delà du prototype public. Prototyper **Option C** en priorité, comme module / extra dans `nirs4all` (par ex. `nirs4all[dask]`). Cible *power users* labo avec leur propre cluster Dask. Démontre techniquement et sert le compute interne de l'arena (matrice méthode × scenario). Critères de validation explicites (voir critères go/no-go ci-dessous).

**12-24 mois** : conditionné à (i) prototype Dask validé, (ii) couplage `dag-ml` ↔ `nirs4all` effectif, (iii) spec du transport remote controller écrite et revue. *Alors* Option B — host controllers `dag-ml` avec RPC distant.

**24m+** : Option A ou D uniquement si un cas d'usage tiers émerge (ex. besoin d'exécution multi-organismes fédérée ou batch communautaire piloté par CIRAD) *et* qu'un financement / équipe dédiés arrivent. En aucun cas comme plateforme de soumission publique type Kaggle.

**Jamais commencer par D.** Piège classique des projets « plateforme ML ».

### Critères de go/no-go pour le spike Dask (Option C)

Le go est conditionnel à toutes ces conditions :
1. ≥ 2 labos / partenaires demandent explicitement l'exécution distribuée.
2. Speedup ≥ 3× mesuré sur un workload réel (grid search AOM / HPO sur ≥ 32 datasets).
3. Résultats *bit-identiques ou metric-identiques* (≤ 1e-10) à l'exécution mono-machine.
4. Modèle data + sécurité + reprise écrit avant le code.
5. **Aucun nouveau dépôt** créé — uniquement un module dans `nirs4all`.

Sans ces 5 conditions : no-go.

---
