# W46 report - Web cross-runtime fixtures

Summary:
Extended the Web RT goldens into a cross-language fixture contract by adding a Python runtime fixture-shape file and enforcing it in the golden tests.

Code changed:
Web RtResult prediction blocks now emit the Python-compatible `y_proba` field as `null` when Web has no probability arrays. The W37 success and scheduler-fallback goldens include that field. Runtime golden tests now check RtResult/RtError field sets against the Python fixture shape, the ecosystem runtime schemas when reachable, and any sibling Python-published shape file when present.

Files touched:
studio-lite/src/engine/rt-result.ts
studio-lite/src/engine/rt-result.goldens.test.ts
studio-lite/src/engine/fixtures/runtime/python_rt_fixture_shape.v1.json
studio-lite/src/engine/fixtures/runtime/rt_result.success.v1.json
studio-lite/src/engine/fixtures/runtime/rt_result.scheduler_fallback.v1.json
/home/delete/nirs4all/nirs4all-ecosystem/docs/agent_reports/W46_WEB_CROSS_RT.md

Commits:
a7b98bd test(studio-lite): pin cross-runtime rt fixtures

Tests run:
npx vitest run --config vitest.config.ts src/engine/rt-result.goldens.test.ts src/engine/rt.contract.test.ts src/engine/dagml-engine.rt-fallback.test.ts src/engine/rt.test.ts
npm run typecheck
npm run build
npm run test
npx vitest run --config vitest.config.ts src/engine/rt-result.goldens.test.ts
git diff --check

Tests not run and why:
build:single and browser smoke suite were not run; W46 gate asked for targeted Vitest, typecheck, and build, and this change is limited to runtime fixture projection/tests with no UI workflow changes.

Blockers:
None.

Impact on blockers/locks:
B-018 advances: Web fixtures now expose a Python-consumable field shape and catch drift in RtResult/RtError field sets. LOCK-RT remains additive; no runtime execution behavior changed beyond the neutral `y_proba: null` projection field.

Next action:
Have the Python W43 side publish the same `python_rt_fixture_shape.v1.json` path or equivalent field sections so Web's optional sibling comparison becomes an active cross-repo drift gate.

Sync doc updated: no
