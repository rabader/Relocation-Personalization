#%%
from sklearnex import patch_sklearn, config_context
patch_sklearn()

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
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

def get_pca_components(df,impute_feature_col_lst,pca_feature_col_lst,n_components,random_state=None,max_iter=10,fig_width=8,fig_height=2):
    X = df[impute_feature_col_lst]

    # One-Hot-Encode columns with string data
    str_cols = [x for x in X.columns if X[x].dtype=="O"]
    X_ohe = pd.get_dummies(X,columns=str_cols)

    # Normalize X
    X_normalized = StandardScaler().fit(X_ohe).transform(X_ohe)

    # Impute Missing Values to get PCA:
    # # Use Simple Imputer
    # imp_mean = SimpleImputer(missing_values=np.nan, strategy='mean')
    # imp_mean.fit(X_normalized)
    # imp_X = imp_mean.transform(X)

    # # Use Iterative Imputer
    # imp_iter = IterativeImputer(max_iter=max_iter, random_state=random_state) # LOOK INTO "add_indicator" karg
    # imp_iter.fit(X_normalized)
    # imp_X = imp_iter.transform(X)
    
    # # Use KNN Imputer
    imp_knn = KNNImputer(n_neighbors=5, weights="uniform")
    imp_knn.fit_transform(X_normalized)
    imp_X = imp_knn.transform(X_ohe)

    # Filter to only features we care about for PCA
    pca_cols_idx = [X.columns.get_loc(c) for c in pca_feature_col_lst if c in X]
    imp_X_for_pca = np.take(imp_X, pca_cols_idx, axis=1)

    # Perform PCA
    pca = PCA(n_components=n_components,random_state=random_state).fit(imp_X_for_pca)
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

    # return pca_feature_names, pca_chart
    return pca_feature_names, pca_chart


