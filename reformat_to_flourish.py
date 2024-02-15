#!/usr/bin/env python3
# coding: utf-8

# Import necessary libraries
import pandas as pd
import ast

df_path = 'full nodes_classified.csv path'
export_path = df_path.replace('.csv', '_weekly.csv')
start_date = '2023-01-01'
end_date = '2023-12-31'

# Load the dataset
df = pd.read_csv(df_path, encoding='latin-1')

# Select only the relevant columns
cols_keep = ['published', 'Label', 'classified_topic']
df = df[cols_keep]

# Convert the 'published' column to datetime format and sort by date
df['published'] = pd.to_datetime(df['published'])
df = df.sort_values('published')

# Filter the dataframe to include only the data from 2023
df = df[(df['published'] >= start_date) & (df['published'] <= end_date)]

# Extract week numbers and adjust the first week of the year
df['Week_Number'] = df['published'].dt.isocalendar().week
# Fix issue where first week of year is recorded as 52
df['Week_Number'] = df.apply(lambda row: 1 if row['published'].date() == pd.Timestamp('2023-01-01').date() else row['Week_Number'], axis=1)


# Remove duplicate entries
df = df.drop_duplicates(subset=['Label', 'Week_Number'])

# Pivot the data for analysis
pivot_df = df.pivot(index='Label', columns='Week_Number', values='classified_topic')

# Prepare for weekly aggregation
weeks = pd.date_range(start='01-01-2023', periods=52, freq='W').strftime('%Y-%m-%d')
topics = df['classified_topic'].unique()
weekly_counts_df = pd.DataFrame(index=topics, columns=weeks)

# Step 2: Iterate through each week
for week in weeks:
    week_date = pd.to_datetime(week)
    year = week_date.year
    week_number = week_date.week
    # Filter dataframe for papers published up to the current week
    papers_up_to_week = df[pd.to_datetime(df['published']).dt.date <= week_date.date()]  # Convert Timestamp to datetime.date
    # Group by classified_topic and count the number of papers published
    weekly_counts = papers_up_to_week.groupby('classified_topic').size()
    # Fill the corresponding cells in the dataframe with the cumulative counts
    weekly_counts_df[week] = weekly_counts

# Step 3: Fill NaN values with 0
weekly_counts_df = weekly_counts_df.fillna(0)

# Step 4: Save the dataframe to a CSV file
weekly_counts_df.to_csv('G:/My Drive/Non-freelance/VAST - A Currency of Ideas/Pantheon Master Folder/Pantheon Projects Master/AIDEN folder/arxiv_paper/data_outputs/api_returned_data/results_datetime.csv', index=True, encoding='utf-8-sig')






# do it again for categories
df = pd.read_csv(df_path, encoding='latin-1')

cols_keep = ['published', 'categories']

df = df[cols_keep]
# make 'categories' into a list
import ast
df['categories'] = df['categories'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

# explode categories into mutliple rows
df = df.explode('categories')

# merge with full names
abbrev = pd.read_csv('G:/My Drive/Non-freelance/VAST - A Currency of Ideas/Pantheon Master Folder/Pantheon Projects Master/AIDEN folder/arxiv_paper/data_outputs/api_returned_data/categories_arxiv.csv')
# clean \xa0
abbrev['abbreviation'] = abbrev['abbreviation'].apply(lambda x: x.replace('\xa0', ''))
# trim
abbrev['abbreviation'] = abbrev['abbreviation'].apply(lambda x: x.strip())
# drop dups
abbrev = abbrev.drop_duplicates(subset=['abbreviation'])

df = df.merge(abbrev, left_on='categories', right_on='abbreviation', how='left')

# drop nan in title col
df = df.dropna(subset=['title'])

# drop anything with cs.
df_no_cs = df[~df['categories'].str.contains('cs.')]

df = df_no_cs.copy()

# drop unneeded cols
df = df.drop(columns=['categories', 'abbreviation'])

# Convert 'published' column to datetime
df['published'] = pd.to_datetime(df['published'])
# sort by earliest date
df = df.sort_values('published')

weeks = pd.date_range(start='01-01-2023', periods=52, freq='W').strftime('%Y-%m-%d')




# Step 1: Create an empty dataframe
topics = df['title'].unique()
weekly_counts_df = pd.DataFrame(index=topics, columns=weeks)

# Aggregate data on a weekly basis
for week in weeks:
    week_date = pd.to_datetime(week)
    papers_up_to_week = df[pd.to_datetime(df['published']).dt.date <= week_date.date()]
    weekly_counts = papers_up_to_week.groupby('title').size()
    weekly_counts_df[week] = weekly_counts

weekly_counts_df.fillna(0, inplace=True)
weekly_counts_df.to_csv(export_path, index=True, encoding='utf-8-sig')
