# Kickstarter Project (COMP3354)

## Dataset
The raw data file `kickstarter_data_raw.json` was downloaded from: https://webrobots.io/kickstarter-datasets/
The raw file is a 1GB+ and contains just over 200,000 lines, each with its own json object representing a webscrabe request.

The cleaned data file `kickstarter_data_final.csv` is the process of running all step of `clean_data.py` on the raw dataset.

`python clean_data.py 1` executes step 1 and produces `kickstarter_data_transformed.csv`. This step translates the raw data into a csv file and removes scraping metadata. This step is quite slow and may take 1-2 hours to execute.

`python clean_data.py 2` executes step 2 and produces `kickstarter_data_transformed.csv`. This step which drops all obviously useless columns.

`python clean_data.py 3` executes step 3 and produces `kickstarter_data_pruned.csv`. This step generates new potentially useful columns based on existing columns.

`python clean_data.py 4` executes step 4 and produces `kickstarter_data_final.csv`. This step further drops irrelevant columns and removes rows with missing data (~1,000).
