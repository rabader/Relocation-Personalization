#%%
from sklearnex import patch_sklearn, config_context
patch_sklearn()

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import SimpleImputer
from sklearn.impute import IterativeImputer
from sklearn.impute import KNNImputer
import matplotlib.pyplot as plt

#suppress warnings
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

def get_pca_components(df,impute_feature_col_lst,pca_feature_col_lst,n_components=10,imputation_method="iterative",n_neighbors=5,max_iter=10,random_state=None,verbose=0,fig_width=8,fig_height=2):
    
    # First filter out any rows that are missing data across ALL pca_feature_cols:
    df.dropna(subset=pca_feature_col_lst, how="all", inplace=True) #if there is a value in at least 1 of these columns, the rest will be imputed
    
    # Select X dataframe:
    X = df[impute_feature_col_lst]

    # One-Hot-Encode columns with string data
    str_cols = [x for x in X.columns if X[x].dtype=="O"]
    X_ohe = pd.get_dummies(X,columns=str_cols)

    # Scale X
    X_ohe = MinMaxScaler(feature_range=(0,1)).fit_transform(X_ohe) #non-distorting, but makes defining min/max values for iterative imputation easier

    # Impute Missing Values to get PCA (choose one of the below imputation methods):
    if imputation_method=="simple":
        # Use Simple Imputer
        imp_mean = SimpleImputer(missing_values=np.nan, strategy='mean')
        imp_X = imp_mean.fit_transform(X_ohe)

    if imputation_method=="iterative":
        # # Use Iterative Imputer
        imp_iter = IterativeImputer(max_iter=max_iter,min_value=0,max_value=1,random_state=random_state,verbose=verbose,tol=1e-4) # LOOK INTO "add_indicator" karg
        imp_X = imp_iter.fit_transform(X_ohe)
    
    if imputation_method=="knn":
        # Use KNN Imputer
        imp_knn = KNNImputer(n_neighbors=n_neighbors, weights="uniform")
        imp_X = imp_knn.fit_transform(X_ohe)

    # Normalize X
    X_scaled = StandardScaler().fit_transform(imp_X)

    # Filter to only features we care about for PCA
    pca_cols_idx = [X.columns.get_loc(c) for c in pca_feature_col_lst if c in X]
    X_scaled_for_pca = np.take(X_scaled, pca_cols_idx, axis=1)

    # Perform PCA
    pca = PCA(n_components=n_components,random_state=random_state).fit(X_scaled_for_pca)
    pca_components = pca.components_

    # Get feature labels for PCA:
    max_idx=[np.where(np.abs(pca_components[x])==np.max(np.abs(pca_components[x])))[0][0] for x in range(len(pca_components))] 
    X_pca_fltd_cols = [x for x in X.columns if x in pca_feature_col_lst]
    X_pca_fltd = X[X_pca_fltd_cols]
    pca_feature_names=[X_pca_fltd.columns[x] for x in max_idx]

    # Plt Results:
    pca_chart_df = pd.DataFrame(data = pca.explained_variance_, index = pca_feature_names, columns = ["explained_variance"])
    pca_chart_df.sort_values(by=["explained_variance"], ascending=True, inplace=True)
    pca_chart = pca_chart_df.plot.barh()
    plt.xscale("log")
    plt.rcParams["figure.figsize"]= (fig_width,fig_height)

    return pca_feature_names, pca_chart


# def perform_knn_analysis(user_df,county_df):


