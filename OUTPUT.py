#!/usr/bin/env python3  # Indica ao sistema que este ficheiro debe executarse usando Python 3. É unha liña estándar chamada "shebang".

'''
Este script está escrito en Python 3. O seu obxectivo é recoller todos os ficheiros de saída
(.log) xerados por AMK durante a descomposición dunha molécula e renomealos co nome
estandarizado que AMK asigna nos ficheiros MINinfo, TSinfo e PRODinfo.

É dicir: AMK xera moitos logs con nomes feos ou longos, e este script busca cal é o
nome AMK asignado internamente (por exemplo MIN15, TS03, PROD21_SP) e renomea os
logs orixinais para que teñan eses nomes.

AMK garda moita información en bases de datos SQLite (.db): min.db, ts.db e prod.db.
Cada unha contén unha táboa coa correspondencia entre estruturas e nomes.
'''

#------------------------------------------------------------------------------#
#                   SECCIÓN 1 — IMPORTACIÓN DE MÓDULOS                         #
#------------------------------------------------------------------------------#
import os        # Módulo estándar para traballar co sistema de ficheiros: listar carpetas,
                 # comprobar se existen directorios, cambiar de directorio, etc.

import sqlite3   # Biblioteca para abrir bases de datos SQLite (min.db, ts.db, prod.db).
                 # AMK utiliza SQLite para gardar as propiedades das estruturas atopadas.

import shutil    # Biblioteca que permite copiar arquivos dun lugar a outro.
                 # Usarémola para mover e renomear os logs.

#------------------------------------------------------------------------------#
#         SECCIÓN 2 — IDENTIFICACIÓN DE CARPETAS IMPORTANTES                   #
#------------------------------------------------------------------------------#
# Esta parte percorre o directorio actual e busca dúas carpetas cruciais:
# - FINAL_HL_xxx : onde AMK almacena as bases de datos min.db, ts.db, prod.db.
# - tsdirHL_xxx  : onde AMK garda os logs orixinais (TS, IRC, PRODs...)

for i in os.listdir():              # Recorre todos os elementos do directorio actual.
    if i.startswith("FINAL_HL"):   # Se o nome comeza por "FINAL_HL"...
        folder_HL = i+"/"          # Gardamos esa carpeta como ruta.

for archo in os.listdir():          # Segundo bucle para atopar tsdirHL
    if archo.startswith("tsdirHL"): # Carpetas onde AMK garda TS, IRC, PRODs...
        tsdirHL = archo+"/"        # Gardamos a ruta para futuros accesos.

#------------------------------------------------------------------------------#
#                   CREACIÓN DA CARPETA DE SAÍDA "OUTPUT"                      #
#------------------------------------------------------------------------------#
# Aquí imos crear unha carpeta onde se gardarán todos os logs renomeados.
# Esta carpeta está ao mesmo nivel que o script.

if not os.path.exists("OUTPUT/"):  # Comproba se a carpeta OUTPUT non existe.
    os.mkdir("OUTPUT/")            # Se non existe, créase.
    print("OUTPUT directory created")
else:
    print("OUTPUT directory was already created")  # Se xa existe, simplemente avisamos.

#------------------------------------------------------------------------------#
#                         SECCIÓN 3 — FUNCIÓNS                                  #
#------------------------------------------------------------------------------#
# As funcións seguintes encargaranse de:
# - Ler as bases de datos SQLite.
# - Construír os nomes correspondentes.
# - Localizar os logs orixinais.
# - Copialos á carpeta OUTPUT con nomes limpos.


def mints_rename(folder_HL):
    """
    Esta función renomea os MIN (mínimos de enerxía) atopados por AMK.
    A información ven da base de datos min.db, situada en FINAL_HL/.
    Os logs orixinais adoitan estar en tsdirHL/IRC/.
    """

    os.chdir(folder_HL)  # Entramos no cartafol FINAL_HL para acceder á base de datos.

    cur = sqlite3.connect("min.db")  # Abrimos a base min.db. "cur" é o obxecto conexión.

    # Executamos unha consulta SQL: isto devolve todas as filas da táboa "min".
    # Cada fila (row) contén: id, natom, name, lname, energy, zpe, g, geom, freq.
    # O nome "lname" é clave: contén o nome orixinal do ficheiro .log.

    for row in cur.execute("select id,natom,name,lname,energy,zpe,g,geom,freq from min"):

        # Construímos o nome orixinal tal e como AMK o gardou.
        # row[3] = lname → algo coma "IRC_0005.min.log"
        old_name = "_".join(row[3].split(".")[0].split("_")[1:]) + ".log"
        # Explicación:
        # - row[3].split(".")[0] elimina extensión
        # - split("_") separa por guión baixo
        # - [1:] elimina o primeiro bloque porque AMK engade información extra
        # - "_".join(...) reconstrúe o nome

        new_name = "MIN" + str(row[0])  # row[0] = id → construímos MIN1, MIN2, MIN3...

        print(new_name, old_name)  # Mostramos a equivalencia atopada.

        # Copiamos o arquivo .log orixinal cara OUTPUT
        shutil.copyfile(
            "../" + tsdirHL + "IRC/" + old_name,
            "../OUTPUT/" + new_name + ".out"
        )

    # Agora repetimos exactamente o mesmo proceso para TS.
    cur = sqlite3.connect("ts.db")

    for row in cur.execute("select id,natom,name,lname,energy,zpe,g,geom,freq from ts"):
        old_name = "_".join(row[3].split(".")[0].split("_")[1:]) + ".log"
        new_name = "TS" + str(row[0])   # Forma estándar para TS

        print(str(row[2]).zfill(3), old_name)  # row[2] = name → imprimimos con ceros á esquerda

        shutil.copyfile(
            "../" + tsdirHL + old_name,
            "../OUTPUT/" + new_name + ".out"
        )

    os.chdir("../")  # Saímos da carpeta FINAL_HL.



