#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
To create this script, I used this prompt for boilerplate code (copying in sample rows from the dataset):

using this column (here are the first two rows, each row representing an academic paper)

[['Ilker Yildirim', 'Max H. Siegel', 'Amir A. Soltani', 'Shraman Ray Chaudhari', 'Joshua B. Tenenbaum'],
['Asadullah Hill Galib', 'Bidhan Bashyal']]

write a function to create a gephi edge dataset where each node is an author and each edge represents a paper that the two authors have worked on together (in the same list)
'''

import pandas as pd
from tqdm import tqdm
import os
import ast
from collections import defaultdict

base_dir = 'your path here /outputs'
nodes_df_path = os.path.join(base_dir, 'title_text_similarity_graph_network/nodes_classified.csv')
# set export paths
nodes_export_path = os.path.join(base_dir, 'authors_graph_network', 'nodes.csv')
edges_export_path = os.path.join(base_dir, 'authors_graph_network', 'edges.csv')

# iterate over a list of papers, creating a list of unique author pairs (edges) from each paper
def create_gephi_edge_dataset(papers):
    edges = []
    for paper in tqdm(papers):
        authors = len(paper)
        for i in range(authors):
            for j in range(i + 1, authors):
                edge = (paper[i], paper[j])
                edges.append(edge)
    return edges

# read in the nodes dataset
df = pd.read_csv(nodes_df_path)
# if authors column items are strings, convert to lists
df['authors'] = df['authors'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

edge_dataset = create_gephi_edge_dataset(df['authors'])
edge_dataset = pd.DataFrame(edge_dataset, columns=['Source', 'Target'])

# create a list of unique authors (no duplicates)
unique_authors = list(set([item for sublist in df['authors'].to_list() for item in sublist]))

# create a node dataset
node_dataset = pd.DataFrame(unique_authors, columns=['authors'])
# add a UID to each author (so that the edge dataset can use UIDs instead of author names)
node_dataset['Id'] = node_dataset.index
node_dataset = node_dataset.rename(columns={'authors': 'Label'})
# create dict where key is author and value is UID
node_dataset_dict = dict(zip(node_dataset['Label'], node_dataset['Id']))

# replace edge_dataset with UIDs
edge_dataset['Source'] = edge_dataset['Source'].apply(lambda x: node_dataset_dict[x])
edge_dataset['Target'] = edge_dataset['Target'].apply(lambda x: node_dataset_dict[x])

'''
To create the next set of code, I used this prompt to generate the boilerplate code:

find most often published topic for each author using authors (list of authors) and classified_topic (string) columns in a pandas dataframe

example of row in authors column
['Ilker Yildirim', 'Max H. Siegel', 'Amir A. Soltani', 'Shraman Ray Chaudhari', 'Joshua B. Tenenbaum']

classified_topic cell in the same row
Computer Vision and Image Processing
'''

# create a dictionary where each author is a key
author_topics = defaultdict(lambda: defaultdict(int))

# Iterate through each row in the DataFrame
for _, row in tqdm(df.iterrows()):
    authors = row['authors']
    topic = row['classified_topic']
    # Update topic count for each author
    for author in authors:
        author_topics[author][topic] += 1

# Determine the most published topic for each author
most_published_topics = {}
for author, topics in tqdm(author_topics.items()):
    most_published_topic = max(topics, key=topics.get)
    most_published_topics[author] = most_published_topic

# add most_published_topic column to node_dataset
node_dataset['most_published_topic'] = node_dataset['Label'].apply(lambda x: most_published_topics[x])

# export (check if path exists for node and edge datasets)
if not os.path.exists(os.path.dirname(nodes_export_path)):
    os.makedirs(os.path.dirname(nodes_export_path))
if not os.path.exists(os.path.dirname(edges_export_path)):
    os.makedirs(os.path.dirname(edges_export_path))

node_dataset.to_csv(nodes_export_path, index=False)
edge_dataset.to_csv(edges_export_path, index=False)

# # make one more edge dataset where the edge weight is the number of times the two authors have worked together
# edge_dataset_weighted = edge_dataset.copy()
# edge_dataset_weighted['Weight'] = 1
# edge_dataset_weighted = edge_dataset_weighted.groupby(['Source', 'Target']).sum().reset_index()
# edge_dataset_weighted.to_csv(os.path.join(base_dir, 'authors_graph_network', 'edges_weighted.csv'), index=False)
