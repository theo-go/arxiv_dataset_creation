# Overview

1. As a heads up, there is a well-maintained repo for a Python wrapper for arXiv API [here](https://github.com/lukasschwab/arxiv.py). I've written this just to show how you can use Googling and ChatGPT to quickly write up scripts to do things 👍 
2. But if you're interested in using ChatGPT to write code to fetch data from the arXiv API, then read on!

## Steps
**1. Research how to use the API**
> **Google search:** "arxiv api python"

Here's some of the information I found: 

Because of speed limitations in our implementation of the API, the maximum number of results returned from a single call (max_results) is limited to 30000 in slices of at most 2000 at a time, using the max_results and start query parameters. For example to retrieve matches 6001-8000: http://export.arxiv.org/api/query?search_query=all:electron&start=6000&max_results=8000

[Link to API rate limiting](https://info.arxiv.org/help/api/user-manual.html#3112-start-and-max_results-paging)

[Link to API requests with Python](https://info.arxiv.org/help/api/basics.html#python)

**<br> 2. Create a query to loop through to get all the papers**

> **ChatGPT-4 prompt:** "write a url api request to get all articles from
https://arxiv.org/list/cs.AI/2309
> 
> based on this documentation: https://info.arxiv.org/help/api/user-manual.html#Quickstart"

**<br>3. Test the query**
> [**Postman:**](https://www.postman.com/) copy paste the url from ChatGPT into the search bar and hit send

- Test a query that I know won't return results to see what the error response looks like

**<br>4. Copy paste the results from Postman to ChatGPT to write parsing code**
> **ChatGPT-4 prompt:** "write python function to parse the following results from the api request. Return a JSON <br><br>(paste Postman results here)"

**<br>5. Get setup.**

Open up ChatGPT in one window and an IDE in the other. The IDE should have a Python interpreter and a nice data viewer and the ability to run code line by line.
- [**Spyder**](https://www.spyder-ide.org/) is a good option
- [**PyCharm**](https://www.jetbrains.com/pycharm/) is another good option
- [**VSCode**](https://code.visualstudio.com/) is a good option but requires a bit more setup (youtube or Medium have good tutorials)

Make sure to set up a hotkey to run the current line of code in the IDE. (chatgpt or google this 👍) For example, I use alt+enter. It'll save you a lot of time.


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
> (copy your postman results here)

**7. Test the code**
- After running the code copied from the last prompt into the IDE line by line (I skipped the while loop line so I could just see how the code was running), I saw that I wasn't getting any results. 
- Therefore, I typed into ChatGPT "I'm not getting any results."
- When I copied the change into the script, it fixed the issue 👍
- To understand more, I typed into ChatGPT
> explain the change you just made and how it works, explaining all terms that a beginner coder would need to understand as well, explaining like you're talking to a high school student

- I played the code through in my head and saw an issue where the "current_start" variable was not being set to 0 for the next date range in the loop so I added an "else" to the "if more results.. continue" statement
- I also noticed that we weren't pausing according to the rate limiting that the API has so I added a time.sleep(3) to the loop
- I also prompted ChatGPT to add export lines to the code to export as a csv and json file and added these lines into my script
- Anddd a progress bar! Just asked *"how to add progress bar to while loop"* and copied the code into my script

**<br>8. Run the code**
- I selected all the code and ran it (you can also find the green triangle play button in an IDE to run the whole script). 

And that's it! I now have a script that will loop through every 10 days from the last day of 2022 to the first day of 2024 and get all the papers from the arXiv API and export them as a csv and json file.


