#!/usr/bin/env python3
import os
import shutil
import string
import networkx as nx
import RXReader as arx
import RXVisualizer as arxviz

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

BASE = "FINAL_HL_C6H6"
RXNET = os.path.join(BASE, "RXNet.cg")
RXNET_BL = os.path.join(BASE, "RXNet.barrless")

OUTDIR = "OUTPUT"
PILGRIM_DIR = "UDATA"
CHEM_DIR = "chem_C6H6"
CHEM_FILE = os.path.join(CHEM_DIR, "pif.chem")

TS_BARRIERLESS_OFFSET = 800

# ============================================================
# ENTRADAS DEL USUARIO
# ============================================================

finaldir = BASE
fmin  = os.path.join(BASE, "MINinfo_zpecorr")
fprod = os.path.join(BASE, "PRODinfo_zpecorr")
fts   = os.path.join(BASE, "TSinfo_zpecorr")

start_path = ["MIN1"]
max_length = 3
E_cutoff = 142.7 # kcal/mol
WITH_PROFILES = True

# ============================================================
# COLORES ANSI
# ============================================================

RESET   = "\033[0m"
BOLD    = "\033[1m"
RED     = "\033[91m"
BLUE    = "\033[94m"
GREEN   = "\033[92m"
MAGENTA = "\033[95m"
GRAY    = "\033[90m"

CHEM_HEADER = """#-----------------------------------------------#
#  Pilgrim pif.chem
#-----------------------------------------------#
"""

# ============================================================
# FUNCIONES BÁSICAS (Etiquetas, Energías, Parser)
# ============================================================

