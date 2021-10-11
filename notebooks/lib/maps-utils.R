
library(dplyr)
library(ggplot2)
library(rnaturalearth)
library(sf)
library(cowplot)

mpr.group_by_geo <- function(df) {
  return(df %>% group_by(longitud, latitud) %>% summarise(n = n(), .groups = "keep"))
}

mpr.draw_map <- function(spain, df) {
  peninsula <- ggplot(data = spain) +
    geom_sf(fill = "cornsilk") + 
    coord_sf(xlim = c(-10.00, 5.00), ylim = c(44.00, 36.00), expand = T, datum = NA) +
    labs(x = "", y = "") +
    theme_bw() +
    geom_point(data = df, aes(x = latitud, y = longitud), size = 1, shape = 21, fill = "red")

  canarias <- ggplot(data = spain) +
    geom_sf(fill = "cornsilk") + 
    coord_sf(xlim = c(-18.1, -13.5), ylim = c(29.3, 27.5), expand = T, datum = NA) +
    labs(x = "", y = "") +
    theme_void() + theme(panel.border = element_rect(colour = "grey", fill = NA)) +
    geom_point(data = df, aes(x = latitud, y = longitud), size = 1, shape = 21, fill = "red")

  ratioCanarias <- (23 - 18) / (-154 - (-161))

  ggdraw(peninsula) +
    draw_plot(canarias, width = 0.26, height = 0.26 * 10/6 * ratioCanarias, x = 0.65, y = 0.02)
}

