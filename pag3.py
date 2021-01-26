import pandas as pd
import streamlit as st
import pyproj
_projections = {}
def zone(coordinates):
	if 56 <= coordinates[1] < 64 and 3 <= coordinates[0] < 12:
		return 32
	if 72 <= coordinates[1] < 84 and 0 <= coordinates[0] < 42:
		if coordinates[0] < 9:
			return 31
		elif coordinates[0] < 21:
			return 33
		elif coordinates[0] < 33:
			return 35
		return 37
	return int((coordinates[0] + 180) / 6) + 1


def letter(coordinates):
	return 'CDEFGHJKLMNPQRSTUVWXX'[int((coordinates[1] + 80) / 8)]

def project(coordinates):
	z = zone(coordinates)
	l = letter(coordinates)
	if z not in _projections:
		_projections[z] = pyproj.Proj(proj='utm', zone=z, ellps='WGS84')
	x, y = _projections[z](coordinates[0], coordinates[1])
	if y < 0:
		y += 10000000
	return z, l, x, y

def unproject(z, l, x, y):
	if z not in _projections:
		_projections[z] = pyproj.Proj(proj='utm', zone=z, ellps='WGS84')
	if l < 'N':
		y -= 10000000
	lng, lat = _projections[z](x, y, inverse=True)
	return (lat,lng)


def main():
	st.title('Conversion WGS84-32619 UTM ZONE19/WGS84-EPSG4326')
	#https://awsm-tools.com/geo/utm-to-geographic
	#unproject(24,'N',510000,7042000)
	## (63.50614385957355, -38.799090003171294)
	st.write("Reference example: 24 N 510000 7042000  -->  63.5061, -38.7991")
	input1 = st.text_input(' Insert the zone number (ex. 24)',max_chars=2)
	if input1 != '': 
		zone = float(input1)
		
	input2 = st.text_input(' Insert zone letter (ex. N)',max_chars=1)
	if input2 != '': 
		letter = str(input2)

	input3 = st.text_input(' Insert the projected latitude x (ex. 510000)',max_chars=10)
	if input3 != '': 
		x = float(input3)

	input4 = st.text_input(' Insert the projected longitude y (ex. 7042000)',max_chars=10)
	if input4 != '': 
		y = float(input4)    

	if st.button('Conver to WGS84-EPSG4326'):
		st.markdown('**Latitude, Longitude**')
		conversion = unproject(zone,letter,x,y)
		Latitude = round(float(conversion[0]),4) #63
		Longitude = round(float(conversion[1]),4)
		st.header(str(Latitude)+','+str(Longitude))
		st.write('Conversion Done!')
		st.write('Copy and Paste WGS84-EPSG4326 coordinate to the Risk Classificator')

if __name__ == "__main__":
	main()