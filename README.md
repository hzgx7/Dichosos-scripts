# Dichosos-scripts
Repositorio de GitHub donde se gardarán os scripts máis importantes empregados no TFG titulado Estudio teórico da pirólise do benceno
README – grafo.py
Xeración automática de mecanismos para Pilgrim a partir de redes de reacción AMK
Descrición xeral

Este script foi desenvolvido para identificar automaticamente os camiños reaccionais máis relevantes dentro dunha rede de reacción xerada por AutoMeKin (AMK) e preparar os ficheiros necesarios para a súa posterior utilización en Pilgrim.

A partir da información contida nos ficheiros de conectividade da rede (RXNet.cg e RXNet.barrless) e dos ficheiros enerxéticos xerados previamente (MINinfo_zpecorr, TSinfo_zpecorr e PRODinfo_zpecorr), o programa constrúe un grafo de reaccións, localiza os camiños accesibles desde un mínimo inicial definido polo usuario e aplica filtros estruturais e enerxéticos para seleccionar unicamente aqueles que presentan interese cinético.

Como resultado, o script:

identifica todos os camiños válidos entre o reactivo inicial e os produtos;
elimina rutas redundantes;
selecciona os estados de transición máis favorables cando existen varias conexións entre dúas especies;
xera automaticamente o ficheiro pif.chem empregado por Pilgrim;
recompila todas as estruturas necesarias para os cálculos cinéticos posteriores.
Fundamento metodolóxico

As redes xeradas por AMK poden conter centos ou miles de especies químicas conectadas mediante múltiples estados de transición. Non todas estas conexións resultan relevantes desde o punto de vista cinético.

O programa aplica dous criterios principais para reducir a complexidade da rede:

Filtro estrutural

Limita o número máximo de mínimos intermedios permitidos entre o reactivo inicial e o produto final.

Este criterio está controlado pola variable:

max_length

e permite descartar rutas excesivamente longas que dificilmente contribuirán de forma significativa á cinética global.

Filtro enerxético

Impón unha enerxía máxima permitida para todas as especies e estados de transición pertencentes a unha ruta.

Este criterio está definido por:

E_cutoff

e garante que só se consideren rutas cun custo enerxético compatible coas condicións estudadas.

Lectura da rede de reacción

O programa analiza automaticamente os ficheiros:

RXNet.cg
RXNet.barrless

O primeiro contén as reaccións convencionais con estado de transición explícito, mentres que o segundo describe procesos considerados sen barreira.

Para cada conexión extráense:

reactivo;
estado de transición;
produto;
tipo de reacción (con ou sen barreira).

No caso das reaccións sen barreira, o programa asigna identificadores artificiais a partir dun desprazamento numérico configurable para evitar conflitos cos estados de transición reais.

Procura automática de camiños

A procura das rutas reacciónais realízase mediante un algoritmo de busca en profundidade (Depth First Search, DFS).

Partindo dun mínimo inicial definido polo usuario, o programa:

explora todas as conexións posibles;
evita ciclos e repeticións;
identifica os produtos alcanzables;
verifica o cumprimento dos criterios enerxéticos;
elimina rutas duplicadas.

O resultado é unha lista de camiños reacciónais válidos entre o reactivo inicial e os produtos finais.

Selección do camiño máis favorable

Para cada ruta calcúlase a enerxía máxima alcanzada ao longo do camiño, considerando tanto mínimos como estados de transición.

Esta magnitude representa o denominado "pescozo de botella" enerxético da ruta.

Posteriormente identifícanse automaticamente os camiños que presentan o menor valor desta enerxía máxima, xa que constitúen as rutas potencialmente máis importantes desde o punto de vista cinético.

Xeración automática de pif.chem

Unha vez identificadas as rutas válidas, o programa crea automaticamente o ficheiro:

chem_C6H6/pif.chem

Este ficheiro constitúe a entrada principal de Pilgrim para a definición do mecanismo cinético.

As reaccións con barreira numéranse secuencialmente:

1 : MIN1 --> TS4 --> MIN13
2 : MIN13 --> TS12 --> PR50_a + PR50_b

Mentres que as reaccións sen barreira identifícanse mediante letras:

a : MIN13 --> TS_dummy_a --> PR14_a + PR14_b

Isto permite diferenciar claramente ambos tipos de procesos durante a preparación dos cálculos cinéticos.

Recompilación de estruturas

Ademais da xeración do mecanismo, o programa copia automaticamente todas as estruturas necesarias ao directorio:

UDATA/

Inclúense:

mínimos;
estados de transición;
produtos;
fragmentos moleculares asociados aos produtos disociativos.

Esta funcionalidade garante que Pilgrim dispoña de todos os ficheiros necesarios para os cálculos posteriores.

Ficheiros de entrada

O programa require:

RXNet.cg
RXNet.barrless
MINinfo_zpecorr
TSinfo_zpecorr
PRODinfo_zpecorr
Directorio OUTPUT cos ficheiros estruturais previamente xerados
Ficheiros xerados

