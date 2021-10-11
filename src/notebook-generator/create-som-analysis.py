#!/usr/bin/env python3

import os, sys, string, csv, stat

CLUSTERS = [3, 4, 5, 6, 8, 10]

# Templates {{{
# Main {{{
TEMPLATE_MAIN = """---
title: "$TITLE"
output: html_notebook
---

# Modelo

* ID: $MODEL_ID
* Descripción: $MODEL_DESCRIPTION
* Frecuencia: $MODEL_FREQUENCY
* Variables: $MODEL_FEATURES
* Dimensiones del mapa: $MODEL_GRID
* Iteraciones: $MODEL_ITERATIONS
* Parámetros adicionales: $MODEL_PARAMS

```{r}
source("../../lib/som-utils.R")
source("../../lib/maps-utils.R")
```

# Carga del modelo desde disco

```{r}
mpr.set_base_path_analysis()
model <- mpr.load_model("$MODEL_FILENAME")
summary(model)
```

```{r}
plot(model, type="changes")
```

# Carga del dataset de entrada

```{r}
df <- mpr.load_data("datos_$OFFSET.csv.xz")
```

```{r}
df
```

```{r}
summary(df)
```

# Carga de los mapas

```{r}
world <- ne_countries(scale = "medium", returnclass = "sf")
spain <- subset(world, admin == "Spain")
```
"""
# }}}
# Plot maps {{{
TEMPLATE_PLOT_MAPS = """
# Mapa de densidad

```{r}
plot(model, type="count", shape = "straight", palette.name = mpr.degrade.bleu)
```

Número de elementos en cada celda:

```{r}
nb <- table(model$$unit.classif)
print(nb)
```
Comprobación de nodos vacíos:

```{r}
dim_model <- $MODEL_XDIM*$MODEL_YDIM;
len_nb = length(nb);
empty_nodes <- dim_model != len_nb;
if (empty_nodes) {
  print(paste("[Warning] Existen nodos vacíos: ", len_nb, "/", dim_model))
}
```

# Mapa de distancia entre vecinos

```{r}
plot(model, type="dist.neighbours", shape = "straight")
```
"""

# }}}
# Variables {{{
TEMPLATE_VARIABLES = """
# Influencia de las variables

```{r}
model_colnames = c($MODEL_FEATURES)
model_ncol = length(model_colnames)
```

## Mapa de variables.

```{r}
plot(model, shape = "straight")
```

## Mapa de calor por variable

```{r}
par(mfrow=c(3,4))
for (j in 1:model_ncol) {
  plot(model, type="property", property=getCodes(model,1)[,j],
    palette.name=mpr.coolBlueHotRed,
    main=model_colnames[j],
    cex=0.5, shape = "straight")
}
```

## Correlación para cada columna del vector de nodos

```{r}
if (!empty_nodes) {
  cor <- apply(getCodes(model,1), 2, mpr.weighted.correlation, w=nb, som=model)
  print(cor)
}
```

Representación de cada variable en un mapa de factores:

```{r}
if (!empty_nodes) {
  par(mfrow=c(1,1))
  plot(cor[1,], cor[2,], xlim=c(-1,1), ylim=c(-1,1), type="n")
  lines(c(-1,1),c(0,0))
  lines(c(0,0),c(-1,1))
  text(cor[1,], cor[2,], labels=model_colnames, cex=0.75)
  symbols(0,0,circles=1,inches=F,add=T)
}
```

Importancia de cada variable - varianza ponderada por el tamaño de la celda:

```{r}
if (!empty_nodes) {
  sigma2 <- sqrt(apply(getCodes(model,1),2,function(x,effectif)
     {m<-sum(effectif*(x-weighted.mean(x,effectif))^2)/(sum(effectif)-1)},
     effectif=nb))
  print(sort(sigma2,decreasing=T))
}
```
"""

# }}}
# Clustering {{{
TEMPLATE_CLUSTERING = """
# Clustering

```{r}
if (!empty_nodes) {
  hac <- mpr.hac(model, nb)
}
```
"""

