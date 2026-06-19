import os

SCAN_FILE = "scan_min44.out.scan"
OUTDIR    = "MIN44_freq"

if not os.path.exists(OUTDIR):
    os.mkdir(OUTDIR)

with open(SCAN_FILE, "r") as f:
    lines = f.readlines()

geometries = []
i = 0
while i < len(lines):
    line = lines[i].strip()
    # El formato es: primera línea = número de átomos (solo un número)
    if line.isdigit():
        natoms = int(line)
        i += 1
        # Segunda línea = "scf done: energía" — la saltamos
        i += 1
        # Siguientes natoms líneas = geometría
        geom = []
        for _ in range(natoms):
            parts = lines[i].split()
            symbol = parts[0]
            x      = parts[1]
            y      = parts[2]
            z      = parts[3]
            geom.append((symbol, x, y, z))
            i += 1
        geometries.append(geom)
    else:
        i += 1

print(f"Se encontraron {len(geometries)} geometrias optimizadas.")

for idx, geom in enumerate(geometries, start=1):
    filename = os.path.join(OUTDIR, f"freq_{idx}.com")
    with open(filename, "w") as f:
        f.write("%nprocshared=8\n")
        f.write("%mem=12GB\n")
        f.write("#p M08HX/6-31+G(d,p) freq IOP(1/7=10,1/26=5) temperature=298 IOP(2/17=4) scf=(xqc,maxcycle=1000) guess=mix nosymm\n\n")
        f.write(f"MIN1 scan point {idx}\n\n")
        f.write("0 1\n")
        for atom in geom:
            symbol, x, y, z = atom
            f.write(f"{symbol:<2}  {x:>12}  {y:>12}  {z:>12}\n")
        f.write("\n")

print(f"Inputs generados correctamente en carpeta: {OUTDIR}")
