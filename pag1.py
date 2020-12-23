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
import shapefile #pip install pyshp#
#fondamentali
import shapely.speedups
shapely.speedups.enable()

############# from shapefile to dataframe pandas #################
def read_shapefile(shp_path):
	"""
	Read a shapefile into a Pandas dataframe with a 'coords' column holding
	the geometry information. This uses the pyshp package
	"""
	#read file, parse out the records and shapes
	sf = shapefile.Reader(shp_path)
	fields = [x[0] for x in sf.fields][1:]
	records = [list(i) for i in sf.records()]
	shps = [s.points for s in sf.shapes()]
	#write into a dataframe
	df = pd.DataFrame(columns=fields, data=records)
	df = df.assign(coords=shps)
	return df
##############################################################################################
# Landslide Risk (Vectorised)
landslide_shp = gpd.read_file('Flood_and_Landslide_Datasets/geonode_class3_elev.shp')
landslide_json = 'Flood_and_Landslide_Datasets/geonode_class3_elev1.geojson'

# Flood Risk (Vectorised)
flood_shp = gpd.read_file('Flood_and_Landslide_Datasets/geonode_flood_hazard_map_vector.shp')
flood_gj = geojson.load(open('Flood_and_Landslide_Datasets/geonode_flood_hazard_map_vector.geojson')) # Import geojson file # https://stackoverflow.com/questions/42753745/how-can-i-parse-geojson-with-python

##DF
#df = pd.DataFrame(np.random.randint(0,100,size=(100, 4)), columns=list('ABCD'))
# import datetime
# todays_date = datetime.datetime.now().date()
# index = pd.date_range(todays_date-datetime.timedelta(1), periods=1, freq='d')
# columns=['latitude','longitude','Risk_Landslide','Risk_Flood']
# #df = pd.DataFrame(index=index, columns=columns)

def main():
	colors = ['#2b83ba', '#abdda4', '#ffffbf', '#fdae61', '#d7191c'] # these have been assigned to each FloodRisk category in the GeoJSON file on QGIS!!!
	m = folium.Map(location=[15.4275, -61.3408], zoom_start=11) # center of island overview
	
	# Show Landslide GeoJSON to the map
	folium.GeoJson(
	landslide_json,
	name='Landslide',
		style_function=lambda feature: {
		# 'fillColor': feature['properties']['Color'],
		# 'color' : feature['properties']['Color'],
		'weight' : 1,
		'fillOpacity' : 0.3,
		}
	).add_to(m)

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

	# Setup colormap MUST USE SAME COLORS AS QGIS GEOJSON FILE!!!!
	levels = len(colors)
	cmap = branca.colormap.LinearColormap(colors, vmin=0, vmax=4).to_step(levels-1)
	cmap.add_to(m)

	# Enable lat-long Popup; LayerControl; Call to render Folium map in Streamlit
	m.add_child(folium.ClickForMarker(popup='Waypoint (Double-click to remove it)')) # and click-for-marker functionality (dynamic)
	m.add_child(folium.LatLngPopup()) # It's not possible to save lat long automatically from clicking on it :-( . # https://github.com/python-visualization/folium/issues/520
	folium.LayerControl().add_to(m)
	folium_static(m)
	st.write('This map uses coordinate format WGS84-EPGS4326')
	#-------------------
	# col = ['c1', 'c2', 'c3','c4']
	# df = pd.DataFrame(columns=col)
	# lst_dict=[]

	######## Dictionary Landslide-Flood-Risk
	dict_Landslide = {0:'Low-Risk',1:'Moderate-Risk',2:'High-Risk'}
	dict_Flood = {0:'No-Risk',1:'Low-Risk',2:'Moderate-Risk',3:'High-Risk',4:'Very High-Risk'}
# Text labels to enter the lat & long coordinates once you read them on the map
	lat_long = st.text_input('Insert Latitude,Longitude (without spaces) format WGS84-EPGS4326 (DD.dddd) for example: 15.2533,-61.3164',max_chars=16)
	if lat_long != '': 
		latitude = float(lat_long.split(',')[0])
		longitude = float(lat_long.split(',')[1])

	if st.button('Analyse Lat & Long'): # this is if you want to add a button to launch the analysis (without this, it does automatically when there's lat & long values in the cell)
		st.header('Extracting Results for the location selected:\n(Lat: ' + str(latitude) +' & Long: ' + str(longitude) + ')')
		coordinate = shapely.geometry.Point((longitude,latitude,))
		# Printing a list of the coords to ensure iterable 
		#list(coordinate.coords)
		
		######## First loop for Landslide		
		landslide_code='NAN'
		for i in landslide_shp.loc[:,'geometry']:
			p = Point(longitude,latitude)
			if p.within(i):
				polig_landslide = landslide_shp[landslide_shp.geometry.intersects(coordinate)].values[0][0]
				landslide_code =polig_landslide-1
				if landslide_code <=2:
					for key,value in dict_Landslide.items():
						if key == landslide_code:
							landslide_str=value
					print(landslide_code)
					st.markdown('**-Landslide Risk: **'+ str(landslide_code)+' ---> '+landslide_str)
					#st.write('wait for Flood Risk Analysis... ')
				else:
					###seems doesn't work!
					landslide_code = 'Outside Risk Zone'
					print(landslide_code)
					st.markdown('**-Landslide Risk: **'+ str(landslide_code))
					new_risk = 'Outside Flood Risk Zone'
					print(new_risk)
					st.markdown('**-Flood risk: **' + str(new_risk))
					url1 = 'tablerisk.png'
					image1 = Image.open(url1)
					st.image(image1, caption='',use_column_width=True)
					break
		
		######## Second loop for flood risk
		frisk_code = 'NAN'
		new_risk = 'NAN'
		for i in flood_shp.loc[:,'geometry']:
			p = Point(longitude,latitude)
			if p.within(i):	
				frisk_code = flood_shp[flood_shp.geometry.intersects(coordinate)].values[0][0]
				new_risk = frisk_code-1
				if new_risk <=4:
					for key,value in dict_Flood.items():
						if key == new_risk:
							flood_str=value
					st.markdown('**-Flood risk: **' + str(new_risk)+'---> '+flood_str)
					print(new_risk)
					url1 = 'tablerisk.png'
					image1 = Image.open(url1)
					#st.markdown(get_table_download_link(df), unsafe_allow_html=True)
					st.image(image1, caption='',width=350)
					break 

	## TEST ##
	## flood risk ==4 Landl ==1 #15.3393,-61.2603
	## flood risk ==0 Landl ==2 15.5310,-61.4623
	## flood risk ==0 Landl ==1 #15.3451,-61.3588
	## outside flood and risk # 15.4265,-61.2447
if __name__ == "__main__":
	main()


