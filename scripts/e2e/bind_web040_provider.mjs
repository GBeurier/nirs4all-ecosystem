// Recompute the immutable Web040 provider's actual served buffers. Numerical
// conversion, schema planning and sample alignment stay in the public provider.
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'

const repo = process.argv[2]
const commit = 'c7070d5defee6ea29d0f42e240a81b4f487e28c8'
const root = mkdtempSync(join(tmpdir(), 'n4a-web040-provider-'))
const show = (file) => execFileSync('git', ['-C', repo, 'show', `${commit}:web-app/src/engine/${file}`], { maxBuffer: 32 * 1024 * 1024 })
const sha = (bytes) => createHash('sha256').update(bytes).digest('hex')
try {
  const ts = (await import(pathToFileURL(join(repo, 'web-app/node_modules/typescript/lib/typescript.js')).href)).default
  for (const name of ['dag_ml_data_wasm.js', 'dag_ml_data_wasm_bg.wasm']) {
    writeFileSync(join(root, name), show(`wasm/dagml-data/${name}`))
  }
  for (const name of ['dag_ml_wasm.js', 'dag_ml_wasm_bg.wasm']) {
    writeFileSync(join(root, name), show(`wasm/dagml/${name}`))
  }
  writeFileSync(join(root, 'package.json'), '{"type":"module"}')
  for (const name of ['relations', 'dagml-data']) {
    let source = show(`${name}.ts`).toString('utf8')
    if (name === 'dagml-data') {
      const loader = "import { loadDagMlDataWasm } from './nirs4all-core'"
      const relations = "from './relations'"
      if (source.split(loader).length !== 2 || source.split(relations).length !== 2) throw new Error('unexpected immutable provider imports')
      source = source.replace(loader, `import * as nativeData from './dag_ml_data_wasm.js'
import { readFileSync } from 'node:fs'
nativeData.initSync({module:readFileSync(new URL('./dag_ml_data_wasm_bg.wasm', import.meta.url))})
async function loadDagMlDataWasm() { return nativeData }`)
      source = source.replace(relations, "from './relations.mjs'")
    }
    const emitted = ts.transpileModule(source, { compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022 } })
    writeFileSync(join(root, `${name}.mjs`), emitted.outputText)
  }
  const dataset = JSON.parse(readFileSync(0, 'utf8'))
  const { materializeViaProvider } = await import(pathToFileURL(join(root, 'dagml-data.mjs')).href)
  const native = await import(pathToFileURL(join(root, 'dag_ml_data_wasm.js')).href)
  if (native.dag_ml_data_version() !== '0.2.10') throw new Error('unexpected immutable provider version')
  const served = await materializeViaProvider({ ...dataset, X: Float64Array.from(dataset.X), y: Float64Array.from(dataset.y) })
  const train = dataset.partitions.flatMap((partition, i) => partition === 'train' ? [i] : [])
  const dag = await import(pathToFileURL(join(root, 'dag_ml_wasm.js')).href)
  dag.initSync({ module: readFileSync(join(root, 'dag_ml_wasm_bg.wasm')) })
  if (dag.dag_ml_version() !== '0.3.34') throw new Error('unexpected immutable fold runtime version')
  const folds = JSON.parse(dag.kfold_split_json(JSON.stringify({ n_splits: 3, shuffle: true, seed: 42 }), JSON.stringify(train.map(i => `s${i}`)), 'outer'))
  const validation_sample_ids = folds.folds.map(fold => fold.validation_sample_ids.map(id => String(dataset.sampleIds[Number(id.slice(1))])).sort())
  const X = Float64Array.from(train.flatMap(i => Array.from(served.X.subarray(i * dataset.nFeatures, (i + 1) * dataset.nFeatures))))
  const y = Float64Array.from(train.map(i => served.y[i]))
  process.stdout.write(JSON.stringify({ data_content_fingerprint: sha(Buffer.from(X.buffer)), target_content_fingerprint: sha(Buffer.from(y.buffer)), fingerprints: served.fingerprints, validation_sample_ids }))
} finally {
  rmSync(root, { recursive: true, force: true })
}
