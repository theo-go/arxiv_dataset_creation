# AI Publishing Trends Analysis Using ArXiv (2023)

## Overview
This project aims to generate analysis-ready datasets to understand trends in the AI publishing space in 2023. It involves fetching data from arXiv API, classifying published articles into custom topics, creating network graphs, and visualizing temporal trends.

## File Descriptions
1. **.env**: Contains environment variables and API keys necessary for the scripts. Use `envexample (rename to .env)` as a template.
2. **arxiv_api_fetch_data.py**: Script for fetching AI-related publication data from the arXiv API.
3. **create_title_text_similarity_network_graph.py**: Analyzes and visualizes the similarity between publication titles using network graphs.
4. **create_authors_network_graph.py**: This script generates datasets formatted for [Gephi network graphing](https://gephi.org/) based on the authors of the publications.
5. **classify_into_topics.py**: Python code to classify the fetched publications into various AI topics.
6. **reformat_to_flourish.py**: Reformats the data for visualization in [Flourish Studio](https://flourish.studio/).

> /2023_dataset_outputs/ is the directory where the output files are stored. If you're just interested in analyzing the data, you can directly use the files from this directory.

## Installation
- Ensure Python 3.8+ is installed.
- Install required packages: `pip install -r requirements.txt`
  - Note: The `requirements.txt` file uses `faiss-cpu` for similarity search. If you want to use GPU, you can install `faiss-gpu` instead.

## Usage
- Set the API keys in the `.env` file (you'll need to rename the `envexample` file to .env).
- Collect the data from the arXiv API by running `python arxiv_api_fetch_data.py`.
  - Note that there is a separate README file for the `arxiv_api_fetch_data.py` script with step-by-step instructions on how it was coded.
- Create the network graphs based on text similarity of titles using `python create_title_text_similarity_network_graph.py`.
- Classify the publications into topics using `python classify_into_topics.py`.
- Create the network graphs based on co-authoring using `python create_authors_network_graph.py`.
- Create datasets formatted for Flourish Studio's "racing bar charts" using `python reformat_to_flourish.py`.
> You've now generated the files needed to analyze the AI publishing trends for 2023!

## Notes
- Please note that the base directory should be manually set at the top of each script.

## Contributing
Contributions to the project are welcome. 

## License

This project is licensed under the Creative Commons Attribution-NonCommercial (CC BY-NC) license. This allows for the redistribution, modification, and use of this work non-commercially, as long as appropriate credit is provided and the new creations are licensed under identical terms. For commercial use, please contact the project owner.

For more details about this license, please visit [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).
