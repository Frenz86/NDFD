import pandas as pd
import numpy as np
from pathlib import Path
import sqlite3
from sqlite3 import Connection
import streamlit as st
import pandas as pd

#URI_SQLITE_DB = "test.db"
URI_SQLITE_DB = "test.db"

def init_db(conn: Connection):
	conn.execute(
		"""CREATE TABLE IF NOT EXISTS test
			(INPUT1 INT,INPUT2 INT);"""
	)
	conn.commit()

def display_data(conn: Connection):
	if st.checkbox("Display data in sqlite databse"):
		st.dataframe(get_data(conn))

def get_data(conn: Connection):
	df = pd.read_sql("SELECT * FROM test", con=conn)
	return df


@st.cache(hash_funcs={Connection: id})
def get_connection(path: str):
	"""Put the connection in cache to reuse if path does not change between Streamlit reruns.
	NB : https://stackoverflow.com/questions/48218065/programmingerror-sqlite-objects-created-in-a-thread-can-only-be-used-in-that-sa
	"""
	return sqlite3.connect(path, check_same_thread=False)

############### to export datafram in excel with button #############
import base64
from io import BytesIO
#pip install xlsxwriter
def to_excel(df):
	output = BytesIO()
	writer = pd.ExcelWriter(output, engine='xlsxwriter')
	df.to_excel(writer, index=True, sheet_name='Sheet1') # <--- here
	writer.save()
	processed_data = output.getvalue()
	return processed_data

def get_table_download_link(df):
	"""Generates a link allowing the data in a given panda dataframe to be downloaded
	in:  dataframe
	out: href string
	"""
	val = to_excel(df)
	b64 = base64.b64encode(val)  # val looks like b'...'
	return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="extract.xlsx">Download xlsx file</a>' # decode b'abc' => abc
# df = ... # your dataframe
# st.markdown(get_table_download_link(df), unsafe_allow_html=True)

def save(x,y):
	#### First part DB ##########
	def build_sidebar(conn: Connection):
		if st.sidebar.button("Save to list"):
			conn.execute(f"INSERT INTO test (INPUT1, INPUT2) VALUES ({input1}, {input2})")
			conn.commit()
	conn = get_connection(URI_SQLITE_DB)
	init_db(conn)
	#############################
	input1 = x
	input2 = y

	################## Export to Excel SQLite
	build_sidebar(conn)
	display_data(conn)
	df = get_data(conn)
	#df = pd.DataFrame(np.random.randint(0,100,size=(100, 4)), columns=list('ABCD'))
	download = st.sidebar.button("export result")
	if download:
		df
		st.markdown(get_table_download_link(df), unsafe_allow_html=True)
	
if __name__ == "__main__":
	save(2,4)