import streamlit as st
from pag1 import main as  pag1
from pag2 import main as  pag2
from pag3 import main as  pag3

#@st.cache(suppress_st_warning=True)
def main():
	# ################ css background #########################
	page_bg_img = '''
	<style>
	body {
	background-image: url("https://i.pinimg.com/originals/85/6f/31/856f31d9f475501c7552c97dbe727319.jpg");
	background-size: cover;
	}
	</style>
	'''
	st.markdown(page_bg_img, unsafe_allow_html=True)
	################
	st.button("Re-run")
	# set up layout
	st.title("Dominica GEO-Risk Evaluation")
	pag_name = ["Risk Classification","Coordinate conversion to WGS84 4326/ WGS84-EPSG 32619 UTM ZONE19","pag3"]
	
	OPTIONS = pag_name
	#sim_selection = st.radio('Select the option', OPTIONS)
	sim_selection = st.radio('Select the option', OPTIONS)

	if sim_selection == pag_name[0]:
		pag1()
	elif sim_selection == pag_name[1]:
		pag2()
	elif sim_selection == pag_name[2]:
		pag3()
	else:
		st.markdown("Something went wrong. We are looking into it.")
	

if __name__ == "__main__":
	main()


