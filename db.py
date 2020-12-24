import pandas as pd
import numpy as np
#from pathlib import Path
import sqlite3
from sqlite3 import Connection
import streamlit as st
import pandas as pd
import xlsxwriter

#URI_SQLITE_DB = "test.db"
URI_SQLITE_DB = "test1.db"

def init_db(conn: Connection):
	conn.execute(
		"""CREATE TABLE IF NOT EXISTS test
			(LATITUDE FLOAT,LONGITUDE FLOAT,RISK_LANDSLIDE INT,RISK_FLOOD INT);"""
	)
	conn.commit()

def display_data(conn: Connection):
	if st.checkbox("Display data in sqlite databse"):
		st.dataframe(get_data(conn))

def get_data(conn: Connection):
	df = pd.read_sql("SELECT * FROM test", con=conn)
	return df

def delete_all_tasks(conn: Connection):
    """
    Delete all rows in the tasks table
    :param conn: Connection to the SQLite database
    :return:
    """
    sql = 'DELETE FROM test'
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

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
	return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="extract.xlsx">Download results on xlsx </a>' # decode b'abc' => abc
# df = ... # your dataframe
# st.markdown(get_table_download_link(df), unsafe_allow_html=True)


def save(x,y,k,z):
	#### First part DB ##########
	def build_sidebar(conn: Connection):
		conn.execute(f"INSERT INTO test (LATITUDE,LONGITUDE,RISK_LANDSLIDE,RISK_FLOOD) VALUES ({x}, {y},{k}, {z})")
		conn.commit()
	conn = get_connection(URI_SQLITE_DB)
	init_db(conn)
	#############################
	x,y,k,z

	################## Export to Excel SQLite
	build_sidebar(conn)
	#display_data(conn)
	df = get_data(conn)
	#df = pd.DataFrame(np.random.randint(0,100,size=(100, 4)), columns=list('ABCD'))
	#download = st.button("export results")
	st.markdown(get_table_download_link(df), unsafe_allow_html=True)
	
if __name__ == "__main__":
	save(2.112,4,6,8)