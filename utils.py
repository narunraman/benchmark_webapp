import streamlit as st
import streamlit_antd_components as sac
import uuid
import pandas as pd


display_name_to_var = {
    'Addition and Subtraction': 'add_sub',
    'Best Response': 'best_response',
    'Borda Count': 'borda_voting',
    'Compute Expectations': 'compute_expectations',
    'Conditional Syllogism': 'conditional',
    'Equivalence of Contrapositive': 'implications',
    'Condorcet Criterion': 'condorcet_criterion',
    'Independence over Lotteries': 'independence_risk',
    'Interpret Games': 'interpret_games',
    'Avoidance of Dominated Strategies': 'dominated_strategies',
    'Iterated Removal of Dominated Strategies': 'iterated_removal',
    'Maximize Expected Utility': 'maximize_expected_utility',
    'Pareto Efficiency Axiom': 'pareto_axiom',
    'Plurality Voting': 'plurality_voting',
    'Pure Nash Equilibrium': 'pure_nash',
    'Subgame-Perfect Nash Equilibrium': 'subgame_nash',
    'Categorical Syllogism': 'syllogism',
    'First-Order False-Belief': 'theory_of_mind',
}

def load_pickle(filename):
    df = pd.read_pickle(f'data/{filename}.pkl')
    st.session_state.df = df

categories = {
    "Foundations": [
        'Arithmetic',
        'Probability', 
        'Optimization', 
        'Logic', 
        'Theory of Mind'
    ], 
    "Decisions in Single-Agent Environments": [
        'Axioms of Utility in Deterministic Environments', 
        'Avoidance of Cognitive Biases in Deterministic Environments',
        'Axioms of Utility in Stochastic Environments', 
        'Avoidance of Cognitive Biases in Stochastic Environments',
    ], 
    "Decisions in Multi-Agent Environments": [
        'Normal Form Games',
        'Extensive Form Games',
        'Imperfect Information in Extensive Form Games',
        'Infinitely Repeated Games',
        'Bayesian Games'
    ],
    "Decisions on Behalf of Others": [
        'Axioms of Social Choice',
        'Social Choice',
        'Desirable Properties in Mechanism Design',
        'Mechanism Design',
    ],
}

def cascade_callback():
    try:
        st.session_state.display_question = st.session_state[st.session_state.cascade_key][-1]
    except:
        st.session_state.display_question = 'EMPTY_DISPLAY'
    st.session_state.cascade_clicked = True

def gen_hierarchies():
    st.session_state.name2index = {}
    st.session_state.cascader_items = []
    st.session_state.tree_items = []
    counter = 0
    for category in categories:

        cascader_group_items = []
        tree_group_items = []

        cat_index = counter
        counter += 1
        for group_name in categories[category]:
            
            cascader_task_items = []
            tree_task_items = []

            group_index = counter
            counter += 1
            for name, row in st.session_state.df.groupby('group_name').get_group(group_name).iterrows():
                
                cascader_task_items.append(sac.CasItem(row['task_name'].replace("\'S", "\'s")))
                tree_task_items.append(sac.TreeItem(row['task_name']))

                task_index = counter
                st.session_state.name2index[row['task_name']] = [cat_index, group_index, task_index]
                counter += 1
            
            cascader_group_items.append(sac.CasItem(group_name, children = cascader_task_items))
            tree_group_items.append(sac.TreeItem(group_name, children=tree_task_items, disabled=True))
            
        st.session_state.cascader_items.append(sac.CasItem(category, children = cascader_group_items))
        st.session_state.tree_items.append(sac.TreeItem(category, children = tree_group_items, disabled=True))

def display_explorer():
    cascade_index = st.session_state.name2index.get(st.session_state.display_question, 'EMPTY_DISPLAY')

    st.session_state.cascade_key = str(uuid.uuid4())
    if cascade_index != 'EMPTY_DISPLAY':
        sac.cascader(
                items=st.session_state.cascader_items, 
                label='**Choose an Element:**', 
                index=cascade_index,
                format_func='title', 
                placeholder='Type or Click to Select', 
                search=True, 
                clear=True,
                key=st.session_state.cascade_key,
                on_change=cascade_callback
        )
    else:
        sac.cascader(
                items=st.session_state.cascader_items, 
                label='**Choose an Element:**', 
                format_func='title', 
                placeholder='Type or Click to Select', 
                search=True, 
                clear=True,
                key=st.session_state.cascade_key,
                on_change=cascade_callback
        )


def load_df(element_name, df_type):
    return pd.read_pickle(f'data/elements/{display_name_to_var[element_name]}/{df_type}.pkl')


def get_metadata(element_name):
    metadata = pd.read_pickle(f'data/elements/{display_name_to_var[element_name]}/questions_metadata.pkl')
    return metadata['domain'].unique().tolist(), metadata['difficulty_level'].unique().tolist()