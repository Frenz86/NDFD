import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import requests
from io import BytesIO
import folium
from streamlit_folium import folium_static

def main():
	m = folium.Map(location=[27.783889, -97.510556],zoom_start=12)
	folium_static(m)

if __name__ == "__main__":
	main()