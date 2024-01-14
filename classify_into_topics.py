#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from time import sleep
import ast
from tqdm import tqdm
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Base directory
base_dir = 'add your path here'  # os.path.dirname(os.path.abspath(__file__))

# Relative path to the outputs directory
outputs_dir = os.path.join(base_dir, 'outputs')
# Relative path for nodes.csv
nodes_df_path = os.path.join(outputs_dir, 'nodes.csv')


def query_chatgpt(instruction_str, text_input):
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
            # temperature=0.5,
            # max_tokens=64,
            # top_p=1
        )

        # print the chat completion
        returned_content = chat_completion.choices[0].message.content
        sleep(2)
        return returned_content
    except Exception as e:
        print(e)
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
number_of_titles_to_pass_in = 40

total_length = len(title_list)
# pass in groups of ten
for i in range(0, len(title_list), number_of_titles_to_pass_in):
    try:
        text_input = title_list[i:i + number_of_titles_to_pass_in]
        returned_content = query_chatgpt(instruction_str, str(text_input))
        returned_content = ast.literal_eval(returned_content)
        classified_titles.append(returned_content)

        # Calculate and print the completion percentage
        percentage_complete = (i / total_length) * 100
        print(f"Progress: {percentage_complete:.2f}%")
    except Exception as e:
        print(e)
        sleep(2)
        continue


classified_titles_flat = [item for sublist in classified_titles for item in sublist]
# drop any elements with more than 2 elements and handle TypeError: object of type 'ellipsis' has no len()
classified_titles_flat = [x for x in classified_titles_flat if isinstance(x, tuple) and len(x) == 2]

classified_titles_dict = dict(classified_titles_flat)

# check any errors in the returned topics (improvisation from gpt...)
# # unique topics
# unique_topics = list(set(df['classified_topic'].tolist()))
#
# # export topics
# topics_df = pd.DataFrame(unique_topics, columns=['topics'])
# # count usage of each topic in df['classified_topic']
# topics_df['count'] = topics_df['topics'].apply(lambda x: df['classified_topic'].tolist().count(x))
# topics_df.to_csv('C:/Users/tgoet/Documents/GitHub/collect_tannya_papers/arxiv_scrape/outputs/topics.csv', index=False)

classified_titles_df = pd.DataFrame(classified_titles_dict.items(), columns=['title', 'topics'])

# read in topics mapped (fix erroneous topics)
topics_df = pd.read_csv(os.path.join(base_dir, 'outputs', 'topics_mapped.csv'))

# replace topics in classified_titles_df with the correct topics
classified_titles_df = pd.merge(classified_titles_df, topics_df, how='left', on=['topics'])
classified_titles_df = classified_titles_df.drop(columns=['topics'])
classified_titles_df = classified_titles_df.rename(columns={'fix': 'topics'})
df = pd.merge(df, classified_titles_df, how='left', left_on=['Label'], right_on=['title'])
df = df.drop(columns=['title'])
df = df.rename(columns={'topics': 'classified_topic'})

# export to csv
df.to_csv(nodes_df_path.replace('.csv', '_classified.csv'), index=False)
