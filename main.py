import streamlit as st
import pandas as pd
from streamlit_extras.grid import grid
from streamlit_extras.tags import tagger_component
from annotated_text import annotated_text, annotation

st.set_page_config(
    page_title="Curriculum Viewer",
    page_icon="",
)


# df = pd.read_pickle("../generated_samples/utility_theory/filled/compute_expec_util.pkl")
# # @st.cache
# def convert_df(df):
#     # IMPORTANT: Cache the conversion to prevent computation on every rerun
#     return df.to_csv().encode('utf-8')

# csv = convert_df(df)

st.title("Rationality Benchmark")

# st.sidebar.tabs(["View Filter", "Generate Test"])
st.sidebar.header("Filters")

categories = {"Foundations": [
               'Arithmetic', 
               'Probability', 
               'Optimization', 
               'Logic', 
               'Theory of Mind'
               ], 
               "Preferences": [
                   'Utility Theory', 'Reference Independent Decision-Making'], "Decision Making Under Uncertainty": ['Expected Utility Theory', 'Judgements Under Limited Data'], "Decision Making in the Presence of Other Agents": ['Game Theory']
                   }

selected_categories = {category: [] for category in categories}
for category in categories:
    with st.sidebar.expander(category):
        selected_categories[category].append(st.slider('Difficulty range:', 0, 12, (2, 7), key=category))
# st.sidebar.write('Values:', values)
# st.sidebar.download_button(label="Download Test", data=csv, file_name='large_df.csv', mime='text/csv', type='primary')

# progress_bar = st.sidebar.progress(0)
# status_text = st.sidebar.empty()
# last_rows = np.random.randn(1, 1)
# chart = st.line_chart(last_rows)

# for i in range(1, 101):
#     new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
#     status_text.text("%i%% Complete" % i)
#     chart.add_rows(new_rows)
#     progress_bar.progress(i)
#     last_rows = new_rows

# progress_bar.empty()



# foundations, preferences, uncertainty, game = st.tabs(categories)

