import streamlit as st
import streamlit_authenticator as stauth
import random
import time
import sys
st.set_page_config(layout = 'wide')
sys.path.append('..')
from generation_utils import send_request, GPTClient
from question_utils import get_test_questions
from utils import *

temperature = 0.0
AZURE_OPENAI_KEY = '4e1861dc55a34ed1b1b25149eea3105c'
AZURE_OPENAI_ENDPOINT = 'https://gpt-4-rationality-001.openai.azure.com/'

# st.title('Evaluation Playground')
# st.session_state.name2index = {}
if 'display_question' not in st.session_state:
    st.session_state.display_question = 'Interpret Games'
# st.session_state.cascader_items = []
load_pickle('all_tasks')
gen_hierarchies()



# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


def reset_messages():
    st.session_state.messages = []


def initialize_conversation(test_questions):
    '''

    '''
    for test_question in test_questions:
        test_question = test_question.replace('\n', '  \n')
        with st.chat_message('user'):
            st.markdown(test_question)
        st.session_state.messages.append({"role": "user", "content": test_question})
        with st.chat_message('assistant'):
            with st.spinner('Generating response'):
                response = send_request(st.session_state.client, st.session_state.messages, 1, temperature)
            response_text = response.choices[0].message.content
            st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})

def conversation_handler():
    '''

    '''
    if prompt := st.chat_input("Message model..."):
        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            with st.spinner('Generating response'):
                response = send_request(st.session_state.client, st.session_state.messages, 1, temperature)
            response_text = response.choices[0].message.content
            st.markdown(response_text)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response_text})
    
def get_valid_q_ids(element_name, domain, grade_level):
    metadata = load_df(element_name, 'questions_metadata')
    valid_q_ids = metadata.query("domain == @domain and difficulty_level == @grade_level")['question_id'].tolist()
    return valid_q_ids

def build_question_text(element_name, domain, grade_level, adaptation):
    q_ids = get_valid_q_ids(element_name, domain, grade_level)
    question_id = random.choice(q_ids).split('_')[0]
    questions_df = load_df(element_name, 'questions')
    options_df = load_df(element_name, 'options')


    test_question, _ = get_test_questions(question_id, questions_df, options_df, {'question_type': adaptation['explanation']})
    
    return test_question

def playground_view():
    with st.expander('Choose a test:', expanded = True):
        # with st.form('hello', border = False):
        display_explorer()
        if st.session_state.display_question != 'EMPTY_DISPLAY':
            domains, grade_levels = get_metadata(st.session_state.display_question)
            cols = st.columns(2)
            with cols[0]:
                domain = st.selectbox('Choose a Domain', domains)
            with cols[1]:
                grade_level = st.selectbox('Choose a Grade Level', grade_levels)
            st.session_state.submitted = st.button("Submit", on_click=reset_messages)
    if st.session_state.submitted:
        st.session_state.messages = []
        test_question = build_question_text(st.session_state.display_question, domain, grade_level, {'num_shots': num_shots, 'explanation': explanation})
        initialize_conversation(test_question)
    
    conversation_handler()




with st.sidebar:
    st.session_state.playground = st.toggle('Playground')
    
    if st.session_state.playground:
        with st.expander("Model Setup", expanded = True):
            with st.form('model_setup', border = False):
                # Client dropdown accessing the GPT API
                account = st.selectbox('GPT Client:', ['OpenAI', 'Azure'])

                # Text input for the API key
                st.session_state.api_key = st.text_input("API Key", type="password")

                # Text input for the endpoint (Azure)
                if account == 'Azure':
                    st.session_state.azure_endpoint = st.text_input("Azure Endpoint")
                    # st.session_state.client = GPTClient(account, st.session_state.api_key, st.session_state.azure_endpoint)
                    client = GPTClient(account, AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT)
                else:
                    client = GPTClient(account, st.session_state.api_key)
                if st.form_submit_button("Submit"):
                    st.session_state.client = client


        st.header('Model Settings')
        
        num_shots = st.slider('Few-Shot Prompting', 0, 5, 0)
        explanation = st.selectbox('Explanation:', ['simultaneous', 'sequential-shown', 'sequential-hidden', 'No Explanation'])

        # Temperature setting for model
        temperature = st.slider('Temperature', 0.0, 1.0, 0.00)

if st.session_state.playground:
    playground_view()

    