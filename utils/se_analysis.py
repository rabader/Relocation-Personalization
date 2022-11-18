import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt

def get_pca_components(df,feature_col_lst,n_components,random_state=None,fig_width=8,fig_height=2):
    X = df[feature_col_lst]

    # Normalize X
    X_normalized = StandardScaler().fit(X).transform(X)

    # Impute Missing Values to get PCA:
    imp_mean = SimpleImputer(missing_values=np.nan, strategy='mean')
    imp_mean.fit(X_normalized)
    imp_X = imp_mean.transform(X)

    # Perform PCA
    pca = PCA(n_components=n_components,random_state=random_state).fit(imp_X)
    pca_components = pca.components_

    # Get feature labels for PCA:
    max_idx=[np.where(np.abs(pca_components[x])==np.max(np.abs(pca_components[x])))[0][0] for x in range(len(pca_components))]
    pca_feature_names=[X.columns[x] for x in max_idx]

    # Plt Results:
    pca_chart_df = pd.DataFrame(data = pca.explained_variance_, index = pca_feature_names, columns = ["explained_variance"])
    pca_chart_df.sort_values(by=["explained_variance"], ascending=True, inplace=True)
    pca_chart = pca_chart_df.plot.barh()
    plt.xscale("log")
    plt.rcParams["figure.figsize"]= (fig_width,fig_height)

    return pca_feature_names, pca_chart