tab_class = st.tabs(categories)
df = pd.DataFrame([
    {'Category': 'Arithmetic', "Tasks": ["Can Add and Subtract Integers", "Can Add and Subtract with Fractions", "Can Add and Subtract Large Numbers", ], "Difficulties": [0, 1, 2], 'Selected': True},
    {'Category': 'Arithmetic', "Tasks": ["Can Multiply and Divide Integers", "Can Multiply and Divide with Fractions", "Can Multiply and Divide Large Numbers"], "Difficulties": [1, 2, 3], 'Selected': True},
    {'Category': 'Probability', "Tasks": ["Correctly Assigns Probabilities to a Single Outcome", "Correctly Assigns Probabilities to Few Outcomes", "Correctly Assigns Probabilities to Many Outcomes"], "Difficulties": [1, 2, 3], 'Selected': True},
    {'Category': 'Probability', "Tasks": ["Respects Complement Rule", "Respects Complement Rule with Three Outcomes", "Respects Complement Rule with Many Outcomes"], "Difficulties": [1, 2, 3], 'Selected': True},
    {'Category': 'Probability', "Tasks": ["Can Compute Joint Probabilities", "Can Compute Joint Probabilities Harder", "Can Compute Joint Probabilities Hardest"], "Difficulties": [3, 4, 5], 'Selected': True},
    {'Category': 'Probability', "Tasks": ["Can Compute Marginal Probabilities", "Can Compute Marginal Probabilities Harder", "Can Compute Marginal Probabilities Hardest"], "Difficulties": [3, 4, 5], 'Selected': True},
    {'Category': 'Probability', "Tasks": ["Can Correctly Use Bayes Rule in Multiple Choice", "Can Correctly Use Bayes Rule in Open-Ended"], "Difficulties": [5, 6], 'Selected': True},
    {'Category': 'Optimization', "Tasks": ["Can Pick Biggest Number"], "Difficulties": [0], 'Selected': True},
    {'Category': 'Optimization', "Tasks": ["Can Compute Simple Unconstrained Optimization"], "Difficulties": [2], 'Selected': True},
    {'Category': 'Optimization', "Tasks": ["Can Compute Simple Constrained Optimization"], "Difficulties": [3], 'Selected': True},
    {'Category': 'Theory of Mind', "Tasks": ["Task Easy", "Task Hard"], "Difficulties": [3, 4], 'Selected': True},
    {'Category': 'Logic', "Tasks": ["Can Correctly Identify Simple Logically Equivalent Statements", "Can Correctly Identify Intermediate Logically Equivalent Statements", "Can Correctly Identify Hard Logically Equivalent Statements"], "Difficulties": [2, 3, 4], 'Selected': True},
    {'Category': 'Utility Theory', "Tasks": ["Respects Transitivity Across Three Options", "Respects Transitivity Across Four Options", "Respects Transitivity Across Many Options"], "Difficulties": [2, 3, 4], 'Selected': True},
    {'Category': 'Utility Theory', "Tasks": ["Ignores a Single Irrelevant Alternative", "Ignores Two Irrelevant Alternatives", "Ignores Many Irrelevant Alternatives"], "Difficulties": [4, 5, 6], 'Selected': True},
    # {'Category': 'Reference Independent Decision-Making', "Tasks": ["Unaffected by Peer Pressure"], "Difficulties": [7], 'Selected': True},
    {'Category': 'Reference Independent Decision-Making', "Tasks": ["Ignores Sunk Costs in One Option", "Ignores Sunk Costs Across Many Options"], "Difficulties": [7, 8], 'Selected': True},
    # {'Category': 'Reference Independent Decision-Making', "Tasks": ["Unaffected by Status Quo"], "Difficulties": [7], 'Selected': True},
    {'Category': 'Reference Independent Decision-Making', "Tasks": ["Unaffected by Being Endowed with One Item", "Unaffected by Being Endowed with Many Items"], "Difficulties": [6, 7], 'Selected': True},
    {'Category': 'Reference Independent Decision-Making', "Tasks": ["Discounts Consistently Across a Few Time Steps", "Discounts Consistently Across Many Time Steps"], "Difficulties": [4, 5], 'Selected': True},
    {'Category': 'Reference Independent Decision-Making', "Tasks": ["Can Recall a Few Objects Agnostic to Ordering", "Can Recall Many Objects Agnostic to Ordering"], "Difficulties": [5, 6], 'Selected': True},
    {'Category': 'Expected Utility Theory', "Tasks": ["Can Compute Expected Utility of Two Outcomes", "Can Compute Expected Utility of Three Outcomes", "Can Compute Two Expected Utilities of Many Outcomes", "Can Compute Many Expected Utilities of Many Outcomes"], "Difficulties": [3, 4, 5, 6], 'Selected': True},
    {'Category': 'Expected Utility Theory', "Tasks": ["Can Maximize Expected Utility Between Two Options", "Can Maximize Expected Utility Between Three Options", "Can Maximize Between Many Expected Utilities of Three Outcomes", "Can Maximize Between Many Expected Utilities of Many Outcomes"], "Difficulties": [4, 5, 6, 7], 'Selected': True},
    # {'Category': 'Expected Utility Theory', "Tasks": ["Does Not Make Risk Averting Decisions"], "Difficulties": [6], 'Selected': True},
    # {'Category': 'Expected Utility Theory', "Tasks": ["Does Not Make Risk Seeking Decisions"], "Difficulties": [6], 'Selected': True},
    # {'Category': 'Expected Utility Theory', "Tasks": ["Does Not Make Loss Averting Decisions"], "Difficulties": [6], 'Selected': True},
    {'Category': 'Expected Utility Theory', "Tasks": ["Computes Expectations of Few Outcomes with Objective Probabilities", "Computes Expectations of Many Outcomes with Objective Probabilities", ], "Difficulties": [7, 8, 9], 'Selected': True},
    {'Category': 'Judgements Under Limited Data', "Tasks": ["Not Averse to Ambiguity in Choices"], "Difficulties": [7], 'Selected': True},
    # {'Category': 'Judgements Under Limited Data', "Tasks": "Can Make Accurate Judgements on Everyday Events", "Difficulties": [6], 'Selected': True},
    {'Category': 'Game Theory', "Tasks": ["Can Interpret 2x2 Normal Form", "Can Interpret 3x3 Normal Form", "Can Interpret XxX Normal Form"], "Difficulties": [2, 3, 4], 'Selected': True},
    {'Category': 'Game Theory', "Tasks": ["Does Not Play Dominated Strategies in 2x2 Games", "Does Not Play Dominated Strategies in 3x3 Games", "Does Not Play Dominated Strategies in XxX Games"], "Difficulties": [3, 4, 5], 'Selected': True},
    {'Category': 'Game Theory', "Tasks": ["Can Best Respond in 2x2 Games", "Can Best Respond in 3x3 Games", "Can Best Respond in XxX Games"], "Difficulties": [5, 6, 7], 'Selected': True},
    {'Category': 'Game Theory', "Tasks": ["Can Find Pure Nash in 2x2 Games","Can Find Pure Nash in 3x3 Games","Can Find Pure Nash in XxX Games"], "Difficulties": [9, 10, 11], 'Selected': True},
]   
)


