#!/usr/bin/env python3
# ============================================================
# AutoMeKin – amk-tools (robusto CESGA ~2021)
# Red interactiva 2D + 3D (SIN perfiles energéticos)
# MIN1 → PRxx (HTML independiente)
# ============================================================

import RXReader as arx
import RXVisualizer as arxviz
import networkx as nx

# ============================================================
# CONFIGURACIÓN
# ============================================================

finaldir   = "FINAL_HL_C6H6"
rxnfile    = "RXNet.cg"
start_node = "MIN1"
cutoff     = 10   # cutoff topológico (número de pasos)

print("=== Leyendo red AutoMeKin ===")

# ============================================================
# PARSEO Y CONSTRUCCIÓN DEL GRAFO
# ============================================================

data = arx.RX_parser(finaldir, rxnfile)
G    = arx.RX_builder(finaldir, data)

print(f"Nodos totales en la red: {len(G.nodes())}")

# ============================================================
# LISTA DE PRODUCTOS PRxx
# ============================================================

pr_list = sorted([n for n in G.nodes() if n.startswith("PR")])
print(f"Productos encontrados: {pr_list}")

if not pr_list:
    raise RuntimeError("No se encontraron PRxx en la red")

# ============================================================
# BUCLE PRINCIPAL: MIN1 → PRxx
# ============================================================

for pr in pr_list:

    print(f"\n=== Procesando {start_node} → {pr} ===")

    limits = arx.node_synonym_search(G, [[start_node], [pr]])

    path_list = arx.add_paths(
        G,
        limits[0],
        limits[1],
        cutoff=cutoff
    )

    if not path_list:
        print(f"   ⚠ No hay rutas con cutoff={cutoff}")
        continue

    G_sub = arx.graph_path_selector(G, path_list)
    print(f"   Subgrafo con {len(G_sub.nodes())} nodos")

    # ========================================================
    # VISUALIZACIÓN ROBUSTA (recomendada por amk-tools)
    # ========================================================

    arxviz.generate_visualization(
        G_sub,
        finaldir,
        title=f"{start_node} → {pr}",
        outfile=f"{start_node}_to_{pr}.html",
        layout_function=nx.kamada_kawai_layout,
        with_profiles=False,
        Nvibrations=0
    )

    print(f"   ✔ HTML generado: {start_node}_to_{pr}.html")

print("\n=== Proceso completado sin bloqueos ===")

