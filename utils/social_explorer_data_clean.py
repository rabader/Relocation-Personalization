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

    fbi_concat_df = pd.DataFrame()
    for fbi_file in fbi_file_lst:
        # Read file as dataframe:
        fbi_df = pd.read_csv(fbi_file, encoding="ISO-8859-1") #Social Explorer uses Western Latin-1 (ISO-8859-1) encoding

        # Get year:
        fbi_year = re.findall(r'\d+', [x for x in fbi_df.columns if "Total Population (" in x][0])[0]
        fbi_df["Year"] = fbi_year

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

        fbi_df.rename(columns={"State":"state_code","County":"county_code"}, inplace=True)
        fbi_df["State"] = fbi_df["state_code"].map(state_num_dict)

        # Get primary key and rename some columns:
        fbi_df["FIPS_Year"] = fbi_df["FIPS"].astype(str)+"_"+str(fbi_year)
        fbi_df.rename(columns=lambda x: "Total Population" if "Total Population (" in x else x, inplace=True)
        fbi_df.drop(columns="Qualifying Name",inplace=True)
        fbi_df.rename(columns={"Name of Area":"County"}, inplace=True)

        # Concatenate data
        fbi_concat_df = pd.concat([fbi_concat_df,fbi_df], ignore_index=True)
        
    # Re-order some columns for better readability during exploration:
    ref_cols = ['FIPS','County','State','FIPS_Year','Year']
    other_cols = [col for col in fbi_concat_df.columns if col not in ref_cols]
    fbi_concat_df = fbi_concat_df[ref_cols+other_cols]

    # Save to Processed Data Folder
    fbi_concat_df.to_csv(f"../data/processed/fbi_crime.csv.gz", encoding="utf-8-sig",index=False)
        

def clean_ucr_crime_raw_data():
    """
    Function to clean raw ucr_crime CSV data, and store cleaned results in project's "processed" data folder.
    """
    # Get file names of all raw UCR crime data CSVs.
    ucr_file_lst = glob.glob('../data/raw/ucr_crime*.csv')
    ucr_concat_df = pd.DataFrame()
    for ucr_file in ucr_file_lst:
        # Read file as dataframe:
        ucr_df = pd.read_csv(ucr_file,encoding="ISO-8859-1") #Social Explorer uses Western Latin-1 (ISO-8859-1) encoding

        # Remove duplicated columns:
        ucr_df = ucr_df.loc[:, ~ucr_df.columns.str.replace("(\.\d+)$", "").duplicated()]

        # Get year:
        ucr_year = re.findall(r'\d+', [x for x in ucr_df.columns if "Total Population (" in x][0])[0]
        ucr_df["Year"] = ucr_year

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
        
        ucr_df.rename(columns={"State":"state_code","County":"county_code"}, inplace=True)
        ucr_df["State"] = ucr_df["state_code"].map(state_num_dict)

        # Get primary key and rename some columns:
        ucr_df["FIPS_Year"] = ucr_df["FIPS"].astype(str)+"_"+str(ucr_year)
        ucr_df.rename(columns=lambda x: "Total Population" if "Total Population (" in x else x, inplace=True)
        ucr_df.drop(columns="Qualifying Name",inplace=True)
        ucr_df.rename(columns={"Name of Area":"County"}, inplace=True)

        # Concatenate data
        ucr_concat_df = pd.concat([ucr_concat_df,ucr_df], ignore_index=True)
    
    # Re-order some columns for better readability during exploration:
    ref_cols = ['FIPS','County','State','FIPS_Year','Year']
    other_cols = [col for col in ucr_concat_df.columns if col not in ref_cols]
    ucr_concat_df = ucr_concat_df[ref_cols+other_cols]

    # Save to Processed Data Folder
    ucr_concat_df.to_csv(f"../data/processed/ucr_crime.csv.gz", encoding="utf-8-sig",index=False)


def clean_health_raw_data():
    """
    Function to clean raw health CSV data, and store cleaned results in project's "processed" data folder.
    """
    # Get file names of all raw UCR crime data CSVs.
    health_file_lst = glob.glob('../data/raw/health*.csv')

    health_concat_df = pd.DataFrame()
    for health_file in health_file_lst:
        # Read file as dataframe:
        health_df = pd.read_csv(health_file,encoding="ISO-8859-1") #Social Explorer uses Western Latin-1 (ISO-8859-1) encoding

        # Remove duplicated columns:
        health_df = health_df.loc[:, ~health_df.columns.str.replace("(\.\d+)$", "").duplicated()]

        # Get year from filename (no indicators in health data):
        health_year = re.findall(r'\d+', health_file)[0]
        health_df["Year"] = health_year

        # Begin Cleaning:
        health_df = health_df.iloc[1:].reset_index(drop=True) #drop first row

        # Get state # to state_name key:
        state_num_dict = dict()
        for county_num in range(len(health_df)):
            try:
                state_name = health_df.iloc[0]["Qualifying Name"].split(",")[1].strip()
                state_num = health_df.iloc[county_num]["State"]
                state_num_dict[state_num] = state_name
            except:
                pass

        health_df.rename(columns={"State":"state_code","County":"county_code"}, inplace=True)
        health_df["State"] = health_df["state_code"].map(state_num_dict)

        # Get primary key and rename some columns:
        health_df["FIPS_Year"] = health_df["FIPS"].astype(str)+"_"+str(health_year)
        health_df.rename(columns=lambda x: re.sub("\, .\d.*est.\)",")",x), inplace=True)
        health_df.drop(columns="Qualifying Name",inplace=True)
        health_df.rename(columns={"Name of Area":"County"}, inplace=True)

        # Concatenate data
        health_concat_df = pd.concat([health_concat_df,health_df], ignore_index=True)
    
    # Re-order some columns for better readability during exploration:
    ref_cols = ['FIPS','County','State','FIPS_Year','Year']
    other_cols = [col for col in health_concat_df.columns if col not in ref_cols]
    health_concat_df = health_concat_df[ref_cols+other_cols]

    # Save to Processed Data Folder
    health_concat_df.to_csv(f"../data/processed/health.csv.gz", encoding="utf-8-sig",index=False)
       
#%%
clean_fbi_crime_raw_data()
clean_ucr_crime_raw_data()
clean_health_raw_data()


# %%
