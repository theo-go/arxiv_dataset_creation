# Overview

> As a heads up, there is a well-maintained repo for a Python wrapper for arXiv API [here](https://github.com/lukasschwab/arxiv.py). 
> 
> I've written this just to show how you can Google + ChatGPT your way to quickly writing up scripts 👍

## Steps
**1. Research how to use the API**
> **Google search:** "arxiv api python"

From the search, I found some information that will inform how we're going to write the script.

*Because of speed limitations in our implementation of the API, the maximum number of results returned from a single call (max_results) is limited to 30000 in slices of at most 2000 at a time, using the max_results and start query parameters. For example to retrieve matches 6001-8000: http://export.arxiv.org/api/query?search_query=all:electron&start=6000&max_results=8000*

- [Google result about arXiv API rate limiting](https://info.arxiv.org/help/api/user-manual.html#3112-start-and-max_results-paging)
- [Result about using arXiv API requests with Python](https://info.arxiv.org/help/api/basics.html#python)

**<br> 2. Create a query to loop through to get all the papers**

> **ChatGPT-4 prompt:** "write a url api request to get all articles from
https://arxiv.org/list/cs.AI/2309
> 
> based on this documentation: https://info.arxiv.org/help/api/user-manual.html#Quickstart"

**<br>3. Test the query from ChatGPT**
> [**Using Postman (link here):**](https://www.postman.com/) copy paste the url from ChatGPT into the search bar and hit send

- Also, I tested a query that I know won't return results to see what the error response looks like

**<br>4. Copy paste the results from Postman to ChatGPT to write the code to parse results**
> **ChatGPT-4 prompt:** "write python function to parse the following results from the api request. Return a JSON <br><br>***(paste Postman results here)***

**<br>5. Get setup with your IDE.**

Open up your LLM of choice (e.g. ChatGPT, Copilot (which runs inside VSCode, Pycharm), etc. Or wait for Bard to continue rebranding lol) in one window and an IDE in the other 😎 I prefer an IDE that has a Python interpreter window, an accessible data viewer, and the ability to run code line by line.
- [**PyCharm**](https://www.jetbrains.com/pycharm/) (free for students, otherwise paid)
- - [**VSCode**](https://code.visualstudio.com/) (free, easy to setup (watch a youtube video/medium article if needed))
- [**Spyder**](https://www.spyder-ide.org/) always shoutout to Spyder, near and dear to my heart

Make sure your IDE is set up to run the current line of code with a hotkey. (chatgpt or google this 👍) For example, I use alt+enter. It's nice to have.


**<br>6. Write the code.**
> **ChatGPT-4 prompt:** "write a python script that will loop through every 10 days from the last day of 2022 to the first day of 2024 using this api request code
>
> 
> ```
> url = 'http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1'
> data = urllib.request.urlopen(url)
> print(data.read().decode('utf-8'))
> ```
> but replace the url string with this one:
> https://export.arxiv.org/api/query?search_query=cat:cs.AI+AND+submittedDate:[20230901+TO+20230905]&start=0&max_results=2000&sortBy=submittedDate&sortOrder=descending
>
> if the returned text says that there were more than 1999 results, then change the start to 2000 in the url string until there are none left
> 
> finally parse the xml results into a json 
> an example of the returned results are here
> 
> ***(copy your postman results here)***

**7. Test the code**
- After running the code copied from the last prompt into the IDE line by line (skip any for/while loops so you can just see how the code runs), I saw that I wasn't getting any results. 
- Therefore, I typed into ChatGPT `"I'm not getting any results."`
- Copied the change into the script -> it fixed the issue 👍
- To understand more, you can type into ChatGPT:
> explain the change you just made and how it works, explaining all terms that a beginner coder would need to understand as well, explaining like you're talking to a beginnger Python student
- Now, I read through the code and made some changes:
- Fixed issue where the "current_start" variable was not being reset for the next date range in the loop.
- Added pauses to respect API rate limits.
- Prompted ChatGPT to add export functionality (csv and json).
- Added progress bar (Chatgpt `"how to add progress bar to while loop"`).

**<br>8. Run the code**
- Select all the code and run it or find the green triangle play button.

