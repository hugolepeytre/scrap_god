# Scrap God

## Requirements

Requirements are listed in [requirements.txt](requirements.txt). The other requirement is to be able to run Jupyter Notebooks.

## How to run

Since the CSV file and visualisations are already generated, there is no need to actually run the code, expect to check that it works. To do that, there are 2 important files :
- [scrap_gods.py](scrap_gods.py) generates the csv file (gods.csv). It runs in about 10 minutes, 99% of the time being taken to fetch god pages. Run with `python scrap_gods.py`
- [visualisation.ipynb](visualisation.ipynb) is a Jupyter notebook (already evaluated) which contains the data exploration and insights. Simply open it using jupyter-notebook and run all the cells


## Scraping

Scraping is done in [scrap_gods.py](scrap_gods.py) 
The scraping process goes as follows :
First collect all pantheon pages since they contain the lists of gods. They are all listed in the main page, except the Modern Pantheon which was added by hand so we can simply collect all links and filter out the non-pantheon ones.

Then on every page, the list of gods is located in the element with class `text-bubble` so we can again collect all urls, filter out uninteresting ones and duplicates and request all the remaining pages.

Every page is transformed into a dictionnary entry containing all information from the Facts and Figures box (`vitalsbox` class in source code) as well as the current url and pantheon. Finally, we also collect all mentions of other gods in the description, as this can be relevant info later. Since there are some garbage urls and misspelled names we use a previously constructed url to name mapping defaulting all garbage data to the current god's name, which is then taken out.

Finally, we take the maximal set of dictionnary keys as our database's columns and store everything in a CSV file.

## Storage

For storage, I chose to use a simple CSV format instead of a more complicated SQL-like database. The reasons for this are :
- The data's structure is very simple, with almost no relational component. The only relational column is the references to other gods, and this is not enough to justify using a relational database.
- There is only about 1Mb worth of data, which can fit easily into a single CSV file
- This makes the whole thing self-contained in Python, which means less installation requirements as well as ease of use
- I assume our historian friend is much more likely to know some Python than any other language so he will not feel lost

I also added some functions in [visualisation.ipynb](visualisation.ipynb) to allow the user to make some simple requests to the database:
- `get_god`: Search a god by any of its names
- `get_related_gods`: Get all gods related to some god
- `gods_from_keyword`: Get all gods related to some keyword (e.g. Agriculture)

## Visualisation

Use pandas
