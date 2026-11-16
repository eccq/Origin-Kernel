#!/usr/bin/env python3
"""Fail the build when exported symbol CRCs drift from the Android KMI.

Vendor modules on the phone were built against the KMI in android/abi_gki_aarch64.stg.
If our kernel exports a different CRC for a symbol they use, they refuse to load and the
phone bootloops. Pass the vendor symbol lists (android/abi_gki_aarch64_mtk, _nothing) to
check only what the modules actually import; without them every KMI symbol is checked.
"""
import re
import sys

stg_path, symvers_path = sys.argv[1], sys.argv[2]
lists = sys.argv[3:]

wanted = set()
for path in lists:
    for line in open(path):
        line = line.strip()
        if line and not line.startswith(('#', '[')):
            wanted.add(line)

kmi = {}
for block in re.finditer(r'elf_symbol \{(.*?)\n\}', open(stg_path).read(), re.S):
    body = block.group(1)
    name = re.search(r'\n  name: "([^"]+)"', body)
    crc = re.search(r'\n  crc: (0x[0-9a-f]+)', body)
    if name and crc:
        kmi[name.group(1)] = int(crc.group(1), 16)

ours = {}
for line in open(symvers_path):
    fields = line.split('\t')
    if len(fields) >= 2:
        ours[fields[1]] = int(fields[0], 16)

checked = [s for s in kmi if s in ours and (not wanted or s in wanted)]
bad = [s for s in checked if ours[s] != kmi[s]]
scope = f"{len(wanted)} vendor symbols" if wanted else "the whole kmi"
print(f"checked {len(checked)} symbols ({scope}), mismatches: {len(bad)}")
for s in bad[:20]:
    print(f"  {s}: kernel {ours[s]:#010x}, kmi {kmi[s]:#010x}")
if not checked:
    sys.exit("no kmi symbols found in Module.symvers, nothing was checked")
sys.exit(1 if bad else 0)
