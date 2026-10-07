"""Execute the existing release smoke contract inside the public SDK image."""
import hashlib
import json
import sys
from importlib.metadata import version
from pathlib import Path

import n4m
import nirs4all
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold

expected = "1.4.5"
assert version("nirs4all") == expected
assert nirs4all.__version__ == expected
assert n4m.abi_version()[:2] == (2, 17)
assert n4m.version().split("+abi.")[0] == version("nirs4all-methods")
rng = np.random.default_rng(42)
X = rng.normal(size=(30, 8))
y = X[:, 0] * 1.2 - X[:, 1] * 0.4 + rng.normal(scale=0.05, size=30)
with nirs4all.run(
    [KFold(3), Ridge(alpha=1.0)],
    (X, y),
    engine="dag-ml",
    verbose=0,
    save_artifacts=False,
    save_charts=False,
) as result:
    assert result.execution_engine == "dag-ml"
    score = float(result.cv_best_score)
    assert np.isfinite(score)
module_origins = {}
for name, module in sorted(sys.modules.items()):
    if name.split(".", 1)[0] not in {
        "nirs4all", "n4m", "dag_ml", "dag_ml_data", "nirs4all_core",
        "nirs4all_io", "nirs4all_formats", "polars", "numpy", "sklearn",
    } or not getattr(module, "__file__", None):
        continue
    path = Path(module.__file__).resolve()
    module_origins[name] = {
        "path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
print(json.dumps({
    "status": "PASS",
    "sdk_version": expected,
    "sdk_module": nirs4all.__file__,
    "loaded_module_origins": module_origins,
    "methods_version": n4m.version(),
    "methods_abi": list(n4m.abi_version()),
    "execution_engine": "dag-ml",
    "cv_best_score": score,
    "installed_versions": {name: version(name) for name in (
        "nirs4all", "nirs4all-methods", "dag-ml", "dag-ml-data",
        "nirs4all-core", "nirs4all-io", "polars", "numpy", "scikit-learn",
    )},
}, sort_keys=True))
