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

weekly_counts_df.fillna(0, inplace=True)
weekly_counts_df.to_csv(export_path, index=True, encoding='utf-8-sig')