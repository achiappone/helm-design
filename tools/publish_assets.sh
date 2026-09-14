#!/bin/sh
# Copy every generated drawing and render into assets/, which IS committed.
#
# cad/out/ is gitignored and always has been - it rebuilds in minutes and a
# repo full of regenerated PNGs is a repo full of noise. But that reasoning
# only holds for someone standing at this machine with the toolchain built.
# From a phone, from another laptop, or in two years when build123d has moved
# on, the drawings ARE the design. So they get copied out, once, into a folder
# that is tracked.
set -e
cd "$(dirname "$0")/.."
mkdir -p assets/renders assets/drawings
cp -f cad/out/*.png assets/renders/ 2>/dev/null || true
cp -f cad/out/*.svg assets/drawings/ 2>/dev/null || true
cp -f docs/index.html assets/build-review.html
printf '%s renders, %s drawings\n' \
  "$(ls assets/renders | wc -l | tr -d ' ')" \
  "$(ls assets/drawings | wc -l | tr -d ' ')"
