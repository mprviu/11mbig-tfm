#!/usr/bin/env python3

import os, string

# Campos comunes a los tres datasets de entrada (día, semana y mes).
# 0   id_estacion  object
# 1   fecha        datetime64[ns]
# 2   fecha_cnt    int64
# 3   tmax         float64
# 4   tmin         float64
# 5   precip       float64
# 6   nevada       float64
# 7   prof_nieve   float64
# 8   longitud     float64
# 9   latitud      float64
# 10  altitud      float64
FEATURES = [
    ["fecha_cnt", "tmax", "tmin", "precip", "nevada", "prof_nieve", "longitud", "latitud", "altitud"],
    ["fecha_cnt", "tmax", "tmin", "precip", "longitud", "latitud", "altitud"],
    ["fecha_cnt", "tmax", "tmin", "longitud", "latitud", "altitud"],
    ["fecha_cnt", "precip", "longitud", "latitud", "altitud"],
    ["tmax", "tmin", "precip", "nevada", "prof_nieve", "longitud", "latitud", "altitud"],
    ["tmax", "tmin", "precip", "longitud", "latitud", "altitud"],
    ["tmax", "tmin", "longitud", "latitud", "altitud"],
    ["precip", "longitud", "latitud", "altitud"],
    ["fecha_cnt", "tmax", "tmin", "precip", "nevada", "prof_nieve"],
    ["fecha_cnt", "tmax", "tmin", "precip"],
    ["fecha_cnt", "tmax", "tmin"],
    ["fecha_cnt", "precip"],
    ["tmax", "tmin", "precip", "nevada", "prof_nieve"],
    ["tmax", "tmin", "precip"],
    ["tmax", "tmin"],
    ["precip"],
]
GRIDS = [ 5, 10, 25, 50 ]
ITERATIONS = [ 1000, 10000 ]
OFFSETS = [ "dia", "semana", "mes" ]

TEMPLATE_MAIN = """---
title: "$TITLE"
output: html_notebook
---

```{r}
source("../lib/som-utils.R")
```

# Carga del dataset de entrada.

```{r}
df <- mpr.load_data("datos_$OFFSET.csv.xz")
```

```{r}
df
```

```{r}
summary(df)
```

# Construcción modelos
"""

TEMPLATE_SCALE_FEATURES = """
## Features: $FEATURES

```{r}
Z <- mpr.scale_features(df, $FEATURES)
summary(Z)
```

"""

TEMPLATE_GENERATE_SOM = """
model <- mpr.create_som(Z, $XDIM, $YDIM, $ITERATIONS, "$MODEL_FILENAME")
if (!is.null(model)) { plot(model, type="changes") }
"""

model_id = 1

def generateNotebook(outputFilename, offset, f_models):
    global model_id
    f = open(outputFilename, "w")
    try:

        # Carga de los templates.
        tpl_main = string.Template(TEMPLATE_MAIN)
        tpl_features = string.Template(TEMPLATE_SCALE_FEATURES)
        tpl_generate_som = string.Template(TEMPLATE_GENERATE_SOM)

        # Cuerpo principal del notebook.
        f.write(tpl_main.substitute({
            "TITLE": "Construcción de modelos SOM - Frecuencia datos de entrada: {}".format(offset),
            "OFFSET": offset
        }))

        # Features
        for features in FEATURES:
            features_str = ", ".join(features)
            f.write(tpl_features.substitute({
                "FEATURES": features_str
            }))

            f.write("```{r}")

            # Tamaño del mapa.
            for grid in GRIDS:

                # Iteraciones.
                for iterations in ITERATIONS:
                    f.write(tpl_generate_som.substitute({
                        "XDIM": grid,
                        "YDIM": grid,
                        "ITERATIONS": iterations,
                        "MODEL_FILENAME": "som-{:03d}.rds.xz".format(model_id),
                    }))

                    f_models.write('{};"{}";"{}";"{}";"{}";{};"{}"\n'.format(
                        model_id, "", offset, features_str, "{},{}".format(grid, grid), iterations, ""))
                    model_id += 1

            f.write("```\n")

    finally:
        f.close()

def main():
    f_models = open("../../models/models.csv", "w")
    try:
        f_models.write("id;description;frequency;features;grid;iterations;params\n")
        notebook_idx = 101
        for offset in OFFSETS:
            generateNotebook("../../notebooks/som-models/{}-mpr-som-{}.Rmd".format(notebook_idx, offset), offset, f_models)
            notebook_idx += 1
    finally:
        f_models.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(ex)
