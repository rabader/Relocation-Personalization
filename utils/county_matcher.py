import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsClassifier


def county_matcher(county_df,user_ref_df,feature_cols,target_col="FIPS",n_neighbors = 500):
    # Scale user weights:
    user_weights_array = user_ref_df[["Importance"]].to_numpy().reshape(1,-1)[0]
    weights_array_max = user_ref_df[["max_importance"]].to_numpy().reshape(1,-1)[0]
    user_weights_array_scaled = user_weights_array/weights_array_max
    
    # Format user responses for use with knn classifier:
    user_response_array = user_ref_df[["Response"]].T
    response_array_max = user_ref_df[["max_response"]].to_numpy().reshape(1,-1)[0]
    user_response_scaled = user_response_array/response_array_max

    # Any remaining NA values will be filled with 0's (i.e. for religion adherancy):
    county_df = county_df.fillna(value=0)

    # Format and scale inputs for classifier:
    y = county_df[target_col].astype(str)
    X = county_df[feature_cols]
    X_scaler = MinMaxScaler().fit(X)
    X_scaled = X_scaler.transform(X)
    X_scaled_weighted = X_scaled*user_weights_array_scaled #incorporate user-selected importance weights

    # Create and Fit KNN Classifier:
    neigh = KNeighborsClassifier(n_neighbors=n_neighbors, weights="distance")
    neigh.fit(X_scaled_weighted, y)

    # Get indices to neighbors and their distances:
    dist,ind = neigh.kneighbors(user_response_scaled,return_distance=True)

    # Find nearest neighbors based on user's responses/weights
    nearest_neighbors = county_df[["FIPS","County","State"]].iloc[np.r_[ind][0]]
    
    return nearest_neighbors
    # return X,X_scaled,X_scaled_weighted
