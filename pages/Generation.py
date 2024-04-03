import streamlit as st
import streamlit_authenticator as stauth
import random
import time
import sys
sys.path.append('..')
from generation_utils import *
import pickle as pkl
import pandas as pd
st.set_page_config(layout = 'wide')
import yaml
from yaml.loader import SafeLoader

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

azure_token = None
if 'temperature' not in st.session_state:
    st.session_state.temperature = 0.85


def display_carousel(responses):
    # Initialize session state for carousel index
    if 'carousel_index' not in st.session_state:
        st.session_state.carousel_index = 0


    # Display chat message
    with st.session_state.carousel.container(border=True):
        st.write('Example Generation')
        _, _, indicator_col = st.columns([1, 20, 1])
        with indicator_col:
            # current_position = (st.session_state.carousel_index % len(responses)) + 1
            st.write(f"{len(responses)} of {len(responses)}")
        display_current_message(-1, responses)
    
    
    # col1, col2, col3 = st.columns([1, 10, 1])
    # if 'prev_carousel' in st.session_state:
    #     del st.session_state['prev_carousel']
    # if 'next_carousel' in st.session_state:
    #     del st.session_state['next_carousel']
    # # Navigation buttons and indicator
    # with col1:
    #     if st.button("Previous", key=f'prev_carousel'):
    #         prev_message(responses)

    # with col3:
    #     if st.button("Next", key=f'next_carousel'):
    #         next_message(responses)


def playground_view():
    generation_cols = st.columns([0.3, 0.7])
    with generation_cols[0]:
        # st.write(st.session_state.selections)
        with st.expander('Template Description', expanded=True):
            test_desc = st.text_area("Element")
            correct_option = st.toggle('Tag Correct Option')

    system_prompt = build_system_prompt(test_desc, correct_option)

    with generation_cols[1]:
        user_input = st.text_area("Enter template text here")
        user_prompt = build_user_prompt(user_input)


        if st.button('Generate'):
            # with st.chat_message('user'):
                # st.write(user_prompt)
            if not azure_token:
                st.warning("API key is required to send the request.")
            else:
                with st.chat_message('user'):
                    st.write(system_prompt)
                    st.write(user_prompt)
                with st.chat_message("assistant"):
                    with st.spinner('Generating responses'):
                        response = generate_test_question(client=st.session_state.client, test_desc=system_prompt, test_question=user_prompt, temperature=st.session_state.temperature)
                        responses = parse_response(response)
                    for response in responses:
                        st.write(response)





def generation_view():
    st.title('Generate Tests')
    df = generate_fake_dataframe()
    # Create three columns for the selectboxes
    col1, col2, col3, col4 = st.columns(4)

    # Selection for Element in the first column
    with col1:
        selected_element = st.selectbox('Element', df['element'].unique())

    # Filter the DataFrame based on the selected element
    filtered_by_element = df[df['element'] == selected_element]

    # Selection for Domain in the second column, showing only domains available for the selected element
    with col2:
        selected_domain = st.selectbox('Domain', filtered_by_element['domain'].unique())

    # Further filter the DataFrame based on the selected domain
    filtered_by_domain = filtered_by_element[filtered_by_element['domain'] == selected_domain]

    # Selection for Grade Level in the third column, showing only grade levels available for the selected element and domain
    with col3:
        selected_grade_level = st.selectbox('Grade Level', filtered_by_domain['grade_level'].unique())

    # Filter to get the templates for the selected element, domain, and grade level
    filtered_templates = filtered_by_domain[filtered_by_domain['grade_level'] == selected_grade_level]['template'].tolist()

    with col4:
        num2generate = st.number_input('Number to generate', value = 200, step = 1)

    template_desc = 'identify whether or not the chosen output of a voting rule satisfies the Pareto Efficiency axiom between two options. Follow the curly brace formatting exactly (i.e., only use the following: {one}, {two}, {preferences} and do not put the option name in curly braces) but change the setting of the question.'

    template_texts = ['A small community is deciding between two proposals to consider: Proposal {one} and Proposal {two}. Their preference orderings are:\n{preferences}\nAfter the votes were tallied, Proposal {two} was chosen as the final decision. Does this decision satisfy the Pareto Efficiency axiom?\nA. Yes\nB. No', 'A local government is deciding between two policy options: Policy {one} and Policy {two}. The preferences of the individuals are as follows:\n{preferences}\nAccording to the Pareto Efficiency axiom, which policy should be chosen?\nA. Policy {one}\nB. Policy {two}']



    filtered_templates = [{'test_desc': build_system_prompt(template_desc, True), 'test_question': build_user_prompt(template_texts[i])} for i in range(2)]

    generation_buttons = st.columns(9)
    with generation_buttons[1]:
        st.session_state.generation_stop = st.button('Stop')
    with generation_buttons[0]:
        st.session_state.generation_start = st.button('Generate')
    if st.session_state.generation_start:
        progress_text = "Generation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)
        
        # Carousel code
        viewable_responses = []
        if 'carousel' not in st.session_state:
            st.session_state.carousel = st.empty()
        
        for percent_complete in range(num2generate):
            template = random.choice(filtered_templates)
            if st.session_state.api_key == None:
                st.warning("API key is required to send the request.")
                break
            else:
                # response = send_request(st.session_state.client, template['test_desc'], template['test_question'], num_responses=1, temperature=temperature)
                time.sleep(2)
                my_bar.progress((percent_complete+1)/num2generate, text=progress_text)
                if percent_complete % 2 == 0:
                    st.session_state.carousel.empty()
                    st.session_state.carousel = st.empty()
                    # viewable_responses.append(parse_response("{'question': 'what is up', 'options': ['nothing', 'something'] }"))
                    viewable_responses.append({'question': 'what is up', 'options': ['nothing', 'something'] })
                    display_carousel(viewable_responses)
        


##############################################################
#                    
#                    Sidebar Code
#
##############################################################

def sidebar_view():
    with st.sidebar:
        st.write(f'Welcome {st.session_state.name}!')

        st.session_state.playground_view = st.sidebar.toggle('Playground')

        st.header('Model Settings')

        # Client dropdown accessing the GPT API
        account = st.selectbox('GPT Client:', ['OpenAI', 'Azure'])

        # Text input for the API key
        st.session_state.api_key = st.text_input("API Key", type="password")

        # Text input for the endpoint (Azure)
        if account == 'Azure':
            st.session_state.azure_endpoint = st.text_input("Azure Endpoint")
            # st.session_state.client = GPTClient(account, st.session_state.api_key, st.session_state.azure_endpoint)
            st.session_state.client = GPTClient(account, AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT)
        else:
            st.session_state.client = GPTClient(account, st.session_state.api_key)

        # Temperature setting for model
        st.session_state.temperature = st.slider('Temperature', 0.0, 1.0, 0.85)
        
        authenticator.logout()

authenticator.login()

if st.session_state["authentication_status"]:
    sidebar_view()
    if st.session_state.playground_view:
        playground_view()
    else:
        generation_view()
    # x = 10
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')