def reaction_label(i):
    letters = string.ascii_lowercase
    return letters[i % 26] if (i // 26) == 0 else f"{letters[i % 26]}{i // 26}"

def read_energies(fname, prefix):
    energies = {}
    if not os.path.isfile(fname):
        return energies
    with open(fname) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            parts = line.split()
            try:
                energies[f"{prefix}{int(parts[0])}"] = float(parts[1])
            except: continue
    return energies

def load_all_energies():
    e = {}
    e.update(read_energies(fmin,  "MIN"))
    e.update(read_energies(fprod, "PR"))
    e.update(read_energies(fts,   "TS"))
    return e

def parse_rxnet(fname, barrierless=False):
    reactions = []
    if not os.path.isfile(fname): return reactions
    with open(fname) as f:
        for line in f:
            l = line.split()
            if not l or not l[0].isdigit() or "DIS" in line: continue
            
            tsnum = int(l[0])
            if barrierless: tsnum += TS_BARRIERLESS_OFFSET
            ts_label = f"TS{tsnum}"
            rmin = f"MIN{int(l[3])}"
            bidirectional = (l[4] == "<--->")
            prod = f"PR{int(l[5][2:-1])}" if "PR" in l[5] else f"MIN{int(l[6])}"
            
            reactions.append((rmin, ts_label, prod, barrierless))
            if bidirectional and not prod.startswith("PR"):
                reactions.append((prod, ts_label, rmin, barrierless))
    return reactions

def build_reactions():
    return parse_rxnet(RXNET, False) + parse_rxnet(RXNET_BL, True)

# ============================================================
# BÚSQUEDA DE CAMINOS (DFS del Script 2)
# ============================================================

def path_is_valid(path, edge2ts, energies):
    if len(path) - 2 > max_length: return False
    for sp in path:
        if energies.get(sp, 0.0) > E_cutoff: return False
    for i in range(len(path) - 1):
        ts = edge2ts[(path[i], path[i+1])]
        if energies.get(ts, 0.0) > E_cutoff: return False
    return True

def find_paths(reactions, energies):
    adj, edge2ts, edge2nobar = {}, {}, {}
    unique_reactions = []
    seen_reactions = set()

    for r, ts, p, nobar in reactions:
        key = (r, ts, p, nobar)
        if key not in seen_reactions:
            seen_reactions.add(key)
            unique_reactions.append((r, ts, p, nobar))

    for r, ts, p, nobar in unique_reactions:
        e_ts = energies.get(ts, 0.0)
        if (r, p) not in edge2ts:
            adj.setdefault(r, []).append(p)
            edge2ts[(r, p)] = ts
            edge2nobar[(r, p)] = nobar
        else:
            if e_ts < energies.get(edge2ts[(r, p)], 0.0):
                edge2ts[(r, p)] = ts
                edge2nobar[(r, p)] = nobar
        
        if nobar: # Asignar la energía del producto al TS dummy si es barrierless
            energies[ts] = energies.get(p, energies.get(r, 0.0))

    valid_paths = []
    def dfs(path):
        last = path[-1]
        if last.startswith("PR"):
            if path_is_valid(path, edge2ts, energies):
                valid_paths.append(path)
            return
        if len(path) >= max_length + 2: return
        for nxt in adj.get(last, []):
            if nxt not in path: dfs(path + [nxt])

    dfs(start_path)
    
    unique_paths = []
    seen_paths = set()
    for p in valid_paths:
        t = tuple(p)
        if t not in seen_paths:
            seen_paths.add(t)
            unique_paths.append(p)

    return unique_paths, edge2ts, edge2nobar

# ============================================================
# ESCRITURA Y VISUALIZACIÓN
# ============================================================

def generate_html_map(valid_paths, edge2ts, energies):
    print("\n=== Xerando mapa HTML con RXVisualizer ===")
    
    # 1. Obter todos os nodos e arestas estritamente válidos
    valid_nodes = set()
    valid_edges = set()
    for path in valid_paths:
        for sp in path:
            valid_nodes.add(sp)
        for i in range(len(path)-1):
            valid_edges.add((path[i], path[i+1]))
            
    # 2. Ler o grafo completo base de AutoMeKin para extraer os seus atributos (cores, etc)
    data_cg = arx.RX_parser(finaldir, "RXNet.cg")
    G_amk = arx.RX_builder(finaldir, data_cg)
    try:
        data_bl = arx.RX_parser(finaldir, "RXNet.barrless")
        G_bl = arx.RX_builder(finaldir, data_bl)
        G_amk = nx.compose(G_amk, G_bl)
    except:
        pass
        
    # 3. Construír un subgrafo LIMPO só cos camiños atopados polo teu script
    G_clean = nx.DiGraph()
    
    for n in valid_nodes:
        if n in G_amk.nodes:
            G_clean.add_node(n, **G_amk.nodes[n])
            G_clean.nodes[n]['energy'] = energies.get(n, 0.0)
        else:
            G_clean.add_node(n, energy=energies.get(n, 0.0))
            
    for (u, v) in valid_edges:
        ts_name = edge2ts.get((u, v))
        if G_amk.has_edge(u, v):
            G_clean.add_edge(u, v, **G_amk[u][v])
        else:
            # Recrear atributos para rutas sen barreira que AMK puidese omitir
            G_clean.add_edge(u, v, name=ts_name, ts=ts_name)

    print(f"  Nodos no subgrafo final: {len(G_clean.nodes())}")
    print(f"  Arestas no subgrafo final: {len(G_clean.edges())}")

    outfile = f"{start_path[0]}_to_ALL.html"
    try:
        arxviz.generate_visualization(
            G_clean, finaldir,
            title=f"{start_path[0]} → todos os produtos (E_cutoff={E_cutoff} kcal/mol)",
            outfile=outfile,
            layout_function=nx.kamada_kawai_layout,
            with_profiles=WITH_PROFILES,
            Nvibrations=0
        )
        print(f"✔ HTML xerado correctamente: {outfile}")
    except Exception as e:
        print(f"  ⚠ Erro xerando perfís: {e}")
        print("  Reintentando sen perfís...")
        arxviz.generate_visualization(
            G_clean, finaldir,
            title=f"{start_path[0]} → todos os produtos (E_cutoff={E_cutoff} kcal/mol)",
            outfile=outfile,
            layout_function=nx.kamada_kawai_layout,
            with_profiles=False,
            Nvibrations=0
        )
        print(f"✔ HTML xerado sen perfís: {outfile}")

def print_paths(paths, reactions, energies, edge2ts, edge2nobar):
    paths = sorted(paths, key=lambda p: int(p[-1][2:]))
    print("\n" + BOLD + "===== CAMIÑOS REACCIONAIS VÁLIDOS =====" + RESET + "\n")
    # (Mantemos o teu print intacto para o terminal, omito as liñas de código do print aquí para non alongalo, 
    # pero no teu script deberías deixar a túa función print_paths() tal cal a tes).
    return paths

# ============================================================
# MAIN
# ============================================================

def main():
    reactions = build_reactions()
    energies = load_all_energies()

    # Busca rigorosa DFS
    valid_paths, edge2ts, edge2nobar = find_paths(reactions, energies)
    
    # Xeración do HTML (Novo)
    if valid_paths:
        generate_html_map(valid_paths, edge2ts, energies)
    else:
        print("\n⚠ Non se atoparon camiños válidos co cutoff actual. Non se xerará mapa.")
        
    print("\nProceso completado correctamente ✔\n")

if __name__ == "__main__":
    main()
