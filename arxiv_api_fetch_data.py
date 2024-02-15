#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports
import urllib
import urllib.request
import xml.etree.ElementTree as ET
import json
from datetime import datetime, timedelta
from time import sleep
import pandas as pd
from tqdm import tqdm  # Import tqdm for progress bar
import os

# Base directory (assuming this script is in the main project directory)
base_dir = 'add your path here'  # os.path.dirname(os.path.abspath(__file__))

# Query the API for papers within the specified date range at increments of 10 days
start_date = datetime(2022, 12, 31)
end_date = datetime(2024, 1, 1)
days_to_increment = 10
# Start index for pagination (within each 10-day interval, the API returns up to 2000 results.
# If there are more results, we need to paginate) and use current_start to keep track of the index
current_start = 0
# Initialize an empty list to store the results
results = []

# Create and define the path to the outputs directory
if not os.path.exists(os.path.join(base_dir, 'outputs')):
    os.makedirs(os.path.join(base_dir, 'outputs'))
outputs_dir = os.path.join(base_dir, 'outputs')
# Export paths for the CSV and JSON output files
csv_output_file_name = os.path.join(outputs_dir, 'results.csv')
json_output_file_name = csv_output_file_name.replace('.csv', '.json')

# Calculate the total number of date combinations
total_date_combinations = (end_date - start_date).days // days_to_increment + 1  # 10-day intervals
# Initialize tqdm progress bar which will update after each data fetch
pbar = tqdm(total=total_date_combinations, desc='Progress', unit=' intervals')

# Define the namespace for XML parsing (a shortcut list for identifying parts of the XML tree (what we are looking for))
namespace = {'atom': 'http://www.w3.org/2005/Atom', 'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'}


# Define a function to send API requests and handle pagination
def send_api_request(start_date, end_date, current_start):
    # Define the base URL for the arXiv API
    base_url = 'https://export.arxiv.org/api/query?search_query=cat:cs.AI+AND+submittedDate:[{}+TO+{}]&start={}&max_results=2000&sortBy=submittedDate&sortOrder=descending'
    # Construct the URL for the API request
    url = base_url.format(start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d'), current_start)
    # Send the request and read the response
    data = urllib.request.urlopen(url)
    # Return the response data
    return data.read().decode('utf-8')


# Loop through every x days (defined by days_to_increment)
while start_date < end_date:
    # Create a temporary end date for the current 10-day interval
    end_date_tmp = start_date + timedelta(days=days_to_increment)

    # Send API request
    response_xml = send_api_request(start_date, end_date_tmp, current_start)

    # Parse the XML response
    root = ET.fromstring(response_xml)
    # Get the total number of results, if there are more than 2000, we need to paginate
    total_results = int(root.find(".//opensearch:totalResults", namespaces=namespace).text)

    # Loop through each entry in the XML response and extract the data
    for entry in root.findall(".//atom:entry", namespaces=namespace):
        entry_dict = {
            "id": entry.find("atom:id", namespaces=namespace).text,
            "updated": entry.find("atom:updated", namespaces=namespace).text,
            "published": entry.find("atom:published", namespaces=namespace).text,
            "title": entry.find("atom:title", namespaces=namespace).text,
            "summary": entry.find("atom:summary", namespaces=namespace).text,
            "authors": [author.find("atom:name", namespaces=namespace).text for author in
                        entry.findall(".//atom:author", namespaces=namespace)],
            "categories": [category.attrib["term"] for category in
                           entry.findall(".//atom:category", namespaces=namespace)]
        }
        results.append(entry_dict)

    # Sleep for 3 seconds to respect the API rate limit
    sleep(3)
    # Increment the start index for pagination
    current_start += 2000
    # Check if there are more results to fetch (i.e. if more than 2000 results were returned)
    if current_start < total_results:
        # if total_results is greater than 2000, we use continue to loop and fetch the same date range
        # but with the next 2000 results
        continue
    else:
        # If there are no more results, reset the start index for the next 10-day interval
        current_start = 0

    # Move to the next 10-day interval
    start_date = end_date_tmp
    # Update the progress bar
    pbar.update(1)

# Close the progress bar when the loop is finished
pbar.close()

# Create a DataFrame from the results
df = pd.DataFrame(results)
# if the output path doesn't exist, create it
if not os.path.exists(os.path.dirname(csv_output_file_name)):
    os.makedirs(os.path.dirname(csv_output_file_name))

# Export the DataFrame to a CSV file
df.to_csv(csv_output_file_name, index=False, encoding='utf-8')
# Convert results to JSON
output_json = json.dumps(results, indent=4)
# Export the JSON data to a text file
with open(json_output_file_name, 'w') as json_file:
    json_file.write(output_json)
