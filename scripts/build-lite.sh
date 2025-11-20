#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LITE_KERNEL_DIR="$ROOT_DIR/lite-kernel"
LITE_SITE_DIR="$ROOT_DIR/lite-site"
LITE_OUTPUT_DIR="$LITE_SITE_DIR/_output"

echo "[build-lite] Building TypeScript sources in $LITE_KERNEL_DIR"
npm --prefix "$LITE_KERNEL_DIR" run build

echo "[build-lite] Copying bundle into $LITE_SITE_DIR/extensions/lite-kernel"
mkdir -p "$LITE_SITE_DIR/extensions/lite-kernel"
cp "$LITE_KERNEL_DIR/dist/index.js" "$LITE_SITE_DIR/extensions/lite-kernel/index.js"

echo "[build-lite] Cleaning previous Lite site at $LITE_OUTPUT_DIR"
rm -rf "$LITE_OUTPUT_DIR"

echo "[build-lite] Running jupyter lite build"
(
  cd "$LITE_SITE_DIR"
  jupyter lite build --output-dir "$LITE_OUTPUT_DIR"
)

echo "[build-lite] Installing extension bundle into built site"
mkdir -p "$LITE_OUTPUT_DIR/extensions/lite-kernel"
cp "$LITE_KERNEL_DIR/dist/index.js" "$LITE_OUTPUT_DIR/extensions/lite-kernel/index.js"

echo "[build-lite] Ensuring lite-kernel is registered in jupyter-lite.json"
python3 - <<PY
import json
from pathlib import Path

# Use the output dir computed by this script
config_path = Path("$LITE_OUTPUT_DIR") / "jupyter-lite.json"

if config_path.exists():
    data = json.loads(config_path.read_text())
    config = data.setdefault("jupyter-config-data", {})
    fed_exts = config.setdefault("federated_extensions", [])

    has_kernel = any(e.get("name") == "lite-kernel" for e in fed_exts)

    if not has_kernel:
        print("[build-lite] Injecting lite-kernel into jupyter-lite.json")
        fed_exts.append({
            "name": "lite-kernel",
            "load": "index.js",
            "extension": "./index"
        })
        config_path.write_text(json.dumps(data, indent=2))
    else:
        print("[build-lite] lite-kernel already present in config")
else:
    print(f"[build-lite] Warning: jupyter-lite.json not found at {config_path}")
PY

echo "[build-lite] Build complete → $LITE_OUTPUT_DIR"