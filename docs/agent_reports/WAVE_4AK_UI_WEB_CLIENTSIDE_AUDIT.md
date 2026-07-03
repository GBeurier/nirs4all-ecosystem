# Wave 4AK - UI/Web Client-Side Audit

Date: 2026-07-03

## Verdict

Le design vise est concretement en place sur la lane H/UI-Web:

- `nirs4all-ui` est un paquet partage avec exports publics `score`, `runtime` et `components`, publie via `dist` et sans dependance app-specific (`RC-v1-ui/package.json:19`, `RC-v1-ui/src/index.ts:9`, `RC-v1-ui/src/components/RuntimeEngineBadge.tsx:23`).
- Studio consomme `nirs4all-ui` via `file:./vendor/nirs4all-ui`, garde un bridge `@/ui/*` vers le paquet, et adapte seulement l'icone/style cote app (`RC-v1-studio/src/components/runtime/RuntimeEngineBadge.tsx:2`, `RC-v1-studio/src/ui/index.ts:1`).
- Web consomme `nirs4all-ui`, publie une app statique Pages sur `web.nirs4all.org`, et possede un test de contrat qui interdit backend/API runtime, WebSocket, Node builtins et ressources runtime tierces (`RC-v1-web/studio-lite/src/app/client-side-only.test.ts:49`, `RC-v1-web/studio-lite/public/CNAME:1`, `RC-v1-web/.github/workflows/deploy-pages.yml:52`).
- Org et cockpit racontent la meme topologie RC: `nirs4all-core` est le target V1 RC, `nirs4all-lite` reste la ligne artifact legacy/current, `nirs4all-web` est un target Pages client-side-only, et `nirs4all-ui` est suivi separement (`RC-v1-org/index.html:2031`, `RC-v1-org/index.html:2256`, `RC-v1-cockpit/README.md:101`).

## Correctifs appliques

- `RC-v1-org/index.html:2535` et `:2538`: remplacement du libelle abrege `n4a-web` par `nirs4all-web` dans la carte ecosysteme.
- `RC-v1-web/studio-lite/vite.config.ts:8`: commentaire de build corrige vers `web.nirs4all.org` au lieu de `nirs4all.org`.

## Fichiers modifies

- `_worktrees/RC-v1-org/index.html`
- `_worktrees/RC-v1-web/studio-lite/vite.config.ts`
- `_worktrees/RC-v1-ecosystem/docs/agent_reports/WAVE_4AK_UI_WEB_CLIENTSIDE_AUDIT.md`

## Tests lances

- `RC-v1-ui`: `npm run typecheck && npm test && npm run build` - OK, 8 fichiers / 52 tests Vitest.
- `RC-v1-studio`: `npm run check:ui-shim` - OK, vendor `nirs4all-ui` a jour.
- `RC-v1-web/studio-lite`: `npm run check:ui-shim && npm run test:client-only && npm run typecheck` - OK, 2 tests client-only.
- `RC-v1-org`: `rg -n "n4a-web|primary nirs4all\\.org deliverable" index.html README.md || true` puis assertion zero `n4a-web` - OK.

## Risques / suites proposees

- Pas de full parity lancee, conformement au cadrage. Pour une gate plus large Web: `cd _worktrees/RC-v1-web/studio-lite && npm run test && npm run validate:catalog && npm run build && npm run build:single && npm run smoke -- rt-fallback`.
- `nirs4all-ui` reste consomme via shims vendor `file:` jusqu'au premier publish npm; les checks `check:ui-shim` couvrent la derive locale.
- `RC-v1-cockpit` etait deja dirty en lecture seule (`ops/targets.yaml`, `tests/test_targets_topology.py`); je n'y ai rien modifie.

## Decisions

- Corrections limitees aux libelles/naming dans l'ownership.
- Aucun changement runtime, aucun rebuild WASM, aucune modification dans `nirs4all-drafts` ou `nirs4all-lab`.
