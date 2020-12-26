import streamlit as st
from pag1 import main as  pag1
#from pag2 import save as  pag2
from pag3 import main as  pag3

st.set_page_config(page_title='Risk-Classificator',page_icon='🌎')
hide_footer_style = """
<style>
.reportview-container .main footer {visibility: hidden;}    
"""
st.markdown(hide_footer_style, unsafe_allow_html=True)

def show_footer():
	st.markdown("***")
	st.markdown("**© 2021 Developed by Daniele Grotti **") 
	st.markdown("**Like this tool?** Follow me on  "
				"[Linkedin](https://www.linkedin.com/in/daniele-grotti-38681146)")


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
	#st.button("Re-run")
	# set up layout
	st.title("Dominica's GEO-Risk Classificator")
	pag_name = ["Risk Classification","Coordinate conversion WGS84-32619 UTM ZONE19/WGS84-EPGS4326"]
	
	OPTIONS = pag_name
	#sim_selection = st.radio('Select the option', OPTIONS)
	sim_selection = st.radio('Select the option', OPTIONS)

	if sim_selection == pag_name[0]:
		pag1()
	elif sim_selection == pag_name[1]:
		pag3()
	else:
		st.markdown("Something went wrong. We are looking into it.")

	show_footer()
	
if __name__ == "__main__":
	main()


