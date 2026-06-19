# README – Script de renomeado e recompilación de ficheiros de saída de AMK

## Descrición xeral

Este script foi desenvolvido para facilitar a análise posterior dos resultados xerados por **AutoMeKin (AMK)** durante a exploración automática de superficies de enerxía potencial e a construción de redes de reacción. Durante a execución dun cálculo, AMK produce un gran número de ficheiros de saída (`.log`) distribuídos en diferentes directorios e identificados mediante nomes internos que non sempre resultan intuitivos para o usuario.

O obxectivo principal do programa é recompilar estes ficheiros e renomealos segundo a nomenclatura estándar empregada por AMK para identificar as diferentes especies químicas da rede:

* **MIN**: mínimos de enerxía.
* **TS**: estados de transición.
* **PROD**: produtos.
* **PR**: fragmentos optimizados de produtos disociativos.

Como resultado, obtense un directorio único denominado `OUTPUT`, que contén todos os ficheiros organizados cunha nomenclatura consistente e facilmente interpretable.

---

## Estrutura de directorios esperada

O script foi deseñado para executarse no directorio principal dun cálculo de AMK e asume a presenza dunha estrutura similar á seguinte:

```text
.
├── FINAL_HL_xxx/
│   ├── min.db
│   ├── ts.db
│   └── prod.db
│
├── tsdirHL_xxx/
│   ├── IRC/
│   ├── IRC/DISS/
│   └── PRODs/
│
└── rename_logs.py
```

Onde:

* `FINAL_HL_xxx` contén as bases de datos SQLite xeradas por AMK.
* `tsdirHL_xxx` almacena os cálculos electrónicos realizados para mínimos, estados de transición e produtos.
* `rename_logs.py` corresponde ao presente script.

---

## Dependencias

O programa emprega exclusivamente módulos estándar de Python:

| Módulo    | Función                                |
| --------- | -------------------------------------- |
| `os`      | Xestión de directorios e rutas         |
| `sqlite3` | Acceso ás bases de datos SQLite de AMK |
| `shutil`  | Copia e renomeado de ficheiros         |

Non é necesario instalar bibliotecas externas adicionais.

---

## Funcionamento xeral

A execución do programa consta de catro etapas principais:

1. Identificación automática dos directorios de traballo.
2. Creación do directorio de saída.
3. Renomeado dos mínimos, estados de transición e produtos.
4. Recuperación e renomeado dos fragmentos optimizados.

---

## Localización automática dos directorios

Ao iniciarse, o script percorre o directorio actual en busca de dous cartafoles fundamentais:

### Directorio FINAL_HL

Identifícase mediante o prefixo:

```text
FINAL_HL
```

Este directorio contén as bases de datos SQLite:

```text
min.db
ts.db
prod.db
```

Nas que AMK almacena información estrutural e enerxética das especies atopadas.

### Directorio tsdirHL

Identifícase mediante o prefixo:

```text
tsdirHL
```

Neste directorio almacénanse os ficheiros de saída orixinais dos cálculos electrónicos.

---

## Creación do directorio OUTPUT

Todos os ficheiros procesados son copiados a un novo directorio denominado:

```text
OUTPUT/
```

Se o directorio non existe, créase automaticamente. En caso contrario reutilízase o xa existente.

Esta estratexia evita modificar os ficheiros orixinais producidos por AMK e garante a conservación íntegra dos resultados iniciais.

---

# Función `mints_rename()`

## Obxectivo

Procesar e renomear os ficheiros correspondentes a:

* Mínimos de enerxía (MIN)
* Estados de transición (TS)

---

## Renomeado dos mínimos

A función accede á base de datos:

```text
min.db
```

e executa a consulta:

```sql
SELECT id,natom,name,lname,energy,zpe,g,geom,freq
FROM min
```

Cada fila da táboa representa un mínimo localizado por AMK.

O campo:

```text
lname
```

contén o nome orixinal do ficheiro de saída.

Por exemplo:

```text
IRC_0005.min.log
```

A partir desta información constrúese unha correspondencia:

```text
IRC_0005.log  →  MIN5.out
```

