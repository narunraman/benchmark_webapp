from string import ascii_lowercase, ascii_uppercase
ALPHABET = list(ascii_uppercase)

SUFFIX_OPTIONS = {
    'mc':"\nAnswer by writing the option letter corresponding to the correct option. WRITE ONLY A SINGLE LETTER. \n\nCorrect Answer: ",
    'explain_answer': "\nBegin by explaining your reasoning in 2-3 sentences, enclosed in quotes. After your explanation, select and state the correct answer by writing 'Correct Answer: ' followed by your choice. BEGIN WITH YOUR EXPLANATION AND WRITE THE CORRECT ANSWER AT THE END",
    'explanation': "\nBegin by explaining your reasoning in 2-3 sentences, enclosed in quotes. DO NOT WRITE THE CORRECT ANSWER, ONLY EXPLAIN YOUR REASONING.",
}


#########################################################################################
##                                                                                     ##
##                                                                                     ##
##                                                                                     ##
##                            Generate Question Code                                   ##
##                                                                                     ##
##                                                                                     ##
##                                                                                     ##
#########################################################################################


'''
input: 
- answer: str -- letter associated with the correct answer in the original ordering
- permutation: list -- list that was used to permute the options for inference
'''
def reverse_permutation_answer(answer, permutation):
    letters = list(ascii_lowercase)
    try:
        return letters[permutation[letters.index(answer.lower())]].upper()
    except IndexError:
        return answer

def reconstruct_context(prefix, outputs, questions):
    return prefix + '\n' + '\n'.join([question + '\n' + output for output, question in zip(outputs, questions)])

def shuffle_and_permute_options(options):
    """
    Shuffle the options DataFrame conditioned on a question_id

    Args:
        options (pd.DataFrame): DataFrame containing options for a specific question.

    Returns:
        pd.DataFrame, list: the shuffled options DataFrame and a permutation
    """
    options_shuffled = options.sample(frac=1)  # Shuffle options
    permutation = options_shuffled.option_id.tolist()  # Get the permutation
    return options_shuffled, permutation

def permute_answer(model_answers, permutations):
    def reshape_alphabet():
        new_2d = []
        index = 0  # To keep track of the current position in the alphabet

        for permutation in permutations:
            # Take the next slice from one_d_list of length equal to the length of the current row
            new_row = ALPHABET[index:index + len(permutation)]
            new_2d.append(new_row)
            index += len(permutation)  # Move the index

        return new_2d

    # reshape alphabet into options shape
    options_list = reshape_alphabet()
    # permute reshaped alphabet
    permuted_options = [options_list[permutation] for permutation in permutations]
    # get index of model output in permuted reshaped alphabet
    permuted_indices = [permuted_options.index(model_answer) for model_answer in model_answers]
    
    return permuted_indices




def build_options_string(options, start_index):
    """
    Construct a string representing question options with global labels, and return updated global option index.

    Args:
        options (pd.DataFrame): DataFrame containing options for a specific question.
        alphabet (str): String containing the alphabet used for labeling options.
        start_index (int): Starting index for global option labeling.

    Returns:
        str, int: A string of options labeled with globally unique characters from the alphabet,
                  and the updated global option index after processing these options.
    """
    options_str = ""
    for i, option in enumerate(options.itertuples(), start=start_index):
        label = ALPHABET[i % len(ALPHABET)]
        options_str += f"{label}. {option.option_text}  \n"
    updated_global_option_index = start_index + len(options)
    return options_str.strip(), updated_global_option_index

def format_question(question_text, options_str, params):
    """
    Format a question and its options based on specified parameters.

    Args:
        question_text (str): The text of the question.
        options_str (str): Formatted options string.
        params (dict): Parameters for formatting the question.

    Returns:
        list: A list containing formatted question strings.
    """
    question_type = params.get('question_type', 'mc')  # Default to 'mc' if not specified
    question_variants = []

    if question_type == 'mc' or question_type == 'mc-separate':
        suffix = SUFFIX_OPTIONS.get('mc')
        question_variants.append(f"{question_text}  \n{options_str}  \n{suffix}")
    elif question_type == 'simultaneous':
        suffix = SUFFIX_OPTIONS.get('explain_answer')
        question_variants.append(f"{question_text}  \n{options_str}  \n{suffix}")
    elif question_type == 'sequential-shown':
        suffix = SUFFIX_OPTIONS.get('explanation')
        question_variants.append(f"{question_text}  \n{options_str}  \n{suffix}")
        suffix = SUFFIX_OPTIONS.get('mc')
        question_variants.append(f"{options_str}  \n{suffix}")
    elif question_type == 'sequential-hidden':
        suffix = SUFFIX_OPTIONS.get('explanation')
        question_variants.append(f"{question_text}\n{suffix}")
        suffix = SUFFIX_OPTIONS.get('mc')
        question_variants.append(f"{options_str}\n{suffix}")
    else:
        suffix = SUFFIX_OPTIONS.get('mc')
        question_variants.append(f"{question_text}  \n{options_str}  \n{suffix}")
    

    return question_variants

def get_test_questions(q_id, questions_df, options_df, params):
    """
    Generate formatted test questions and their options based on specified parameters, including permutations of options.

    Args:
        q_id (str): Base question ID used to filter related questions.
        questions_df (pd.DataFrame): DataFrame containing question details.
        options_df (pd.DataFrame): DataFrame containing option details for questions.
        params (dict): Dictionary containing parameters for question formatting.
                       Expected keys are:
                       - 'question_type': Specifies the format of the questions and options.

    Returns:
        list, list: A tuple containing two lists:
                    - A list of formatted test questions including their options, modified based on 'question_type'.
                    - A list of permutations used for each question's options.
    
    Each question's options are permuted randomly, and the permutation is returned along with the formatted questions.
    """
    
    related_questions = questions_df[questions_df['question_id'].str.startswith(f"{q_id}_")]
    test_questions = []
    options_permutations = []  # To track permutations of options for each question
    global_option_index = 0

    for _, question in related_questions.iterrows():
        question_id = question['question_id']
        question_text = question['question_text']
        options = options_df[options_df['question_id'] == question_id]
        
        # Shuffle options and generate permutation
        options, permutation = shuffle_and_permute_options(options)
        options_str, updated_global_option_index = build_options_string(options, global_option_index)
        
        # Update global option index
        global_option_index = updated_global_option_index

        # Store the permutation
        options_permutations.append(permutation)

        formatted_question = format_question(question_text, options_str, params)
        test_questions.extend(formatted_question)

    return test_questions, options_permutations

# TODO: need to add logic for question_type
def build_question_string(base_id, questions_df, options_df):
    # Filter questions that start with the base_id
    related_questions = questions_df[questions_df['question_id'].str.startswith(f"{base_id}_")]
    
    full_question_string = ""
    # Alphabet for labeling options globally
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    global_option_index = 0 # Start global option index
    
    for _, question in related_questions.iterrows():
        question_id = question['question_id']
        question_text = question['question_text']
        
        # Find the options for this question
        options = options_df[options_df['question_id'] == question_id].sort_values(by='option_id')
        
        # Building the options string with global indexing
        options_str = ""
        for _, option in options.iterrows():
            label = alphabet[global_option_index % len(alphabet)] # Use modulo to cycle through alphabet if needed
            options_str += f"{label}. {option['option_text']}\n"
            global_option_index += 1 # Increment global index
        
        # Building the question string
        question_string = f"{question_text}\n{options_str.strip()}\n\n"
        
        # Append this question and its options to the full string
        full_question_string += question_string
    
    return full_question_string.strip()

def build_prefix_string():
    x= 10