# nirs4all-ecosystem

> **Ce dépôt n'est pas un monorepo.** C'est un dépôt parent *minimal* qui regroupe
> les projets de l'écosystème **nirs4all** sous forme de **submodules Git**.
> Chaque projet reste un **dépôt indépendant** (historique, issues, releases et
> droits d'accès propres). Ce dépôt ne fait que **référencer un commit précis** de
> chacun — il ne contient pas leur code.

## Projets référencés

| Submodule | Branche suivie | Visibilité |
| --- | --- | --- |
| `nirs4all-aom` | `main` | public |
| `dag-ml` | `main` | public |
| `dag-ml-data` | `main` | public |
| `nirs4all-arena` | `main` | public |
| `nirs4all` | `main` | public |
| `nirs4all-studio` | `master` | public |
| `nirs4all-web` | `main` | public |
| `nirs4all-lite` | `main` | public |
| `nirs4all-org` | `main` | public |
| `nirs4all-drafts` | `main` | **privé** |
| `nirs4all-papers` | `main` | public |
| `nirs4all-lab` | `main` | public cible, actuellement privé |
| `nirs4all-formats` | `main` | public |
| `nirs4all-io` | `main` | public |
| `nirs4all-methods` | `main` | public |
| `nirs4all-datasets` | `main` | public |
| `nirs4all-cluster` | `main` | public |

> **`nirs4all-formats` vs `nirs4all-io`.** Les responsabilités de lecture de
> fichiers et d'assemblage de jeux de données ont été séparées :
> - **`nirs4all-formats`** (anciennement `nirs4all-io`) : bibliothèque Rust de
>   *lecteurs* de fichiers spectroscopiques (lecture seule, ~45 formats).
> - **`nirs4all-io`** (nouveau) : *pont d'assemblage* de jeux de données
>   (résolution → inférence → configuration → matérialisation). Python en phase 1
>   (compatible `SpectroDataset`), Rust en phase 2 (compatible `dag-ml-data`).
>   Il consomme `nirs4all-formats` pour la lecture des fichiers.

## Cloner

Clone complet (parent + contenu des submodules) :

```bash
git clone --recurse-submodules git@github.com:GBeurier/nirs4all-ecosystem.git
```

Initialiser les submodules après un clone simple :

```bash
git submodule update --init --recursive
```

### Pull partiel (submodules privés)

`nirs4all-drafts` reste **privé**. Pendant la migration, `nirs4all-lab` peut
encore être privé sur GitHub tant qu'un audit de publication n'a pas confirmé
qu'il ne contient rien de sensible. Un dépôt public peut référencer des submodules
privés (seule l'URL est exposée, pas le contenu). Sans les droits d'accès, l'init
global échoue *sur ces submodules uniquement* ; les autres s'initialisent
normalement. Pour n'initialiser que ce à quoi vous avez accès, ciblez les chemins
voulus :

```bash
git submodule update --init nirs4all nirs4all-formats nirs4all-io   # exemple
```

## Mettre à jour

Amener tous les submodules au dernier commit de leur branche suivie :

```bash
git submodule update --remote --merge
```

Status global de tous les submodules :

```bash
git submodule foreach 'git status --short'
```

## Figer l'état

Après un `git submodule update --remote --merge`, les pointeurs de submodules ont
bougé localement mais **ne sont pas figés**. Pour figer l'état dans le dépôt
parent, il faut **committer les pointeurs** :

```bash
git add .
git commit -m "Update submodule pointers"
git push
```

## Script

```bash
./pull-all.sh   # met à jour le parent, (re)init puis synchronise les submodules
```
