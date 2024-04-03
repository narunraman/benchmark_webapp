import openai
from openai import AzureOpenAI
import time
import pandas as pd
import streamlit as st
import pickle as pkl
import json
import requests

SUFFIX_OPTIONS = {
    'mc':"\nAnswer by writing the option letter corresponding to the correct option. WRITE ONLY A SINGLE LETTER. \n\nCorrect Answer: ",
    'explain_answer': "\nBegin by explaining your reasoning in 2-3 sentences, enclosed in triple quotes. After your explanation, select and state the correct answer by writing 'Correct Answer: ' followed by your choice. BEGIN WITH YOUR EXPLANATION AND WRITE THE CORRECT ANSWER AT THE END",
    'explanation': "\nBegin by explaining your reasoning in 2-3 sentences, enclosed in triple quotes.",
}

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
    
    # TODO: fix this
    def generate_stream(self, gpt_args):
        if self.account == 'Azure':
            headers = {
                "Ocp-Apim-Subscription-Key": self.api_key,
                "Content-Type": "application/json"
            }
            gpt_args['stream'] = True  # Enable streaming
            response = requests.post(f"{self.endpoint}/chat/completions", headers=headers, json=gpt_args, stream=True)
            for line in response.iter_lines():
                if line:
                    yield line.decode('utf-8')


def send_request(client, messages, num_responses = 5, temperature = 0):
    
    gpt_args = {
        'messages': messages, 
        'model': 'gpt-4', 
        'temperature': temperature, 
        'top_p': 1, 
        'max_tokens': None, 
        'n': num_responses
    }

    response = client.generate(gpt_args)
    return response

def send_request_stream(client, messages, num_responses = 5, temperature = 0):
    gpt_args = {
        'messages': messages, 
        'model': 'gpt-4', 
        'temperature': temperature, 
        'top_p': 1, 
        'max_tokens': None, 
        'n': num_responses
    }

    yield client.generate_stream(gpt_args)

def build_prefix(num_shots):
    return 'Hi!'



def generate_test_question(client, test_desc, test_question, num_responses = 5, temperature=0.85):
    gpt_args = {
        'messages': [{'role': 'system', 'content': test_desc}, {'role': 'user', 'content': test_question}], 
        'model': 'gpt-4', 
        'temperature': temperature, 
        'top_p': 1, 
        'max_tokens': None, 
        'n': num_responses, 
        'response_format': {"type": "json_object"}
    }

    response = client.generate(gpt_args)
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

def load_templates(element, domain, grade_level):
    st.session_state.templates = st.session_state.dropdown_data.query("element == @element and domain == @domain and grade_level == @grade_level")['templates'].tolist()

def load_dropdown_data():
    st.session_state.dropdown_data = pkl.load('templates.pkl')

# Function to display the current chat message
def display_current_message(index, responses):
    current = index % len(responses)
    
    with st.chat_message("assistant"):
        st.write(responses[current])

# Function to display the latest chat message
def display_last_message(responses):
    with st.chat_message("assistant"):
        st.write(responses[-1])

# Function to increment carousel index
def next_message(responses):
    st.session_state.carousel_index = (st.session_state.carousel_index + 1) % len(responses)

# Function to decrement carousel index
def prev_message(responses):
    st.session_state.carousel_index = (st.session_state.carousel_index - 1) % len(responses)


def generate_fake_dataframe():
    # Define the possible values for each column
    elements = ['Pareto Efficiency Axiom', 'Plurality Vote', 'Carbon']
    domains = ['Science', 'Math', 'History']
    grade_levels = ['1', '2', '3']
    
    # Define templates
    templates = [f'Template {i}' for i in range(1, 6)]

    # Initialize an empty list to store the row data
    rows = []

    # Generate rows for each combination of element, domain, and grade_level
    for element in elements:
        for domain in domains:
            for grade_level in grade_levels:
                for template in templates:
                    rows.append({'element': element, 'domain': domain, 'grade_level': grade_level, 'template': template})
    # Create a DataFrame from the rows
    df = pd.DataFrame(rows)

    return df