def prods_rename(folder_HL):
    """
    Renomea os PRODs (produtos) que aparecen na base prod.db.
    Os produtos poden ou non vir dunha ruta con disociación.
    AMK mete os disociativos na carpeta DISS.
    """

    os.chdir(folder_HL)

    cur = sqlite3.connect("prod.db")  # Abrimos prod.db

    for row in cur.execute("select id,natom,name,energy,zpe,g,geom,freq,formula from prod"):

        # row[2] = name, que leva formato tipo:  "12_CH3CH2"
        old_name = "_".join(row[2].split("_")[1:]) + ".log"

        # Renomeamos como PROD_SP
        new_name = '{:0>3}'.format(row[2].split("_")[0] + "_SP")

        print(new_name.zfill(3), old_name)

        # Se NON é disociativo
        if "diss" not in old_name:
            shutil.copyfile(
                "../" + tsdirHL + "IRC/" + old_name,
                "../OUTPUT/" + new_name + ".out"
            )

        # Se é un produto disociativo AMK colócao nunha carpeta separada "DISS"
        if "diss" in old_name:
            shutil.copyfile(
                "../" + tsdirHL + "IRC/DISS/" + old_name,
                "../OUTPUT/" + new_name + ".out"
            )

    os.chdir("../")



def prods_rename_opt():
    """
    Renomea produtos optimizados dentro de tsdirHL/PRODs.
    Aquí a lóxica é distinta: AMK pode dividir un PROD en dous fragmentos
    e ás veces os nomes non coinciden cos esperados, polo que hai que
    recuperar as correspondencias desde o ficheiro fraglist.
    """

    os.chdir(tsdirHL + "PRODs/")

    # PRlist_frag contén pares de fragmentos por PROD
    with open('PRlist_frag','r') as asdf:
        for line in asdf:
            line = line.split()

            if line[1] != "list":  # Filtramos liñas válidas

                new_name_a = "PR" + str(line[1]) + "_a"  # Nome do fragmento A
                new_name_b = "PR" + str(line[1]) + "_b"  # Nome do fragmento B

                name_frag_a = str(line[3]) + ".log"
                name_frag_b = str(line[5]) + ".log"

                # --- Copiamos fragmento A ---
                try:
                    shutil.copyfile(
                        "CALC/" + name_frag_a,
                        "../../OUTPUT/" + new_name_a + ".out"
                    )
                    print("OK,", name_frag_a, " copied to: ", new_name_a)

                except:  # Se falta o fragmento
                    print("This fragment is not computed", name_frag_a)

                    # Buscamos alternativa no fraglist
                    with open('CALC/working/fraglist','r') as asdf2:
                        for l2 in asdf2:
                            l2 = l2.strip().split()
                            if l2[1] == name_frag_a[:-4]:
                                shutil.copyfile(
                                    "CALC/" + l2[2] + ".log",
                                    "../../OUTPUT/" + new_name_a + ".out"
                                )
                                print("OK, trouble solved..,", l2[2] + ".log", " copied to:", new_name_a)
                                break

                # --- Copiamos fragmento B ---
                try:
                    shutil.copyfile(
                        "CALC/" + name_frag_b,
                        "../../OUTPUT/" + new_name_b + ".out"
                    )
                    print("OK,", name_frag_b, " copied to: ", new_name_b)

                except:
                    print("This fragment is not computed", name_frag_b)

                    with open('CALC/working/fraglist','r') as asdf3:
                        for l3 in asdf3:
                            l3 = l3.strip().split()
                            if l3[1] == name_frag_b[:-4]:
                                shutil.copyfile(
                                    "CALC/" + l3[2] + ".log",
                                    "../../OUTPUT/" + new_name_b + ".out"
                                )
                                print("OK, trouble solved..,", l3[2], " copied to: ", new_name_b)
                                break

            continue


#------------------------------------------------------------------------------#
#                      SECCIÓN 4 — EXECUCIÓN DO SCRIPT                         #
#------------------------------------------------------------------------------#
# Finalmente executamos as tres funcións nesta orde:
# 1) Renomea mínimos (MIN)
# 2) Renomea produtos xerais (PRODs)
# 3) Renomea produtos optimizados (PRODs avanzados)

mints_rename(folder_HL)
prods_rename(folder_HL)
prods_rename_opt()

