#%%
import pandas as pd
import glob
import re

def clean_fbi_crime_raw_data():
    """
    Function to clean raw fbi_crime CSV data, and store cleaned results in project's "processed" data folder.
    """
    # Get file names of all raw FBI crime data CSVs.
    fbi_file_lst = glob.glob('../data/raw/fbi_crime*.csv')
    for fbi_file in fbi_file_lst:
        # Read file as dataframe:
        fbi_df = pd.read_csv(fbi_file, encoding="ISO-8859-1") #Social Explorer uses Western Latin-1 (ISO-8859-1) encoding

        # Get year:
        fbi_year = re.findall(r'\d+', [x for x in fbi_df.columns if "Total Population (" in x][0])[0]

        # Begin Cleaning:
        fbi_df = fbi_df.iloc[1:].reset_index(drop=True) #drop first row

        # Get state # to state_name key:
        state_num_dict = dict()
        for county_num in range(len(fbi_df)):
            try:
                state_name = fbi_df.iloc[0]["Qualifying Name"].split(",")[1].strip()
                state_num = fbi_df.iloc[county_num]["State"]
                state_num_dict[state_num] = state_name
            except:
                pass
        fbi_df["state_name"] = fbi_df["State"].map(state_num_dict)

        # Get primary key and rename some columns:
        fbi_df["FIPS_year"] = fbi_df["FIPS"].astype(str)+"_"+str(fbi_year)
        fbi_df.rename(columns=lambda x: "Total Population" if "Total Population (" in x else x, inplace=True)
        fbi_df.drop(columns="Qualifying Name",inplace=True)
        fbi_df.rename(columns={"Name of Area":"county_name"}, inplace=True)

        # Save to Processed Data Folder
        fbi_df.to_csv(f"../data/processed/fbi_crime_{fbi_year}.csv.gz", encoding="utf-8")
        

def clean_ucr_crime_raw_data():
    """
    Function to clean raw ucr_crime CSV data, and store cleaned results in project's "processed" data folder.
    """
    # Get file names of all raw UCR crime data CSVs.
    ucr_file_lst = glob.glob('../data/raw/ucr_crime*.csv')
    for ucr_file in ucr_file_lst:
        # Read file as dataframe:
        ucr_df = pd.read_csv(ucr_file,encoding="ISO-8859-1") #Social Explorer uses Western Latin-1 (ISO-8859-1) encoding

        # Remove duplicated columns:
        ucr_df = ucr_df.loc[:, ~ucr_df.columns.str.replace("(\.\d+)$", "").duplicated()]

        # Get year:
        ucr_year = re.findall(r'\d+', [x for x in ucr_df.columns if "Total Population (" in x][0])[0]

        # Begin Cleaning:
        ucr_df = ucr_df.iloc[1:].reset_index(drop=True) #drop first row

        # Get state # to state_name key:
        state_num_dict = dict()
        for county_num in range(len(ucr_df)):
            try:
                state_name = ucr_df.iloc[0]["Qualifying Name"].split(",")[1].strip()
                state_num = ucr_df.iloc[county_num]["State"]
                state_num_dict[state_num] = state_name
            except:
                pass
        ucr_df["state_name"] = ucr_df["State"].map(state_num_dict)

        # Get primary key and rename some columns:
        ucr_df["FIPS_year"] = ucr_df["FIPS"].astype(str)+"_"+str(ucr_year)
        ucr_df.rename(columns=lambda x: "Total Population" if "Total Population (" in x else x, inplace=True)
        ucr_df.drop(columns="Qualifying Name",inplace=True)
        ucr_df.rename(columns={"Name of Area":"county_name"}, inplace=True)

        # Save to Processed Data Folder
        ucr_df.to_csv(f"../data/processed/ucr_crime_{ucr_year}.csv.gz",encoding="utf-8")

#%%
# clean_fbi_crime_raw_data()
# clean_ucr_crime_raw_data

