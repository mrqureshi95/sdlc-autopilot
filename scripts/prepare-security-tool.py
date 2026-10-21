#!/usr/bin/env python3
"""Explicitly acquire a checksum-pinned Gitleaks binary at a NEW external path.
Never called implicitly by verification; downloads public release assets only.
"""
import argparse
import hashlib
import io
import os
from pathlib import Path
import platform
import tarfile
import urllib.request
import urllib.error

VERSION='8.30.1'
SHA256={
 ('Darwin','arm64'):'b40ab0ae55c505963e365f271a8d3846efbc170aa17f2607f13df610a9aeb6a5',
 ('Darwin','x86_64'):'dfe101a4db2255fc85120ac7f3d25e4342c3c20cf749f2c20a18081af1952709',
 ('Linux','aarch64'):'e4a487ee7ccd7d3a7f7ec08657610aa3606637dab924210b3aee62570fb4b080',
 ('Linux','x86_64'):'551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb',
}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    target=args.output.resolve()
    if target.exists(): p.error('output must be a new directory')
    key=(platform.system(),platform.machine())
    if key not in SHA256: p.error('unsupported binary platform; provision a reviewed scanner manually')
    arch='arm64' if key[1] in ('arm64','aarch64') else 'x64'
    name=f'gitleaks_{VERSION}_{key[0].lower()}_{arch}.tar.gz'
    url=f'https://github.com/gitleaks/gitleaks/releases/download/v{VERSION}/{name}'
    try:
        with urllib.request.urlopen(url,timeout=60) as response:
            raw=response.read(32*1024*1024+1)
    except (urllib.error.URLError, OSError):
        p.error("download failed; check network and the Python TLS trust store (never disable TLS verification)")
    if len(raw)>32*1024*1024 or hashlib.sha256(raw).hexdigest()!=SHA256[key]:
        p.error('release archive failed pinned SHA256 verification')
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as archive:
        member=archive.getmember('gitleaks')
        if not member.isfile() or member.size>64*1024*1024: p.error('invalid binary member')
        binary=archive.extractfile(member).read()
    target.mkdir(parents=True,exist_ok=False)
    with (target/'gitleaks').open('xb') as f: f.write(binary)
    os.chmod(target/'gitleaks',0o755)
    print(f'Prepared Gitleaks {VERSION}; archive SHA256 {SHA256[key]}; path {target / "gitleaks"}')

if __name__=='__main__': main()
