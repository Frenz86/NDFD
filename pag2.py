import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import requests
from io import BytesIO
import folium
from streamlit_folium import folium_static
import geopandas as gpd
import geojson
import shapefile #pip install pyshp

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


def main():
	m = folium.Map(location=[27.783889, -97.510556],zoom_start=12)
	folium_static(m)
	path1='Flood_and_Landslide_Datasets/geonode_flood_hazard_map_vector.shp'
	df = read_shapefile(path1)
	print(df)
	print(df.info)

if __name__ == "__main__":
	main()