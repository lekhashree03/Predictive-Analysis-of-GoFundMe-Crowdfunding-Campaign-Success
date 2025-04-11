# The GoFundMe Dataset

The GoFundMe dataset is part of the training data for the [CommonFrame](https://ra2.io/products) project. It is a collection of the individual fund raising campaigns available through the [GoFundMe](https://www.gofundme.com/discover) website. The dataset was designed to inform machine learning technologies about effective communications and campaign strategies to maximize stakeholder objectives.

## File System

Below is a list of files reflecting the entire process of mining the intial data, preprocessing raw text files, and transforming the resulting dataframe into usable information.

### Project Files

- `gofund_links_scraper.py`     :   Script for links
- `scrape_by_campaign.py`   :   Data miner
- `main.py`    :    To run the complete Flow
- `sent_tokens.ipynb`   :   Test tokenization
- `gofund_stats.ipynb`      :   Data analysis with Pandas

## Data Collection

The GoFundMe dataset was collected using Python web technologies and is stored in *csv* format. Each campaign category from the GoFundMe website was loaded until all active campaigns were cached. The resulting urls were then stored in a separate file, where each url representing individual campaigns was loaded onto a custom built webscraper that targeted elements relevant to the project. The resulting html object is then analyzed to return only the relevant information for the project. The resulting csv file is then stored to disk and imported as a dataframe where further data processing is conducted. This forms the initial training data for machine learning models.

## Description of Data

A total of 13533 campaigns was gathered under 18 different campaign categories. The data includes the individual titles and text description of the campaigns. Descriptive elements for individual campaigns were also included during the scrape which can be used for exploratory data analysis (i.e. EDA / descriptive statistics). 

**Deactivated campaigns** were dropped from the collection.

The column `story_tokens` is a tokenized copy of the header: `c_story` (campaign descriptions). The Punkt sentence tokenizer from the Python Natural Language Toolkit was used to subset the campaign descriptions.

|Column Header|Data Type|Description|
|:---|:---|:---|
|`title`|string|The given title for the campaign as published on the GoFundMe webpage|
|`raised`|int64|Total dollar (USD) amount  raised at time of scraping. The actual value in the dataset may change depending on whether the campaign had reached it’s target amount or not.|
|`target`|int64|The published target amount for the campaign.|
|`m_campaign`|string|One of 18 categories set by GoFundMe to categorize each individual campaign.|
|`created_date`|datetime64|The date the campaign was officially launched in the GoFundMe website|
|`donors`|float64|Total number of donors for the campaign|
|`scrape_date`|datetime64|Date of data mining|
|`c_story`|string|A text description of the campaign written by registered users.|
|`story_tokens`|list/string|Sentence tokens for c_story to break whole campaign descriptions into sentences (tokens). These tokens are then annotated individually to become part of the training data for the model.|




