import streamlit as st
import time
import openai
from openai import AzureOpenAI
import json

azure_token = None
temperature = 0.85

st.set_page_config(layout='wide')

class GPTClient():
    def __init__(self, account, api_key, endpoint=''):
        self.account = account
        self.api_key = api_key
        self.endpoint = endpoint

    def generate(self, gpt_args):
        if self.account == 'OpenAI':
            openai.api_key = self.api_key
            return openai.ChatCompletion.create(**gpt_args)
        elif self.account == 'Azure':
            azure_client = AzureOpenAI(
                api_key=self.api_key,  
                api_version="2023-12-01-preview",
                azure_endpoint = self.endpoint
            )
            return azure_client.chat.completions.create(**gpt_args)

# Initialize session state variables if not already set
if 'show_dropdowns' not in st.session_state:
    st.session_state.show_dropdowns = True

if 'selections' not in st.session_state:
    st.session_state.selections = {}


def send_request_to_azure(client, test_desc, test_question, num_responses = 5):
    gpt_args = {
        'messages': [{'role': 'system', 'content': test_desc}, {'role': 'user', 'content': test_question}], 
        'model': 'gpt-4', 
        'temperature': temperature, 
        'top_p': 1, 
        'max_tokens': None, 
        'n': num_responses, 
        'response_format': {"type": "json_object"}
    }

    response = client.generate(**gpt_args)
    return response

def parse_response(response):
    return [json.loads(response.choices[i].message.content) for i in range(len(response.choices))]

def stream_response(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

def build_system_prompt(test_desc, correct_option):
    desc_dict = {
        'base': 'You are an economics research assistant. Please give one example testing the ability to ',
        'correct_option': "Please tag the correct option with '(correct option)'. ",
        'json': "Please keep the questions brief and give a json string where for each example there should be a field titled 'question' that contains the text preceding the options and a field titled 'options' that is a list containing the text detailing each option. Do not include the option letter but simply the option text."
    }
    if correct_option:
        return desc_dict['base'] + test_desc + desc_dict['correct_option'] + desc_dict['json']
    return desc_dict['base'] + test_desc + desc_dict['json']

def build_user_prompt(user_prompt):
    return 'Here is an example:\n' + user_prompt

def format_mcq(json_data):
    """
    Takes a JSON object with 'question' and 'options' and formats it as a MCQ.
    
    Args:
        json_data (str): JSON string containing 'question' and 'options' keys.
        
    Returns:
        str: Formatted MCQ as a string.
    """

    # Get the question and options
    question = json_data['question']
    options = json_data['options']

    # Start building the MCQ string
    mcq = f"{question}\n"

    # Add each option prefixed with a capital letter
    for i, option in enumerate(options):
        letter = chr(65 + i)  # Convert index to uppercase letter (A, B, C, ...)
        mcq += f"{letter}. {option}\n"

    return mcq

# Define the default options for the dropdowns
# element_options = ['Hydrogen', 'Oxygen', 'Carbon', 'Custom']
# domain_options = ['Science', 'Math', 'History', 'Custom']
# grade_level_options = ['1', '2', '3', 'Custom']

# Sidebar
with st.sidebar:
    st.header("Model Settings")

    # Client dropdown accessing the GPT API
    account = st.selectbox('GPT Client:', ['OpenAI', 'Azure'])

    # Text input for the API key
    st.session_state.api_key = st.text_input("API Key", type="password")

    # Text input for the endpoint (Azure)
    if account == 'Azure':
        st.session_state.azure_endpoint = st.text_input("Azure Endpoint")
        st.session_state.client = GPTClient(account, st.session_state.api_key, st.session_state.azure_endpoint)
    else:
        st.session_state.client = GPTClient(account, st.session_state.api_key)

    # Temperature setting for model
    temperature = st.slider('Temperature', 0.0, 1.0, 0.85)


# def dropdown_visibility():
    # st.session_state.show_dropdowns = False

# if st.session_state.show_dropdowns:
#     dropdown_container = st.empty()
#     with dropdown_container:
#         dropdowns = st.columns(3)
#         with dropdowns[0]:
#             # Dropdown for Element Name
#             element_name = st.selectbox('Element Name', element_options)
#             if element_name == 'Custom':
#                 custom_element = st.text_input('Enter custom element name')
#             st.session_state.show_dropdowns = not st.button('Go')
#         with dropdowns[1]:
#             # Dropdown for Domain
#             domain = st.selectbox('Domain', domain_options)
#             if domain == 'Custom':
#                 custom_domain = st.text_input('Enter custom domain')
#         with dropdowns[2]:
#             # Dropdown for Grade Level
#             grade_level = st.selectbox('Grade Level', grade_level_options)
#             if grade_level == 'Custom':
#                 custom_grade = st.text_input('Enter custom grade level')

# if not st.session_state.show_dropdowns:
# dropdown_container.empty()
# st.session_state.selections = {
#     'element': element_name,
#     'domain': domain,
#     'grade_level': grade_level
# }
# if st.sidebar.button('Reset'):
    # st.session_state.go_button = False

