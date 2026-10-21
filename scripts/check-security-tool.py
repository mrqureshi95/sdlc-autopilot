#!/usr/bin/env python3
"""Positive/negative controls for a provisioned Gitleaks binary; no network."""
import argparse
import importlib.util
import json
import random
import string
from pathlib import Path
import tempfile
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('evidence',ROOT/'skills/sdlc-autopilot/scripts/evidence.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--binary',type=Path,required=True);args=p.parse_args()
binary=args.binary.resolve()
with tempfile.TemporaryDirectory(prefix='sdlc scanner control ') as tmp:
    root=Path(tmp).resolve(); source=root/'example.txt'
    c={'name':'secrets','kind':'security','argv':[str(binary),'dir','.','--redact','--no-banner','--ignore-gitleaks-allow']}
    source.write_text('Ordinary documentation without credentials.\n')
    clean=e.run_check(c,root,30)
    # Synthetic format-valid canary is assembled at runtime; never a live credential.
    canary=''.join(('gh','p_', ''.join(random.Random(42).choices(string.ascii_letters+string.digits,k=40))))
    source.write_text('access_token="'+canary+'"\n')
    positive=e.run_check(c,root,30)
    if clean['state']!='pass' or positive['state']!='fail':
        print(json.dumps({'clean':clean,'canary':positive},indent=2));raise SystemExit(1)
    if canary in json.dumps(positive): raise SystemExit('Secret content escaped into evidence')
    missing=e.run_check({**c,'argv':[str(root/'missing-scanner')]},root,30)
    if missing['state']!='inconclusive': raise SystemExit('Missing scanner was not inconclusive')
print('Gitleaks clean, synthetic finding, redacted evidence, and missing-tool controls passed.')