onde o identificador do mínimo procede do campo `id` da base de datos.

---

## Renomeado dos estados de transición

Posteriormente accédese á base:

```text
ts.db
```

mediante a consulta:

```sql
SELECT id,natom,name,lname,energy,zpe,g,geom,freq
FROM ts
```

e realízase o mesmo procedemento.

Exemplo:

```text
TS_034.log → TS34.out
```

Todos os ficheiros resultantes son copiados ao directorio:

```text
OUTPUT/
```

---

# Función `prods_rename()`

## Obxectivo

Procesar os produtos finais da rede de reacción.

A información obtense da base:

```text
prod.db
```

mediante:

```sql
SELECT id,natom,name,energy,zpe,g,geom,freq,formula
FROM prod
```

---

## Produtos convencionais

Os produtos non disociativos localízanse normalmente en:

```text
tsdirHL/IRC/
```

e son copiados a:

```text
OUTPUT/
```

co formato:

```text
001_SP.out
002_SP.out
003_SP.out
...
```

---

## Produtos disociativos

Cando AMK identifica unha disociación molecular, os ficheiros almacénanse en:

```text
IRC/DISS/
```

A función detecta automaticamente estes casos mediante a presenza da cadea:

```text
diss
```

no nome do ficheiro.

Posteriormente copia o ficheiro correspondente ao directorio final mantendo a nomenclatura estandarizada.

---

# Función `prods_rename_opt()`

## Obxectivo

Procesar os produtos optimizados xerados por AMK.

Esta é a parte máis complexa do programa, xa que os produtos poden fragmentarse durante a optimización.

---

## Lectura de PRlist_frag

O ficheiro:

```text
PRlist_frag
```

contén a correspondencia entre cada produto e os seus posibles fragmentos.

Exemplo simplificado:

```text
PR12 → fragmento A + fragmento B
```

A función analiza esta información e xera automaticamente nomes do tipo:

```text
PR12_a.out
PR12_b.out
```

---

## Copia directa dos fragmentos

Nun primeiro intento o programa busca os ficheiros en:

```text
PRODs/CALC/
```

Se existen, son copiados directamente ao directorio de saída.

---

## Recuperación mediante fraglist

Nalgúns cálculos AMK modifica internamente os nomes dos fragmentos optimizados.

Nestes casos o script consulta:

```text
CALC/working/fraglist
```

para reconstruír a correspondencia correcta entre os nomes esperados e os realmente xerados.

Esta funcionalidade permite recuperar automaticamente ficheiros que doutro xeito quedarían sen identificar.

---

## Xestión de erros

A función incorpora bloques `try/except` para detectar situacións nas que:

* un fragmento non foi calculado;
* un ficheiro non existe;
* AMK modificou a nomenclatura interna.

Nestes casos o programa tenta resolver o problema consultando a información de `fraglist`.

---

# Saída final

Ao rematar a execución obtense un directorio:

```text
OUTPUT/
```

que contén todos os ficheiros relevantes da rede de reacción cunha nomenclatura homoxénea.

Exemplo:

```text
OUTPUT/
├── MIN1.out
├── MIN2.out
├── MIN3.out
├── TS1.out
├── TS2.out
├── TS3.out
├── 001_SP.out
├── 002_SP.out
├── PR12_a.out
└── PR12_b.out
```

Esta organización simplifica significativamente a inspección manual dos resultados, a realización de análises posteriores e o desenvolvemento doutros scripts automatizados para o tratamento da información xerada por AMK.

---

# Resumo

O script automatiza a recompilación e estandarización dos ficheiros de saída producidos por AMK mediante:

* lectura das bases de datos SQLite do cálculo;
* identificación das correspondencias entre estruturas e ficheiros orixinais;
* renomeado de mínimos, estados de transición e produtos;
* recuperación automática de fragmentos optimizados;
* creación dun directorio único de saída con todos os resultados organizados.

Deste xeito elimínase a necesidade de localizar e renomear manualmente centos ou miles de ficheiros xerados durante a exploración automática dunha rede de reacción complexa.
