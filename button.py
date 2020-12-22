import streamlit as st
import clipboard
import SessionState #pip install py-session
import time

def MAINFUNCTION(tojoin):
    JOINLIST = "\n".join(str(i) for i in tojoin)
    return JOINLIST

state = SessionState._get_state()
box2 = st.text_area("enter your age")
labels = [1, 2, 3, 4, 5]
box1 = st.text_area('Generated From function', value='type here')
box4 = st.empty()

if st.button("Submit"):
    runapp = MAINFUNCTION(labels)
    with box4.beta_container():
        state.box4 = st.text_area("Generated", runapp)

    state.box1 = st.text_area("Generated From function", runapp)
    state.box3 = st.text_area('enter your name', runapp)
    # st.success(box1)
if st.button('copy'):
    st.success(f'box1 to be copied: {state.box1}')

    clipboard.copy(state.box1)
    clipboard_paste()
    st.success("copied successfully")

    st.success(f'box4 to be copied: {state.box4}')
    st.success(f'box1 to be copied: {state.box3}')