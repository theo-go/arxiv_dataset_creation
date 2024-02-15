#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pandas as pd
from time import sleep
import ast
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv

# Load the OpenAI API key from the .env file
load_dotenv()
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Base directory
base_dir = 'add your path here'  # os.path.dirname(os.path.abspath(__file__))
# Path to the outputs directory
outputs_dir = os.path.join(base_dir, 'outputs')
# Path to the nodes.csv previously created with `create_title_text_similarity_network.py`
nodes_df_path = os.path.join(outputs_dir, 'nodes.csv')
export_path = nodes_df_path.replace('.csv', '_classified.csv')


def query_chatgpt(instruction_str, text_input):
    # Check if the input is empty (less than 6 characters)
    if len(text_input) < 6:
        return ''
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": instruction_str
            },
                {
                    "role": "user",
                    "content": text_input
            }],
            temperature=0.5,
            # max_tokens=64,
            # top_p=1
        )

        # print the chat completion
        returned_content = chat_completion.choices[0].message.content
        sleep(2)
        return returned_content
    except Exception as e:
        print("Error:", e)
        sleep(10)
        return ''


topics = [
    'Large Language Models and Natural Language Processing',
    'Machine Learning Algorithms and Theoretical AI',
    'Healthcare and Biomedical Applications of AI',
    'Computer Vision and Image Processing',
    'Robotics, Autonomous Systems, and Control',
    'Data Science and Analytics',
    'AI in Education, Art, and Creative Industries',
    'AI Ethics, Society, and Policy',
    'Emerging Technologies and Future Trends in AI',
    'Sustainability and Environmental Applications of AI',
    'Cybersecurity and Information Security with AI',
    'Human-Computer Interaction and User Experience',
    'AI in Social Sciences and Humanities',
    'Quantum Computing and AI',
    'AI for Industrial Automation and Manufacturing'
]

instruction_str = f"""
Given the list of topics pick the one that best classifies the following paper titles.
Return your answers in a list of tuples, where the first element of the tuple is the paper title and the second element is the topic you think it best belongs to.\
Do not change the name of the titles or the topics.
List of topics: {topics}

List of paper titles:
"""


df = pd.read_csv(nodes_df_path)
title_list = df['Label'].tolist()
classified_titles = []
# send article titles in groups of x
number_of_titles_to_pass_in = 40

# get the total number of titles to calculate the progress
total_length = len(title_list)
for i in range(0, len(title_list), number_of_titles_to_pass_in):
    try:
        text_input = title_list[i:i + number_of_titles_to_pass_in]
        returned_content = query_chatgpt(instruction_str, str(text_input))
        # see articles on ensuring JSON consistency of OpenAI API responses as well as more recent openAI models
        # if the returned content is malformed, this script just prints the error and continues
        # room for improvement here
        returned_content = ast.literal_eval(returned_content)
        classified_titles.append(returned_content)

        # Calculate and print the completion percentage
        percentage_complete = (i / total_length) * 100
        print(f"Progress: {percentage_complete:.2f}%")
    except Exception as e:
        print(e)
        sleep(2)
        continue

# flatten the list of lists
classified_titles_flat = [item for sublist in classified_titles for item in sublist]
# drop any elements with more than 2 elements and handle TypeError: object of type 'ellipsis' has no len()
classified_titles_flat = [x for x in classified_titles_flat if isinstance(x, tuple) and len(x) == 2]
classified_titles_dict = dict(classified_titles_flat)
# create a dataframe from the dictionary
classified_titles_df = pd.DataFrame(classified_titles_dict.items(), columns=['title', 'topics'])
# merge nodes dataframe with classified_titles_df
df = pd.merge(df, classified_titles_df, how='left', left_on=['Label'], right_on=['title'])
df = df.drop(columns=['title'])
df = df.rename(columns={'topics': 'classified_topic'})

# export to csv
df.to_csv(export_path, index=False)