#}}}
# Cluster {{{
TEMPLATE_CLUSTER = """
## Visualización de $CLUSTERS clústeres:

```{r}
if (!empty_nodes) {
  plot(hac, hang=-1, labels=F)
  rect.hclust(hac, k=$CLUSTERS)
}
```

### Visualización de los clústers en el mapa

A qué clúster pertenece cada nodo del mapa de kohonen:

```{r}
if (!empty_nodes) {
  groups <- cutree(hac, k=$CLUSTERS)
  plot(model, type="mapping",
    bgcol=c("steelblue1","sienna1","yellowgreen","red","blue","yellow","purple","green","white","#1f77b4", '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2')[groups],
    shape = "straight", labels = "")
  add.cluster.boundaries(model, clustering=groups)
}
```

### Análisis de las observaciones de cada cluster

```{r}
if (!empty_nodes) {
  # Asignamos a cada registro su clúster
  df$$cluster <- groups[model$$unit.classif]
}
```

Nuevos dataframes por cluster

```{r}
if (!empty_nodes) {
  # Creo nuevos dataframes, uno por cada clúster.
$CLUSTER_SUBSET

  # Extraigo del dataframe las features.
$CLUSTER_SELECT_FEATURES
}
```

```{r}
$CLUSTER_SUMMARY
```

#### Número de elementos en cada clúster

```{r}
if (!empty_nodes) {
  df.clusters.dim <- c($CLUSTER_DIM)
  barplot(df.clusters.dim,
          names.arg = c($CLUSTER_BARPLOT),
          col = "steelblue1")
}
```

#### Distribución de los datos

```{r fig.height=7}
$CLUSTER_HISTOGRAMS
```

```{r fig.height=5}
$CLUSTER_BOXPLOT
```

### Localización geográfica de las estaciones de medida de cada cluster

```{r}
# Agrupa por longitud y latitud para rellenar el mapa con menos datos.
if (!empty_nodes) {
$CLUSTER_GROUPED
}
```

```{r}
$CLUSTER_MAPS
```
"""

#}}}
#}}}

