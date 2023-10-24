import streamlit as st
import pandas as pd
from st_pages import Page, show_pages, Section, add_page_title


# TODO: add validated column, which takes three values: np.nan for not-visited, 0 for bad, 1 for good
# TODO: need to be able to keep the state of the counters i.e. need to update the actual dataframe

# add_page_title()

show_pages(
    [
        Page("main.py", "Benchmark Viewer", ":book:"),
        # Page("pages/graphs.py", "Dependency Viewer", ":mag:"),
        # Section(name="Developer Tools", icon=":open_file_folder:"),
        Page("pages/validation.py", "Validation", ":pencil:"),
    ]
)

st.sidebar.title("Toolbar")
tasks = ['sunk_cost', 'ambiguity']#, 'endowment']
selected_task = st.sidebar.selectbox("Select a Task", tasks)

@st.cache_data
def load_df(filename):
    return pd.read_pickle(f'data/{filename}.pkl')

for task in tasks:
    if f'{task}_df' not in st.session_state:
        st.session_state[f'{task}_df'] = load_df(task)



# Difficulty Selection
domains = st.session_state[f'{selected_task}_df']['domain'].unique()
task_types = st.session_state[f'{selected_task}_df']['type'].unique()
selected_domain = st.sidebar.selectbox("Select a Domain", domains)
selected_type = st.sidebar.selectbox("Select a Type", task_types)
if st.session_state[f'{selected_task}_df']['difficulty_level'].min() != st.session_state[f'{selected_task}_df']['difficulty_level'].max():
    slider_difficulty = st.sidebar.slider("Select a Difficulty", min_value=int(st.session_state[f'{selected_task}_df']['difficulty_level'].min()), max_value=int(st.session_state[f'{selected_task}_df']['difficulty_level'].max()), value=int(st.session_state[f'{selected_task}_df']['difficulty_level'].median()))
else:
    st.sidebar.write("Difficulty: ", st.session_state[f'{selected_task}_df']['difficulty_level'].max())



st.title(f"Validate {' '.join(selected_task.split('/')[-1].capitalize().split('_'))} Questions")

# Initialize counters
st.session_state.good_counter = st.session_state[f'{selected_task}_df'][st.session_state[f'{selected_task}_df']['domain'] == selected_domain]['validated'].sum()

st.session_state.total_counter = st.session_state[f'{selected_task}_df'][st.session_state[f'{selected_task}_df']['domain'] == selected_domain]['validated'].count()

# Initialize shuffled DataFrame and current_row_index
df_shuffled = None
current_row_index = 0

# Function to initialize and shuffle the DataFrame
def initialize_and_shuffle_dataframe(domain, task_type):
    global df_shuffled
    df_shuffled = st.session_state[f'{selected_task}_df'].loc[(st.session_state[f'{selected_task}_df']['domain'] == domain) & (st.session_state[f'{selected_task}_df']['validated'].isnull()) & (st.session_state[f'{selected_task}_df']['type'] == task_type)].sample(frac=1)
    


# Function to get the next row from the shuffled DataFrame
def get_next_row():
    global df_shuffled
    try:
        next_row = df_shuffled.iloc[0]
    except IndexError:
        return {'status': 'done'}
    return next_row

initialize_and_shuffle_dataframe(selected_domain, selected_type)

def clean_text(string):
    string = string.replace('$', '\$')
    string = string.replace('{}', '[BLANK]')
    return string

# Function to update counters and display new text
def update_counters_and_display():
    global current_row
    current_row = get_next_row()
    if current_row.get('status') != 'done':
        st.write('Requirements')

        st.warning('- '+'  \n- '.join(current_row['description']))# '- Hello  \n - Goodbye')
        st.write("Current Text:")
        try:
            question = clean_text(current_row['questions'])
            st.info(question)
        except AttributeError:
            # TODO: this is currently hard-coded for test questions that have two questions and two options for each.
            try:
                questions = [clean_text(question) for question in current_row['questions']]
                options = [[clean_text(options[0]), clean_text(options[1])] for options in current_row['options']]
                st.info(questions[0] + '  \n' + f'A. {options[0][0]}' + '  \n' f'B. {options[0][1]}' + '  \n  \n' + questions[1] + '  \n' + f'C. {options[1][0]}' + '  \n' f'D. {options[1][1]}')
            except IndexError:
                questions = [clean_text(question) for question in current_row['questions']]
                options = [[clean_text(options[0]), clean_text(options[1])] for options in current_row['options']]
                st.info(questions[0] + '  \n' + f'A. {options[0][0]}' + '  \n' f'B. {options[0][1]}')
        st.text("")
        st.text("")
        button_cols = st.columns(5)
        if button_cols[0].button("Valid Question"):
            st.session_state.good_counter += 1
            st.session_state.total_counter += 1
            mask = st.session_state[f'{selected_task}_df'].questions.apply(lambda x: x == current_row['questions'])
            st.session_state[f'{selected_task}_df'].loc[mask, 'validated'] = 1
        if button_cols[1].button("Bad Question"):
            st.session_state.total_counter += 1
            mask = st.session_state[f'{selected_task}_df'].questions.apply(lambda x: x == current_row['questions'])
            st.session_state[f'{selected_task}_df'].loc[mask, 'validated'] = 0
        if button_cols[-1].button("Save and Exit", type='primary'):
            # TODO: add functionality to save the updated dataframe
            # save_counters()
            st.stop()
    else:
        st.info("Completed All Questions")
        st.text("")
        st.text("")
        button_cols = st.columns(5)
        if button_cols[-1].button("Save and Exit", type='primary'):
            # save_counters()
            st.stop()


# Initial random row
current_row = None
update_counters_and_display()
st.sidebar.write("Good Counter:", st.session_state.good_counter)
st.sidebar.write("Total Validated:", st.session_state.total_counter)
    
try:
    percent_good = round(int(st.session_state.good_counter)/(int(st.session_state.total_counter))*100, 2)
except:
    percent_good = 0

st.sidebar.write(f"Percent Good: {percent_good}%")