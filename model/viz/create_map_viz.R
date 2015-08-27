#Install all dependecies
install.packages(c("ggplot2", "ggmap", "rgdal"))
library(ggplot2)
library(ggmap)
library(rgdal)

#Load CSV file uag_join_aug_plat_pst_cat.csv 
#hence, userid-age-gender-table join augmented-photoid-lat-lng-userid-
#action-time-table in PST time and age in category bucket
df <- read.csv("path to csv file")

#Get SF map and put into ggmap
sf <- get_map("San Francisco, CA,", zoom=12, source='osm')
p <- ggmap(sf)

#Get SF neighborhoods outline 
sf_d <- readOGR("path to SF neighborhoods folder", "planning_neighborhoods")
sf_d <- spTransform(sf_d, CRS("+proj=longlat + datum=WGS84"))
sf_d <- fortify(sf_d)

#Create different seasons
spring <- c(3,4,5)
summer <- c(6,7,8)
fall <- c(9,10,11)
winter <- c(12,1,2)

#Define hex map activity points filter
filter <- function(x) {
  if (length(x) > 20) {
    return(mean(x))
  } else {
    return(NA)
  }
}

#Example 1: create gender map for the full time period
p + stat_summary_hex(data=df, aes(x=lng, y=lat, z=as.numeric(gender_bucket=="Male")), 
                     bins=50, alpha=0.95, fun=filter) + 
  geom_polygon(aes(x=long, y=lat, group=group), fill='grey', size=.2,color='white', data=sf_d,
               alpha=0) + 
  scale_fill_gradientn(values=c(1, .6, .5, .4, 0), colours=c("#bb7f7f", "#770000", "white",
                                                             "#007777", "#7FBBBB"))

#Example 2: create gender map for spring period
p + stat_summary_hex(data=df[df$month %in% spring,], aes(x=lng, y=lat, z=as.numeric(gender_bucket=="Male")), 
                     bins=50, alpha=0.95, fun=filter) + 
  geom_polygon(aes(x=long, y=lat, group=group), fill='grey', size=.2,color='white', data=sf_d,
               alpha=0) + 
  scale_fill_gradientn(values=c(1, .6, .5, .4, 0), colours=c("#bb7f7f", "#770000", "white",
                                                             "#007777", "#7FBBBB"))