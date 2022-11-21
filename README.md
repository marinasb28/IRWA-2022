# IRWA-2022-u161822-u172733-u172958

### Authors

- Miquel Casas Olivella
- Aina Moncho Roig
- Marina Suárez Blázquez

**This document contains detailed instructions on how to execute the code and choose the various functions and/or other choices to run the code.**


## PART 1: Text Processing

### Before executing
1. Check that the `data`folder contains the files:
- `tw_hurricane_data.json`: contains all the tweets documents
- `tweet_document_ids_map.csv`: used for mapping
If it doesn't make sure to upload these two files so that you do not run into any problem.
2. You will need to run this code on Google Colaboratory or Jupyter Notebook, then make sure to any python-supported platform.

### Further instructions
The main cell shows the code for the processing of the data to tweets taking into account the fields and the necessary information. Then, we make a comparison of 5 processed and unprocessed tweets to check the correctness of the results.




## PART 2: Indexing & Evaluation

### Before executing
1. Check that the `data`folder contains the files:
- `tw_hurricane_data.json`: contains all the tweets documents
- `tweet_document_ids_map.csv`: used for mapping
- `evaluation_gt.csv`: contains 3 queries and a subset of documents from the dataset.
If it doesn't make sure to upload these two files so that you do not run into any problem.
2. You will need to run this code on Google Colaboratory or Jupyter Notebook, then make sure to any python-supported platform.

### Further instructions
The program uses the generated output from the previous part, part 1. In this part we create an index for every term in the set of tweets and we also stored their tf and idf. 




## PART 3: Ranking
