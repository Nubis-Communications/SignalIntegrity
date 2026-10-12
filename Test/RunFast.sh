#!/bin/bash
# Usage: RunFast.sh [SECONDS]   (default threshold: 1.0 seconds)
THRESHOLD="${1:-1.0}"
export PYTHONPATH=$PYTHONPATH:.
python3 ./TestSignalIntegrity/RunTimedTests.py --faster-than "$THRESHOLD"
