#%%
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.impute import KNNImputer

def impute_data(df,impute_cols_lst,imputation_method="iterative",random_state=0,verbose=0):
    """Impute missing data in numerical columns from the input dataframe.

    Args:
        df (pandas DataFrame): A pandas dataframe with some missing data.
        impute_cols_lst (list): A list of columns to impute.
        imputation_method (str, optional): Imputation method of choice. Defaults to "iterative".
        random_state (int, optional): Random state. Defaults to 0.
        verbose (int, optional): Verbosity of output during imputation. Defaults to 0.

    Returns:
        _type_: _description_
    """
    df.dropna(subset=impute_cols_lst, how="all", inplace=True) #if there is a value in at least 1 of these columns, the rest will be imputed
    df = df.dropna(axis=1, how='all') #drop columns where all the values are null
    df.reset_index(drop=True,inplace=True)

    # Select X dataframe:
    impute_cols_lst = [x for x in df.columns if x in impute_cols_lst]
    X = df[impute_cols_lst]

    str_cols = [x for x in X.columns if X[x].dtype=="O"]
    X_ohe_df = pd.get_dummies(X,columns=str_cols)

    # Scale X
    min_max_scaler = MinMaxScaler(feature_range=(0,1)).fit(X_ohe_df)
    X_ohe = min_max_scaler.transform(X_ohe_df) #non-distorting, but makes defining min/max values for iterative imputation easier

    # Impute Missing Values to get PCA (choose one of the below imputation methods):
    if imputation_method=="iterative":
        # # Use Iterative Imputer
        imp_iter = IterativeImputer(max_iter=5,min_value=0,max_value=1,random_state=random_state,verbose=verbose,tol=1e-4) # LOOK INTO "add_indicator" karg
        imp_X = imp_iter.fit_transform(X_ohe)

    if imputation_method=="knn":
        # Use KNN Imputer
        imp_knn = KNNImputer(n_neighbors=10, weights="uniform")
        imp_X = imp_knn.fit_transform(X_ohe)

    # Save Imputed DataFrame:
    imp_X_unscaled = min_max_scaler.inverse_transform(imp_X)
    imputed_df = pd.DataFrame(imp_X_unscaled, columns=X_ohe_df.columns)
    imputed_df_non_ohe_cols = [x for x in imputed_df.columns if x in impute_cols_lst]
    imputed_df = imputed_df[imputed_df_non_ohe_cols] #remove one-hot-encoded columns
    df_cols_not_imputed = [x for x in df.columns if x not in imputed_df.columns]
    imputed_df = df[df_cols_not_imputed].merge(imputed_df,left_index=True,right_index=True)
    imputed_idx_df = df.isnull()

    return imputed_df,imputed_idx_df

# Read in datasets:
acs_df = pd.read_csv("../data/processed/ACS_2020.csv")
crime_df = pd.read_csv("../data/interim/fbi_imputed.csv.gz")
health_df = pd.read_csv("../data/interim/health_imputed.csv.gz")
religion_df = pd.read_csv("../data/processed/Religion_dataset.csv")
school_df = pd.read_csv("../data/interim/School_2018_imputed.csv.gz")
terrain_df = pd.read_csv("../data/interim/Terrain_imputed.csv.gz")
weather_df = pd.read_csv("../data/processed/Weather_etc_State_dataset.csv")

# Filter out to only latest year
crime_df = crime_df[crime_df["Year"]==crime_df["Year"].max()]
health_df = health_df[health_df["Year"]==health_df["Year"].max()]
terrain_df = terrain_df[terrain_df["Year"]==terrain_df["Year"].max()]

# Set column types before merging
acs_df[["FIPS"]] = acs_df[["FIPS"]].astype(str)
crime_df[["FIPS"]] = crime_df[["FIPS"]].astype(str)
health_df[["FIPS"]] = health_df[["FIPS"]].astype(str)
school_df[["FIPS"]] = school_df[["FIPS"]].astype(str)

# School data is by district; Use weighted averages (based on # of students per district to get data at the county level)
# Store district info as "num_districts" variable:
school_df["num_districts"] = school_df.groupby(["County","State"])["School District Name"].transform("count")
wm = lambda x: np.ma.average(x, weights=school_df.loc[x.index, "Number of All students"])
school_county_df = school_df.drop(columns=["School District Name","FIPS"]).groupby(["County","State"]).agg(wm).reset_index()

# Merge datasets into 1 wide dataframe
def left_merger(df1,df2,on_cols):
    """Perform a left join and remove duplicated columns.
    """
    cols_to_use = list(df2.columns.difference(df1.columns))
    cols_to_use = cols_to_use + on_cols
    df_merged = df1.merge(df2[cols_to_use],on=on_cols,how="left")
    return df_merged

df = left_merger(acs_df,crime_df,["FIPS"])
df = left_merger(df,health_df,["FIPS"])
df = left_merger(df,school_county_df,["County","State"])
df = left_merger(df,weather_df,["State"])
df = left_merger(df,terrain_df,["County","State"])

# Drop unneeded columns
df.drop(columns=["FIPS_Year"],inplace=True,errors="ignore")

# Before adding religion, do one more round of imputation
impute_cols_lst = list(df.columns.difference(["FIPS","County"]))
df,df_idx = impute_data(df,impute_cols_lst,imputation_method="knn")

# Add in religion data
df = left_merger(df,religion_df,["County","State"])

# Write to CSV
df.to_csv("../data/interim/county_matcher_data.csv.gz",index=False)

# %%
