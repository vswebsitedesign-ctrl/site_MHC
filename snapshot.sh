#!/bin/bash
LABEL=${1:-"snapshot"}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SNAP_DIR="snapshots/${TIMESTAMP}_${LABEL}"
mkdir -p "$SNAP_DIR"
cp Master_Report.json "$SNAP_DIR/"
cp build.py "$SNAP_DIR/"
cp theme/base.html "$SNAP_DIR/"
cp data/pages.json "$SNAP_DIR/"
echo "✅ Snapshot saved to $SNAP_DIR"
