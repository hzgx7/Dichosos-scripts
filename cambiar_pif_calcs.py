#!/usr/bin/env python3

import re

INPUT_FILE = "pif.calcs"
OUTPUT_FILE = "pif.calcs1"

NEW_TEMPLATE = """#- - - - - - - - - - - - - -#
start_meppoint {NAME} gaussian
%nproc=8
%mem=10GB
%chk=[Pilgrim_name].chk
#p M08HX/6-31+G(d,p)
scf=(xqc,verytight)
guess=(mix,always)
IOP(1/7=10,1/26=5) IOP(2/17=4)
nosymm
[Pilgrim_gradientcalc_start]
force
[Pilgrim_gradientcalc_end]
[Pilgrim_hessiancalc_start]
freq=noraman
[Pilgrim_hessiancalc_end]

Input file for MEP calculation

{CHARGE_MULT}
[Pilgrim_geometry]

end_meppoint
#- - - - - - - - - - - - - -#

"""

def extract_blocks(filename):
    with open(filename) as f:
        content = f.read()

    pattern = r"start_meppoint\s+(\S+)\s+gaussian(.*?)end_meppoint"
    matches = re.findall(pattern, content, re.DOTALL)

    blocks = []
    for name, block in matches:
        # Buscar línea de carga y multiplicidad (ej: 0 2)
        cm_match = re.search(r"\n\s*(\d+\s+\d+)\s*\n", block)
        charge_mult = cm_match.group(1) if cm_match else "0 1"
        blocks.append((name, charge_mult))

    return blocks

def main():
    blocks = extract_blocks(INPUT_FILE)

    with open(OUTPUT_FILE, "w") as out:
        out.write("#-------------------------#\n")
        out.write("# MEP POINT CALCULATIONS  #\n")
        out.write("#-------------------------#\n\n")

        for name, charge_mult in blocks:
            out.write(NEW_TEMPLATE.format(NAME=name,
                                          CHARGE_MULT=charge_mult))

    print(f"Convertidos {len(blocks)} bloques correctamente.")

if __name__ == "__main__":
    main()

