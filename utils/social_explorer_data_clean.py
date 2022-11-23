#%%
import pandas as pd
import glob
import re
def clean_population_estimate_raw_data():
    """
    Function to clean raw population_estimate CSV data, and store cleaned results in project's "processed" data folder.
    """
    # Get file names of all raw FBI crime data CSVs.
    popest_file_lst = glob.glob('../data/raw/population_estimate*.csv')

    popest_concat_df = pd.DataFrame()
    for popest_file in popest_file_lst:
        # Read file as dataframe:
        popest_df = pd.read_csv(popest_file, encoding="ISO-8859-1") #Social Explorer uses Western Latin-1 (ISO-8859-1) encoding

        # Remove duplicated columns:
        popest_df = popest_df.loc[:, ~popest_df.columns.str.replace("(\.\d+)$", "", regex=True).duplicated()]

        # Get year:
        popest_year = re.findall(r'\d+', popest_file)[0]
        popest_df["Year"] = popest_year

        # Begin Cleaning:
        popest_df = popest_df.iloc[1:].reset_index(drop=True) #drop first row

        # Get state # to state_name key:
        state_num_dict = dict()
        for county_num in range(len(popest_df)):
            try:
                state_name = popest_df.iloc[county_num]["Qualifying Name"].split(",")[1].strip()
                state_num = popest_df.iloc[county_num]["State"]
                state_num_dict[state_num] = state_name
            except:
                pass

        popest_df.rename(columns={"State":"state_code","County":"county_code"}, inplace=True)
        popest_df["State"] = popest_df["state_code"].map(state_num_dict)

        # Get primary key and rename some columns:
        popest_df["FIPS_Year"] = popest_df["FIPS"].astype(str)+"_"+str(popest_year)
        popest_df.drop(columns="Qualifying Name",inplace=True)
        popest_df.rename(columns={"Name of Area":"County"}, inplace=True)

        # Make all columns Title Case
        popest_df.columns = [(' '.join([w.title() if w.islower() else w for w in x.split()])) for x in popest_df.columns]

        # Consistent Rate Names in Column Names:
        popest_df.columns = [x.replace("100 000","100,000") for x in popest_df.columns]
        popest_df.columns = [x.replace("100000","100,000") for x in popest_df.columns]
        popest_df.columns = [x.replace("1000","1,000") for x in popest_df.columns]
        popest_df.columns = [x.replace("1 000","1,000") for x in popest_df.columns]

         # Concatenate data
        popest_df = popest_df.loc[:, ~popest_df.columns.duplicated()]
        popest_concat_df = pd.concat([popest_concat_df,popest_df], ignore_index=True)
        
    # Re-order some columns for better readability during exploration:
    ref_cols = ['FIPS','County','State','FIPS_Year','Year','Total Population']
    other_cols = [col for col in popest_concat_df.columns if col not in ref_cols and "%" in col] #only keep percentages
    popest_concat_df = popest_concat_df[ref_cols+other_cols]

    # Drop columns with no data
    popest_concat_df = popest_concat_df.dropna(axis=1, how='all')

    # Save to Processed Data Folder
    popest_concat_df.to_csv(f"../data/processed/population_estimate.csv.gz", encoding="utf-8-sig",index=False)


def clean_fbi_crime_raw_data():
    """
    Function to clean raw fbi_crime CSV data, and store cleaned results in project's "processed" data folder.
    Note that columns with "Rate" in the column name are rates per 100,000 people.
    """
    # Get file names of all raw FBI crime data CSVs.
    fbi_file_lst = glob.glob('../data/raw/fbi_crime*.csv')

    fbi_concat_df = pd.DataFrame()
    for fbi_file in fbi_file_lst:
        # Read file as dataframe:
        fbi_df = pd.read_csv(fbi_file, encoding="ISO-8859-1") #Social Explorer uses Western Latin-1 (ISO-8859-1) encoding

        # Remove duplicated columns:
        fbi_df = fbi_df.loc[:, ~fbi_df.columns.str.replace("(\.\d+)$", "", regex=True).duplicated()]

        # Get year:
        fbi_year = re.findall(r'\d+', [x for x in fbi_df.columns if "Total Population (" in x][0])[0]
        fbi_df["Year"] = fbi_year

        # Begin Cleaning:
        fbi_df = fbi_df.iloc[1:].reset_index(drop=True) #drop first row

        # Get state # to state_name key:
        state_num_dict = dict()
        for county_num in range(len(fbi_df)):
            try:
                state_name = fbi_df.iloc[county_num]["Qualifying Name"].split(",")[1].strip()
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

        # Make all columns Title Case
        fbi_df.columns = [(' '.join([w.title() if w.islower() else w for w in x.split()])) for x in fbi_df.columns]

        # Consistent Rate Names in Column Names:
        fbi_df.columns = [x.replace("100 000","100,000") for x in fbi_df.columns]
        fbi_df.columns = [x.replace("100000","100,000") for x in fbi_df.columns]
        fbi_df.columns = [x.replace("1000","1,000") for x in fbi_df.columns]
        fbi_df.columns = [x.replace("1 000","1,000") for x in fbi_df.columns]

        # Concatenate data
        fbi_df = fbi_df.loc[:, ~fbi_df.columns.duplicated()]
        fbi_concat_df = pd.concat([fbi_concat_df,fbi_df], ignore_index=True)
        
    # Re-order some columns for better readability during exploration:
    ref_cols = ['FIPS','County','State','FIPS_Year','Year','Total Population']
    other_cols = [col for col in fbi_concat_df.columns if col not in ref_cols and "Rate" in col] #only keep rates
    fbi_concat_df = fbi_concat_df[ref_cols+other_cols]

    # Drop columns with no data
    fbi_concat_df = fbi_concat_df.dropna(axis=1, how='all')

    # Save to Processed Data Folder
    fbi_concat_df.to_csv(f"../data/processed/fbi_crime.csv.gz", encoding="utf-8-sig",index=False)
        