difficulty_values = {}

for tab_class, category_texts in zip(tab_class, categories):
    for category_text in categories[category_texts]:
        with tab_class.expander(category_text):
            # tagger_component("", ["grade 0", "grade 1", "grade 2"], color_name=["green", "orange", "red"],)
            # st.write('hello')
            # task_name, difficulty_slider = st.columns(2)

            my_grid = grid([0.6,0.3], vertical_align="bottom")

            # with task_name:
            my_grid.write("**Difficulty Range:**")
            my_grid.write("**Task:**")
            # difficulty_slider.slider("**Difficulty Range:**", 0, 12, key=category_text)
            rows = df.groupby('Category').get_group(category_text)
            for name, difficulties in zip(rows['Tasks'], rows['Difficulties']):
                if f'{name}_value' not in st.session_state:
                    st.session_state[f'{name}_value'] = 0
                
                if st.session_state[f'{name}_value'] == 0:
                    html=f'''
                    <br> {name[difficulties[0]]}
                    '''
                else:
                    html=f'''
                    <br> {name[difficulties.index(st.session_state[f'{name}_value'])]}
                    '''

                my_grid.markdown(html, unsafe_allow_html=True)
                if len(difficulties) > 1:
                    st.session_state[f'{name}_value'] = my_grid.slider(" ", difficulties[0], difficulties[-1], key=name)
                # else:
                #     st.session_state.value = difficulties[0]
                #     my_grid.write(st.session_state.value)
                # task_name.write('')
                # task_name.write('')
                # my_grid.empty(name[difficulties.index(value)])
                
                # my_grid.markdown(f'<p color:Yellow">{name[difficulties.index(value)]}</p>', unsafe_allow_html=True)
                # task_name.write('')
                # task_name.write('')
                # task_name.write('')
            # for row in rows['Difficulties']:
                
                # for diff_range in df.groupby('Category').get_group(category_text)['Difficulties']:
                #     difficulty_slider.slider(" ", diff_range[0], diff_range[-1], key=category_text)
            # st.data_editor(
            #     df.loc[df['Category'] == category_text][['Task', 'Difficulty', 'Selected']].set_index('Task'),
            #     column_config={
            #         "Difficulty": st.column_config.ProgressColumn(
            #             "Difficulty",
            #             help="The Level of Difficulty in this task",
            #             format="",
            #             min_value=-1,
            #             max_value=12,
            #             width='medium',
            #         ),
            #         "Task": st.column_config.TextColumn(
            #             "Task",
            #             help="Task",
            #             default="st.",
            #             max_chars=50,
            #             disabled=True,
            #             # validate="^st\.[a-z_]+$",
            #         )
            #     },
            #     key = category_text
            # # hide_index=True,
            # )

# st.write("# Welcome to Streamlit! 👋")

# st.sidebar.success("Select a demo above.")

# st.markdown(
#     """
#     Streamlit is an open-source app framework built specifically for
#     Machine Learning and Data Science projects.
#     **👈 Select a demo from the sidebar** to see some examples
#     of what Streamlit can do!
#     ### Want to learn more?
#     - Check out [streamlit.io](https://streamlit.io)
#     - Jump into our [documentation](https://docs.streamlit.io)
#     - Ask a question in our [community
#         forums](https://discuss.streamlit.io)
#     ### See more complex demos
#     - Use a neural net to [analyze the Udacity Self-driving Car Image
#         Dataset](https://github.com/streamlit/demo-self-driving)
#     - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
# """
# )