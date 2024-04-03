import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import pandas as pd
import colorsys
from streamlit_extras.no_default_selectbox import selectbox 
import random
import textwrap 

st.set_page_config(
    layout='wide'
)

categories = {
    "Foundations": [
        'Arithmetic', 
        'Probability', 
        'Optimization', 
        'Logic', 
        'Theory of Mind'
    ], 
    "Preferences": [
        'Utility Theory', 
        'Reference Independence'
    ], 
    "Decision Making Under Uncertainty": [
        'Expected Utility Theory', 
        'Risk Assessment'
    ], 
    "Decision Making in the Presence of Other Agents": [
        'Single-Round Game Theory',
        'Multi-Round Game Theory',
    ]
}


df = pd.read_pickle('data/all_tasks.pkl')
sources = df['tasks']
targets = df['dependencies'].apply(lambda x: x[0] if x else x)
task2group_name = {task_name: group_name for group_name, task_name in zip(df['group_name'], df['tasks'])}
rev_categories = {group_name: cat_name for cat_name in categories for group_name in categories[cat_name]}

nodes = []
edges = []

def value_to_color(value):
    # Ensure the value is in the range [0, 100]
    value = max(0, min(100, value))

    # Map the value to the range [0, 120], where 0 is red, 120 is green
    hue = (value / 100) * 120

    # Convert HSV to RGB
    rgb = colorsys.hsv_to_rgb(hue / 360, 1, 1)

    # Scale RGB values to the range [0, 255]
    rgb = tuple(int(val * 255) for val in rgb)

    hex_color = "#{:02x}{:02x}{:02x}".format(*rgb)

    return hex_color


group_shapes = {'Foundations': 'square',
'Preferences': 'dot',
'Decision Making Under Uncertainty': 'triangle',
'Decision Making in the Presence of Other Agents': 'diamond'}

def generate_graph():
    for source in sources:
        # wrapper = textwrap.TextWrapper(width=13) 
        name = '\n'.join(textwrap.wrap(text=source, width = 13, break_long_words = False))
        nodes.append(Node(id = source,
                        label = name,
                        size = 20,
                        chosen = True,
                        borderWidth = 3,
                        borderWidthSelected = 2,
                        maxZoom=2,
                        minZoom=1,
                        initialZoom=1,
                        #   physics = True,
                        shape = group_shapes[rev_categories[task2group_name[source]]],
                        color = {'background': st.session_state.colors[source], 'border': st.session_state.colors[source], 'hover': {'border': st.session_state.colors[source], 'background': 'white'}, 'highlight': {'border': st.session_state.colors[source], 'background': 'black'}}, 
                        font = {'color': 'white'},
                        group = rev_categories[task2group_name[source]]))

    for source, target in zip(sources, targets):
        if target:
            for end in target:
                # print(target)
                # print(source, end)
                edges.append( Edge(source = source, 
                                target = end,
                                color = {'color': 'gray', 'hover': 'white', 'highlight': 'white'},
                                smooth = {'enabled': True, 'type': 'continuous'},
                                arrowStrikethrough = False,
                                width = 2,
                                hoverWidth = 3,
                                selectionWidth = 4))



    st.session_state.config = Config(width=500,
                    height=600,
                    interaction = {'hover': True, 'multiselect': True},
                    directed=True, 
                    physics = {'enabled': True, 
                            'barnesHut': {
                                'theta': 0.5, 
                                'gravitationalConstant': -5000,
                                'centralGravity': 0.3,
                                'springLength': 95,
                                'springConstant': 0.04,
                                'damping': 0.09,
                                'avoidOverlap': 1
                        }
                    },
                    layout = {"hierarchical": {
                        'enabled': True, 
                        'levelSeparation': 150, 
                        'nodeSpacing': 120, 
                        'sortMethod': 'directed',
                        'shakeTowards': 'leaves',
                        'direction': 'UD'}}, 
                    nodeHighlightBehavior=True, 
                    # graphviz_layout='sfdp',
                    # graphviz_config={"ranksep": 10, "nodesep": 100},
                    # highlightColor="#FFFFFF",
                    collapsible=True,
                    maxZoom=2,
                    minZoom=0.1,
                    color = {'background': 'white'},
                    node={'labelProperty':'label', 'labelColor': 'white'},
                    link={'labelProperty': 'label', 'renderLabel': True},
                    # **kwargs
                    )
# st.header('Dependency Graph:')
col1, col2 = st.columns([0.45, 0.55])
with col1:
    # with st.expander('Dependency Graph:'):
    model = selectbox('Select a Model:', ['Model 1', 'Model 2'])
with col2:
    if model == None:
        st.session_state.colors = {task_name: 'lightblue' for task_name in sources}
        generate_graph()
        return_value = agraph(nodes=nodes, edges=edges, config=st.session_state.config)
    else:
        st.session_state.colors = {task_name: value_to_color(random.randint(0, 100)) for task_name in sources}
        generate_graph()
        return_value = agraph(nodes=nodes, edges=edges, config=st.session_state.config)

# print(return_value)