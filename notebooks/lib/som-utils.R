
library(kohonen)
library(dplyr)

mpr.data_base_path <- "../../data/processed/nooa/spain";
mpr.models_base_path <- "../../models";

mpr.set_base_path_analysis <- function() {
  mpr.data_base_path <<- paste("..", mpr.data_base_path, sep = "/");
  mpr.models_base_path <<- paste("..", mpr.models_base_path, sep = "/");
}

# Carga de disco los datos.
mpr.load_data <- function(filename) {
  full_path <- paste(mpr.data_base_path, filename, sep = "/");
  df <- read.csv(full_path, sep = ";")
  return(df);
}

# Selecciona variables a usar del dataframe y las escala.
mpr.scale_features <- function(.df, ...) {
  df_features <- select(df, ...)
  set.seed(4273)
  Z <- scale(df_features, center=T, scale=T)
  return(Z)
}

# Genera el modelo SOM y lo almacena en disco.
mpr.create_som <- function(.Z, xdim, ydim, rlen, filename) {
  model <- tryCatch({
    # Genera modelo.
    grid <- somgrid(xdim = xdim, ydim = ydim, topo = "hexagonal");
    model <- som(Z, grid = grid, rlen = rlen);

    # Guarda el modelo en disco.
    full_path <- paste(mpr.models_base_path, filename, sep = "/");
    saveRDS(model, full_path, compress = "xz");

    return(model);
  },
  error = function(err) {
    print(paste("**ERROR** [mpr.create_som]: ", err));
    NULL;
  });
}

# Carga del modelo desde disco.
mpr.load_model <- function(filename) {
  full_path <- paste(mpr.models_base_path, filename, sep = "/");
  return(readRDS(full_path))  
}

# Mapa de densidad con tonos azules
mpr.degrade.bleu <- function(n){
  return(rgb(0,0.4,1,alpha=seq(0,1,1/n)))
}

# Mapa de densidad de colores de azul a rojo
mpr.coolBlueHotRed <- function(n, alpha = 1) {
  rainbow(n, end=4/6, alpha=alpha)[n:1]}

# Correlación en función de coordenadas (x,y) del mapa
# v: variable (primera columna), w: weight, som: Mapa de Kohonen
mpr.weighted.correlation <- function(v, w, som) {
  x <- som$grid$pts[,"x"]
  y <- som$grid$pts[,"y"]
  mx <- weighted.mean(x,w)
  my <- weighted.mean(y,w)
  mv <- weighted.mean(v,w)
  numx <- sum(w*(x-mx)*(v-mv))
  denomx <- sqrt(sum(w*(x-mx)^2))*sqrt(sum(w*(v-mv)^2))
  numy <- sum(w*(y-my)*(v-mv))
  denomy <- sqrt(sum(w*(y-my)^2))*sqrt(sum(w*(v-mv)^2))
  #correlation for the two axes
  res <- c(numx/denomx,numy/denomy)
  return(res)
}

mpr.hac <- function(som, nb) {
  # Matriz de distancia entre nodos
  dc <- dist(getCodes(som,1))
  # HAC
  return(hclust(dc, method="ward.D2", members=nb))
}

mpr.hist <- function(df) {
  par(mfrow=c(3,3))
  for (col in 1:ncol(df)) {
    hist(df[,col], main = names(df)[col], xlab = "", col = "lightblue")
  }
}

mpr.boxplot <- function(df) {
  par(mfrow=c(2,5))
  for (col in 1:ncol(df)) {
    boxplot(df[,col], main = names(df)[col], xlab = "", col = "lightgreen")
  }
}
