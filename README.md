relocation-destination-personalization-machination
==============================

[SIADS699 Capstone Project Blog/Report](https://docs.google.com/document/d/1FIWErmp5vROyqxZ-FWEhxqRoRkev7X2j9UK_XVgYvN8)

[Project Overview Video + Demo](https://drive.google.com/file/d/18kUIyaUUqIjFS9_mHYpZF7l1lGarIwas/view?usp=sharing)

Team Members:
------------
Collin Clifford - cgcliff

Robert Abader - abaderro

Project Organization
------------

    ├── LICENSE
    ├── README.md                <- The top-level README for developers using this project.
    ├── data
    │   ├── external             <- Data from third party sources.
    │   │   ├── user_responses   <- Commpleted questionnaires to run through recommender.
    │   ├── interim              <- Intermediate data that has been transformed.
    │   ├── processed            <- The final, canonical data sets for modeling.
    │   └── raw                  <- The original, immutable data dump.
    │
    ├── notebooks                <- Jupyter notebooks, where all analysis resides.
    │
    ├── utils                    <- Customized function modules for use by notebooks. 
    │
    ├── requirements.txt         <- The requirements file for reproducing the analysis environment.


How To Run This Code
------------
#### 0. Install Dependencies
In a new environment, install the requirements in the requirements.txt file. This can be done with the examples shown here using pip or conda:

    pip install -r requirements.txt

    conda install --file requirements.txt

#### 1. Data Cleaning
This section of code only needs to be run when new datasets are added. It also likely needs to be customized per dataset, as it is depended on column labels. The script to perform this cleaning is stored in utils/social_explorer_data_clean.py

#### 2. Principal Component Analysis
This section of code only needs to be run when evaluating a new dataset, for dimensionality reduction. If you want to do this, open the notebook at this location: notebooks/pca_exploration.ipynb and run all of the cells. This notebook leverages the functions in utils/se_analysis.py. Reference this file for more details on the operations/transorfmations. This step also saves modified versions of input data that have missing values imputed.

#### 3. Quiz Evaluation
This section of code creates n randomized quiz entries, and feeds them through the county matching recommender. This can be found in the notebooks/RDPM_Recommender_Evaluation.ipynb notebook. The number of randomized quizzes to run can be set in the notebook, and then you can run all of the cells.

#### 4. Fill Questionairre
Create a copy of the quiz, found at data/external/user_responses/"RDPM Questionnaire.xlsx" and fill out the responses.

#### 5. Run Recommender
Point the quiz to the newly filled out questionnaire file, and run all cells to find matching counties and some visualizations that provide insight.


Data Access Statement
------------
Data used in this project was retrieved from Social Explorer, at https://www.socialexplorer.com/explore-tables
Access to this data is paywalled, but this link https://www.lib.umich.edu/database/link/10387 takes you to the subscription version provided by the University of Michigan Library, which is the method we used for access.

--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