def generateNotebook(outputFilename, model, csvFile):
    with open(outputFilename, "w") as f:

        # Carga de los templates.
        tpl_main = string.Template(TEMPLATE_MAIN)
        tpl_plot_maps = string.Template(TEMPLATE_PLOT_MAPS)
        tpl_variables = string.Template(TEMPLATE_VARIABLES)
        tpl_clustering = string.Template(TEMPLATE_CLUSTERING)
        tpl_cluster = string.Template(TEMPLATE_CLUSTER)

        # Cuerpo principal del notebook.
        f.write(tpl_main.substitute({
            "TITLE": "Análisis de modelos SOM - Frecuencia datos de entrada: {}".format(model["frequency"]),
            "OFFSET": csvFile,
            "MODEL_FILENAME": "som-{:03d}.rds.xz".format(model["id"]),
            "MODEL_ID": model["id"],
            "MODEL_DESCRIPTION": model["description"],
            "MODEL_FREQUENCY": model["frequency"],
            "MODEL_FEATURES": model["features"],
            "MODEL_GRID": model["grid"],
            "MODEL_ITERATIONS": model["iterations"],
            "MODEL_PARAMS": model["params"]
        }))

        # Mapas
        dims = model["grid"].split(",")
        f.write(tpl_plot_maps.substitute({
            "MODEL_XDIM": dims[0],
            "MODEL_YDIM": dims[1] 
        }))

        # Variables
        features = ", ".join([ '"{}"'.format(feature) for feature in model["features"].split(", ")])
        f.write(tpl_variables.substitute({
            "MODEL_FEATURES": features
        }))

        # Features a analizar en cada cluster.
        select_features = "fecha_cnt, tmax, tmin, precip, nevada, prof_nieve, longitud, latitud, altitud"

        # Clustering
        f.write(tpl_clustering.substitute({}))
        for clusters in CLUSTERS:
            subset  = "\n".join(
                ["  df.cluster{:02d} <- subset(df, cluster=={})".format(cluster, cluster) for cluster in range(1, clusters+1)]
            )
            select  = "\n".join(
                ["  df.cluster{:02d} <- select(df.cluster{:02d}, {})".format(cluster, cluster, select_features) for cluster in range(1, clusters+1)]
            )
            summary = "\n".join(
                ["if (!empty_nodes) summary(df.cluster{:02d})".format(cluster) for cluster in range(1, clusters+1)]
            )
            clusters_dim = ", ".join(
                ["dim(df.cluster{:02d})[1]".format(cluster) for cluster in range(1, clusters+1)]
            )
            barplot = ", ".join(
                ['"cluster{:02d}"'.format(cluster) for cluster in range(1, clusters+1)]
            )
            histograms = "\n".join(
                ["if (!empty_nodes) mpr.hist(df.cluster{:02d})".format(cluster) for cluster in range(1, clusters+1)]
            )
            boxplot = "\n".join(
                ["if (!empty_nodes) mpr.boxplot(df.cluster{:02d})".format(cluster) for cluster in range(1, clusters+1)]
            )
            grouped = "\n".join(
                ["  df.cluster{:02d}.grouped <- mpr.group_by_geo(df.cluster{:02d})".format(cluster, cluster) for cluster in range(1, clusters+1)]
            )
            maps = "\n".join(
                ["if (!empty_nodes) mpr.draw_map(spain, df.cluster{:02d}.grouped)".format(cluster) for cluster in range(1, clusters+1)]
            )
            f.write(tpl_cluster.substitute({
                "CLUSTERS": clusters,
                "CLUSTER_SUBSET": subset,
                "CLUSTER_SELECT_FEATURES": select,
                "CLUSTER_SUMMARY": summary,
                "CLUSTER_DIM": clusters_dim,
                "CLUSTER_BARPLOT": barplot,
                "CLUSTER_HISTOGRAMS": histograms,
                "CLUSTER_BOXPLOT": boxplot,
                "CLUSTER_GROUPED": grouped,
                "CLUSTER_MAPS": maps
            }))

def load_models(frequency):
    models = {}
    with open("../../models/models.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader, None)
        for row in reader:
            if row[2] == frequency:
                id = int(row[0])
                models[id] = {
                    "id": id,
                    "description": row[1],
                    "frequency": row[2],
                    "features": row[3],
                    "grid": row[4],
                    "iterations": int(row[5]),
                    "params": row[6]
                }
    return models

def create_dir_base(frequency):
    dirname = "../../notebooks/som-analysis/{}".format(frequency)
    if not os.path.exists(dirname):
        os.mkdir(dirname)

def generate_run_script(outputFilename, frequency, models):
    with open(outputFilename, "w") as f:
        f.write("#!/bin/bash\n")
        for i, model in models.items():
            f.write('Rscript -e "rmarkdown::render(\'{}/{:03d}-mpr-som.Rmd\')"\n'.format(frequency, i))
    st = os.stat(outputFilename)
    os.chmod(outputFilename, st.st_mode | stat.S_IEXEC)

def main():
    # Frecuencia (dia, semana, mes)
    # También se puede indicar un dataset filtrado de forma opcional (p.ej: dia_2k)
    if len(sys.argv) > 1 and sys.argv[1] != "":
        frequency = sys.argv[1]
    else:
        frequency = "mes"
    # Dataset de entrada.
    csvFile = frequency
    if frequency.find("_") > -1:
        frequency = frequency.split("_")[0]

    create_dir_base(csvFile)

    models = load_models(frequency)
    for i, model in models.items():
        generateNotebook("../../notebooks/som-analysis/{}/{:03d}-mpr-som.Rmd".format(csvFile, i), model, csvFile)

    generate_run_script("../../notebooks/som-analysis/render_notebook_{}.sh".format(csvFile), csvFile, models)

if __name__ == "__main__":
    main()

# vim: foldmethod=marker
