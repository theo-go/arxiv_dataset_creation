#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import libraries
import pandas as pd
import nltk
import faiss
import spacy
import os
import numpy as np
from nltk.corpus import stopwords
from tqdm import tqdm
tqdm.pandas()
from joblib import Parallel, delayed
from pandarallel import pandarallel
from sentence_transformers import SentenceTransformer
# Download NLTK data (if not already downloaded)
nltk.download('punkt')
nltk.download('stopwords')
# Initialize Pandarallel for parallel processing
pandarallel.initialize(progress_bar=True)
# Load spaCy model and stopwords
en = spacy.load('en_core_web_sm')
spacy_stopwords = en.Defaults.stop_words
# Merge stopwords from NLTK and spaCy
stop_list = stopwords.words('english') + list(spacy_stopwords)
stop_list = list(set(stop_list))
# Load the Sentence Transformer model for sentence embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
# custom imports
from utils import process_text

# Base directory
base_dir = 'add your path here'  # os.path.dirname(os.path.abspath(__file__))

# Relative path to the outputs directory
outputs_dir = os.path.join(base_dir, 'outputs')
# Set variables with relative paths
input_file_path = os.path.join(outputs_dir, 'results.json')
export_edge_file_path = os.path.join(outputs_dir, 'edges.csv')
export_node_file_path = os.path.join(outputs_dir, 'nodes.csv')
corpus_export_temp_path = os.path.join(outputs_dir, 'corpus_embeddings.csv')

# Import, clean, and process data
df = pd.read_json(input_file_path)
df_untouched = df.copy()


if not os.path.exists(corpus_export_temp_path):
    df['title'] = df['title'].parallel_apply(process_text, args=(stop_list,))
    df['summary'] = df['summary'].parallel_apply(process_text, args=(stop_list,))

    corpus_sentences = df['title'].to_list()

    print("Encode the corpus. This might take a while")
    corpus_embeddings = model.encode(corpus_sentences, batch_size=64, show_progress_bar=True, convert_to_tensor=True)
    corpus_embeddings = corpus_embeddings.cpu().numpy()
    np.savetxt(corpus_export_temp_path, corpus_embeddings, delimiter=",")
else:
    corpus_embeddings = np.loadtxt(corpus_export_temp_path, delimiter=",")

# Normalize the embeddings
corpus_embeddings_normalized = corpus_embeddings / np.linalg.norm(corpus_embeddings, axis=1)[:, np.newaxis]

# Create Faiss index
vector_dimension = corpus_embeddings.shape[1]
faiss_index = faiss.IndexFlatL2(vector_dimension)
faiss_index.add(corpus_embeddings_normalized)


# Function to process each embedding
def process_embedding(i):
    distances, indices = faiss_index.search(corpus_embeddings_normalized[i:i + 1], n)
    result = []
    for j in range(1, n):  # Start from 1 to avoid self-similarity
        source = i
        target = indices[0][j]
        similarity = 1 - distances[0][j]  # Convert distance to similarity
        if similarity > threshold:  # Apply threshold
            result.append((source, target, similarity))
    return result

n = corpus_embeddings_normalized.shape[0]
threshold = 0.3  # Set your threshold

# Using joblib to parallelize the computation
results = Parallel(n_jobs=-1)(delayed(process_embedding)(i) for i in tqdm(range(n), desc="Processing embeddings"))
flattened_results = [item for sublist in results for item in sublist]

# Convert results to a DataFrame
edge_df = pd.DataFrame(flattened_results, columns=['Source', 'Target', 'Weight'])
edge_df = edge_df.sort_values(by=['Weight'], ascending=[False])
edge_df = edge_df[edge_df['Source'] != edge_df['Target']]
edge_df = edge_df.drop_duplicates(subset=['Source', 'Target'])
edge_df['sorted_columns'] = edge_df.apply(lambda x: tuple(sorted([x['Source'], x['Target']])), axis=1)
edge_df = edge_df.drop_duplicates(subset='sorted_columns', keep='first').drop(columns='sorted_columns')
edge_df = edge_df.reset_index(drop=True)

# create node dataset from df_untouched
node_df = df_untouched.copy()
# create Id column from index, starting at 0
node_df['Id'] = node_df.index
# change title to Label
node_df = node_df.rename(columns={'title': 'Label'})
# resort columns so Id and Label are first
node_df = node_df[['Id', 'Label', 'summary', 'authors', 'categories', 'published', 'updated', 'id']]

# Export the DataFrames to CSV files
edge_df.to_csv(export_edge_file_path, index=False)
node_df.to_csv(export_node_file_path, index=False)

