#!/bin/sh
# Rebuild everything, in dependency order. Geometry first (each writes the JSON
# the next one reads), then meshes, then views, then the page.
#   helm_housing  -> housing.json    (the single source of truth)
#   heatsink_shroud -> shroud.json   (the unit's real rear extent)
#   bail          -> bail.json       (reads both)
set -e
cd "$(dirname "$0")/.."
PY=.venv/bin/python
# web3d is deliberately NOT in this list: it is a module now, and assembly.py
# calls it with the same shapes it renders. (And a comment cannot go inside the
# backslash continuation below - it ends the line and breaks the loop.)
for s in helm_housing heatsink_shroud bail helm_visor assembly_check print_check sensor_tray fit_coupon \
         lp24_mount lp24_shroud lp24_upright_mount lp24_wedge_mount \
         export_mesh render assembly exploded annotate assembly_dims \
         measured_parts seal_detail subassemblies build_review build_manual; do
  if out=$($PY "cad/$s.py" 2>&1); then
    printf '%-18s ok\n' "$s"
  else
    printf '%-18s FAIL\n' "$s"
    printf '%s\n' "$out" | tail -6 | sed 's/^/    /'
  fi
done
cp cad/out/review.html docs/index.html
cp cad/out/manual.html docs/manual.html
echo "docs/index.html updated"
# and out of the gitignored build directory into the tracked one
./tools/publish_assets.sh
