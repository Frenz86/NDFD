import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import geopandas as gpd
import geojson
from shapely.geometry import Point
import folium
from streamlit_folium import folium_static
import matplotlib, matplotlib.pyplot as plt 
import branca


def main():
	st.write('this map will use coordinate format WGS84/UTMzone19N')
	landslide_shp = gpd.read_file('Flood_and_Landslide_Datasets/landslides_1_4326.shp')
	landslide_json = 'Flood_and_Landslide_Datasets/landslides_1_4326.geojson'
	# Flood Risk (Vectorised)
	flood_shp = gpd.read_file('Flood_and_Landslide_Datasets/geonode_flood_hazard_map_vector.shp')
	flood_gj = geojson.load(open('Flood_and_Landslide_Datasets/geonode_flood_hazard_map_vector.geojson')) # Import geojson file # https://stackoverflow.com/questions/42753745/how-can-i-parse-geojson-with-python

	colors = ['#2b83ba', '#abdda4', '#ffffbf', '#fdae61', '#d7191c'] # these have been assigned to each FloodRisk category in the GeoJSON file on QGIS!!!
	m = folium.Map(location=[15.4275, -61.3408], zoom_start=11) # center of island overview
	
	## Show risk zones
	folium.GeoJson(
	flood_gj,
	name='Flood Risk',
	style_function=lambda feature: {
		'fillColor': feature['properties']['Color'],
		'color' : feature['properties']['Color'],
		'weight' : 1,
		'fillOpacity' : 0.3,
		}
	).add_to(m)

	# Show Landslide GeoJSON to the map
	folium.GeoJson(
		landslide_json,
		name='Landslide'
	).add_to(m)

	# Setup colormap MUST USE SAME COLORS AS QGIS GEOJSON FILE!!!!
	levels = len(colors)
	cmap = branca.colormap.LinearColormap(colors, vmin=0, vmax=4).to_step(levels-1)
	cmap.add_to(m)

	# Enable lat-long Popup; LayerControl; Call to render Folium map in Streamlit
	m.add_child(folium.ClickForMarker(popup='Waypoint (Double-click to remove it)')) # and click-for-marker functionality (dynamic)
	m.add_child(folium.LatLngPopup()) # It's not possible to save lat long automatically from clicking on it :-( . # https://github.com/python-visualization/folium/issues/520
	folium.LayerControl().add_to(m)
	folium_static(m)
	#-------------------
# Text labels to enter the lat & long coordinates once you read them on the map
	lat = st.text_input('Insert Latitude in the format WGS84/UTMzone19N (DD.dddd) for example: 15.2533')
	if lat != '': 
		latitude = float(lat)
	
	longi = st.text_input('Insert Longitude in the format WGS84/UTMzone19N (DD.dddd) for example: -61.3164')
	if longi != '': 
		longitude = float(longi)

	if st.button('Analyse Lat & Long'): # this is if you want to add a button to launch the analysis (without this, it does automatically when there's lat & long values in the cell)
		p = Point(longitude,latitude)
		st.header('Extracting Results for the location selected:\n(Lat: ' + str(latitude) +' & Long: ' + str(longitude) + ')')
		# ======= Get Value from Shapefile
		landslide_code = 'Outside Risk Zone'
		# From a given Point coordinates, quickly/efficiently check if it's contained in any polygons geometry, and print out the LANDSLIDE code of that polygon if so. 
		# this works, but is this teh most efficient way?!? Think it can be improved with lampda / apply / map, without iterating on the whole dataframe?
		for elem in landslide_shp.loc[:,'geometry']:
			if p.within(elem): 
				landslide_code = landslide_shp.loc[landslide_shp.loc[:,'geometry'] == elem]['LANDSLIDES'].values[0]
		st.markdown('**-Landslide Risk: **'+ landslide_code)
		st.write('wait for Flood Risk Analysis... ')

		# ======= Get Value from Raster
		# From a given Point coordinates, quickly/efficiently check if it's contained in any polygons geometry, and print out the LANDSLIDE code of that polygon if so. 
		# this works, but is this teh most efficient way?!? Think it can be improved with lampda / apply / map, without iterating on the whole dataframe?
		frisk_code = 'NAN'
		new_risk = 'NAN'
		for elem in flood_shp.loc[:,'geometry']:
			if p.within(elem): 
				frisk_code = flood_shp.loc[flood_shp.loc[:,'geometry'] == elem]['FloodRisk'].values[0]
				new_risk = frisk_code-1
				print(new_risk)
			if new_risk == 0:
				new_risk = 'No Risk'
		
		## TEST
		## flood risk ==3 #15.2533,-61.3164
		## flood risk ==4 #15.3393,-61.2603
		## flood risk ==0 #15.3451,-61.3588
		##LandslideNO + flood risk ==0 ## 15.3955,-61.2482
		##LandslideNO + flood risk ==0 ## 15.3955,-61.2482

		st.markdown('**-Flood risk: **' + str(new_risk))
		url1 = 'tablerisk.png'
		image1 = Image.open(url1)
		st.image(image1, caption='',use_column_width=True) 

# FloodRisk
# No Risk
# Low Risk (1)
# Moderate Risk (2)
# High Risk (3)
# Very High (4)

#Landslide Risk
# No Risk
# xx Risk (1)


if __name__ == "__main__":
	main()