Ao finalizar a execución créanse:

chem_C6H6/pif.chem
Directorio UDATA coas estruturas necesarias para Pilgrim
Resumo
Este script automatiza a extracción das rutas reacciónais máis relevantes dunha rede AMK, aplicando filtros estruturais e enerxéticos para reducir a complexidade do mecanismo. Ademais, xera automaticamente os ficheiros necesarios para Pilgrim e recompila todas as estruturas químicas implicadas nas rutas seleccionadas, simplificando considerablemente a preparación de cálculos cinéticos complexos.

README –VTST3.PY
Análise VTST de scans de reacción e cálculo de constantes cinéticas dependentes da temperatura
Descrición xeral

Este script foi desenvolvido para analizar os resultados dun scan de coordenada de reacción obtido mediante cálculos de química cuántica e calcular propiedades termodinámicas e cinéticas empregando a Teoría do Estado de Transición Variacional (VTST).

O programa procesa automaticamente unha serie de ficheiros Gaussian correspondentes aos distintos puntos do scan e calcula:

enerxías libres de Gibbs;
perfís de ΔG ao longo da coordenada de reacción;
constantes cinéticas dependentes da temperatura;
posición do máximo de enerxía libre;
evolución da barreira variacional.

Os resultados almacénanse nun ficheiro Excel que inclúe táboas numéricas e representacións gráficas xeradas automaticamente.

Fundamento teórico

A VTST constitúe unha extensión da Teoría do Estado de Transición convencional.

Mentres que a teoría clásica asume que o estado de transición coincide cun punto estacionario da superficie de enerxía potencial, a VTST determina a posición efectiva da superficie divisoria minimizando a taxa de recrossing.

Isto permite describir de forma máis realista reaccións nas que:

non existe un estado de transición ben definido;
a barreira é moi plana;
a coordenada de reacción experimenta importantes efectos entrópicos.
Procesamento dos puntos do scan

O programa analiza automaticamente todos os ficheiros:

freq_*.out

presentes no directorio definido polo usuario.

Para cada punto:

comproba que o cálculo Gaussian rematou correctamente;
extrae a xeometría molecular;
obtén as frecuencias vibracionais;
calcula as funcións de partición;
determina a enerxía libre de Gibbs;
calcula a constante cinética correspondente.
Corrección manual de frecuencias baixas

As frecuencias moi baixas poden producir contribucións entrópicas excesivas e introducir erros significativos nos cálculos termodinámicos.

Por este motivo o script incorpora un procedemento opcional que substitúe automaticamente a frecuencia máis baixa por un valor definido polo usuario a partir dun punto determinado do scan.

Esta funcionalidade resulta especialmente útil cando aparecen modos brandos asociados á separación progresiva de fragmentos moleculares.

Selección manual dos puntos

O usuario pode controlar explicitamente que puntos do scan serán procesados mediante:

selección dun rango específico;
exclusión individual de puntos concretos.

Isto permite eliminar rexións problemáticas ou cálculos non converxidos sen necesidade de modificar os ficheiros orixinais.

Cálculo das enerxías libres

Para cada temperatura considerada calcúlase:

enerxía libre do punto do scan;
enerxía libre do reactivo de referencia;
diferenza de enerxía libre ΔG.

Estas magnitudes empréganse posteriormente para obter as constantes cinéticas segundo a formulación VTST implementada en Pilgrim.

Cálculo das constantes cinéticas

As constantes cinéticas determínanse para cada temperatura empregando as funcións internas de Pilgrim.

O resultado é unha serie de valores k(T) que describen a evolución da velocidade da reacción ao longo da coordenada de reacción e permiten localizar a superficie divisoria variacional óptima.

Xeración automática de Excel

Todos os resultados almacénanse nun ficheiro Excel.

Para cada temperatura inclúense:

número do punto do scan;
distancia internuclear monitorizada;
enerxía libre do reactivo;
enerxía libre do punto do scan;
ΔG;
constante cinética.

Ademais, créase automaticamente unha gráfica de:

ΔG fronte á distancia internuclear

permitindo visualizar rapidamente a evolución da barreira libre ao longo da coordenada de reacción.

Ficheiros de entrada

O programa require:

serie de ficheiros Gaussian freq_*.out;
biblioteca Pilgrim instalada;
módulos auxiliares empregados por Pilgrim;
lista de temperaturas;
enerxías libres de referencia do reactivo.
Ficheiros xerados

Ao finalizar a execución obtense:

vtst_scan_*.xlsx

que contén todas as táboas e gráficas xeradas durante a análise.

Resumo

Este script automatiza a análise VTST de scans de reacción obtidos mediante cálculos de química cuántica. A partir dos ficheiros Gaussian calcula funcións de partición, enerxías libres de Gibbs e constantes cinéticas para múltiples temperaturas, permitindo localizar a barreira variacional efectiva e obter unha descrición cinética máis rigorosa do proceso estudado. Os resultados preséntanse automaticamente nun ficheiro Excel preparado para a súa análise e interpretación posterior.