def clean_ucr_crime_raw_data():
    """
    Function to clean raw ucr_crime CSV data, and store cleaned results in project's "processed" data folder.
    Note that columns with "Rate" in the column name are rates per 100,000 people.
    """
    # Get file names of all raw UCR crime data CSVs.
    ucr_file_lst = glob.glob('../data/raw/ucr_crime*.csv')
    ucr_concat_df = pd.DataFrame()
    for ucr_file in ucr_file_lst:
        # Read file as dataframe:
        ucr_df = pd.read_csv(ucr_file,encoding="ISO-8859-1") #Social Explorer uses Western Latin-1 (ISO-8859-1) encoding

        # Remove duplicated columns:
        ucr_df = ucr_df.loc[:, ~ucr_df.columns.str.replace("(\.\d+)$", "", regex=True).duplicated()]

        # Get year:
        ucr_year = re.findall(r'\d+', [x for x in ucr_df.columns if "Total Population (" in x][0])[0]
        ucr_df["Year"] = ucr_year

        # Begin Cleaning:
        ucr_df = ucr_df.iloc[1:].reset_index(drop=True) #drop first row

        # Get state # to state_name key:
        state_num_dict = dict()
        for county_num in range(len(ucr_df)):
            try:
                state_name = ucr_df.iloc[county_num]["Qualifying Name"].split(",")[1].strip()
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

        # Make all columns Title Case
        ucr_df.columns = [(' '.join([w.title() if w.islower() else w for w in x.split()])) for x in ucr_df.columns]

        # Consistent Rate Names in Column Names:
        ucr_df.columns = [x.replace("100 000","100,000") for x in ucr_df.columns]
        ucr_df.columns = [x.replace("100000","100,000") for x in ucr_df.columns]
        ucr_df.columns = [x.replace("1000","1,000") for x in ucr_df.columns]
        ucr_df.columns = [x.replace("1 000","1,000") for x in ucr_df.columns]

        # Concatenate data
        ucr_df = ucr_df.loc[:, ~ucr_df.columns.duplicated()]
        ucr_concat_df = pd.concat([ucr_concat_df,ucr_df], ignore_index=True)
    
    # Re-order some columns for better readability during exploration:
    ref_cols = ['FIPS','County','State','FIPS_Year','Year','Total Population']
    other_cols = [col for col in ucr_concat_df.columns if col not in ref_cols and "Rate" in col] #only keep rates]
    ucr_concat_df = ucr_concat_df[ref_cols+other_cols]

    # Drop columns with no data
    ucr_concat_df = ucr_concat_df.dropna(axis=1, how='all')

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
        health_df = health_df.loc[:, ~health_df.columns.str.replace("(\.\d+)$", "", regex=True).duplicated()]

        # Get year from filename (no indicators in health data):
        health_year = re.findall(r'\d+', health_file)[0]
        health_df["Year"] = health_year

        # Begin Cleaning:
        health_df = health_df.iloc[1:].reset_index(drop=True) #drop first row

        # Get state # to state_name key:
        state_num_dict = dict()
        for county_num in range(len(health_df)):
            try:
                state_name = health_df.iloc[county_num]["Qualifying Name"].split(",")[1].strip()
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

        # Make all columns Title Case
        health_df.columns = [(' '.join([w.title() if w.islower() else w for w in x.split()])) for x in health_df.columns]

        # Remove the word "Of" to take care of inconsistencies in column names from year-to-year
        health_df.rename(columns=lambda x: re.sub("Of ","",x), inplace=True)

        # Consistent Rate Names in Column Names:
        health_df.columns = [x.replace("100 000","100,000") for x in health_df.columns]
        health_df.columns = [x.replace("100000","100,000") for x in health_df.columns]
        health_df.columns = [x.replace("1000","1,000") for x in health_df.columns]
        health_df.columns = [x.replace("1 000","1,000") for x in health_df.columns]

        # Concatenate data
        health_df = health_df.loc[:, ~health_df.columns.duplicated()]
        health_concat_df = pd.concat([health_concat_df,health_df], ignore_index=True)

    
    # Re-order some columns for better readability during exploration:
    # Only Keep Data with Rates:
    popestdf = pd.read_csv("../data/processed/population_estimate.csv.gz", usecols = ["FIPS_Year","Total Population"],encoding="utf-8-sig")
    health_concat_df = health_concat_df.merge(popestdf,how="left",on="FIPS_Year")
    ref_cols = ['FIPS','County','State','FIPS_Year','Year','Total Population']
    other_cols = [col for col in health_concat_df.columns if col not in ref_cols]
    rate_cols = [col for col in other_cols if "Rate" in col or "%" in col or "Percent" in col] #only keep rates]
    health_concat_df = health_concat_df[ref_cols+rate_cols]

    # Drop columns with no data
    health_concat_df = health_concat_df.dropna(axis=1, how='all')

    # Save to Processed Data Folder
    health_concat_df.to_csv(f"../data/processed/health.csv.gz", encoding="utf-8-sig",index=False)
       
#%%
# clean_population_estimate_raw_data()
# clean_fbi_crime_raw_data()
# clean_ucr_crime_raw_data()
# clean_health_raw_data()

