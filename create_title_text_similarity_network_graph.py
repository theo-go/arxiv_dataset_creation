#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import standard libraries
import os
import numpy as np
import pandas as pd

# Import NLP and ML libraries
import nltk
from nltk.corpus import stopwords
import faiss
import spacy
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
tqdm.pandas()
from joblib import Parallel, delayed

# Import parallel processing library
from pandarallel import pandarallel

# Import utility functions
from utils import process_text

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Initialize Pandarallel
pandarallel.initialize(progress_bar=True)

# Load spaCy model and merge stopwords from NLTK and spaCy
en = spacy.load('en_core_web_sm')
stop_list = set(stopwords.words('english') + list(en.Defaults.stop_words))

# Load Sentence Transformer model for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# Base directory and file paths setup
base_dir = 'add your path here'
outputs_dir = os.path.join(base_dir, 'outputs')
input_file_path = os.path.join(outputs_dir, 'results.json')
export_edge_file_path = os.path.join(outputs_dir, 'edges.csv')
export_node_file_path = os.path.join(outputs_dir, 'nodes.csv')
corpus_export_temp_path = os.path.join(outputs_dir, 'corpus_embeddings.csv')

# Data preprocessing
if not os.path.exists(corpus_export_temp_path):
    df = pd.read_json(input_file_path)
    df['title'] = df['title'].parallel_apply(process_text, args=(stop_list,))
    df['summary'] = df['summary'].parallel_apply(process_text, args=(stop_list,))

    corpus_sentences = df['title'].tolist()
    corpus_embeddings = model.encode(corpus_sentences, batch_size=64, show_progress_bar=True, convert_to_tensor=True)
    corpus_embeddings = corpus_embeddings.cpu().numpy()
    np.savetxt(corpus_export_temp_path, corpus_embeddings, delimiter=",")
else:
    corpus_embeddings = np.loadtxt(corpus_export_temp_path, delimiter=",")


def process_text(text, stop_list):
    import re
    from nltk.tokenize import word_tokenize

    # Use a single regex to remove numbers and punctuation, and normalize whitespace
    text = re.sub(r'\d+|[^\w\s]|[\r\n\t]| +', ' ', text)
    # Lowercase and tokenize the text
    tokens = word_tokenize(text.lower())
    # Filter out stop words
    filtered_tokens = [word for word in tokens if word not in stop_list]
    return " ".join(filtered_tokens)


# Normalize embeddings and create Faiss index
corpus_embeddings_normalized = corpus_embeddings / np.linalg.norm(corpus_embeddings, axis=1)[:, np.newaxis]
faiss_index = faiss.IndexFlatL2(corpus_embeddings_normalized.shape[1])
faiss_index.add(corpus_embeddings_normalized)


# Function to process each embedding (plug this into chatgpt/copilot etc to improve performance)
# This is written to maximize legibility for readers less familiar with network analysis
def process_embedding(i):
    # search across the corpus (the embeddings of the titles) for similar titles
    # distance is the similarity, indices are the index of the similar titles
    distances, indices = faiss_index.search(corpus_embeddings_normalized[i:i + 1], n)
    result = []
    # loop through the similar titles and add them to the result list if they are above our similarity threshold
    for j in range(1, n):
        source = i
        target = indices[0][j]
        similarity = 1 - distances[0][j]
        if similarity > threshold:
            result.append((source, target, similarity))
    return result

# Set the number of embeddings to process (in this case, shape[0] meaning all of the titles)
n = corpus_embeddings_normalized.shape[0]
# Set a similarity threshold (so our edge dataset doesn't get too big)
threshold = 0.3

# Using joblib to parallelize the computation
results = Parallel(n_jobs=-1)(delayed(process_embedding)(i) for i in tqdm(range(n), desc="Processing embeddings"))
flattened_results = [item for sublist in results for item in sublist]

# Convert results to a DataFrame
edge_df = pd.DataFrame(edges, columns=['Source', 'Target', 'Weight']).sort_values(by='Weight', ascending=False).drop_duplicates()
edge_df = edge_df[edge_df['Source'] != edge_df['Target']]
edge_df = edge_df.drop_duplicates(subset=['Source', 'Target'])
# Remove duplicate edges considering the order of nodes. For example, edge (A, B) is considered the same as (B, A).
# We create a temporary column 'Edge' that contains a sorted tuple of (Source, Target) to identify such duplicates.
edge_df['Edge'] = edge_df.apply(lambda row: tuple(sorted((row['Source'], row['Target']))), axis=1)
# Drop duplicate edges based on the 'Edge' column, then drop the 'Edge' column as it's no longer needed.
edge_df = edge_df.drop_duplicates(subset='Edge').drop(columns='Edge')
# Reset the DataFrame's index to ensure it's in sequential order after all the modifications.
edge_df = edge_df.reset_index(drop=True)

# Prepare the node dataset from df_untouched
node_df = df_untouched.copy()
node_df['Id'] = node_df.index  # Create Id column from index
node_df.rename(columns={'title': 'Label'}, inplace=True)  # Rename 'title' to 'Label'
# Reorder columns so that 'Id' and 'Label' are the first two columns
node_df = node_df[['Id', 'Label'] + [col for col in node_df.columns if col not in ['Id', 'Label']]]

# Export to CSV files
edge_df.to_csv(export_edge_file_path, index=False)
node_df.to_csv(export_node_file_path, index=False)

