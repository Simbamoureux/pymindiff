import pandas as pd
import numpy as np
from pymindiff.scale import MinMaxScaler


#TODO Address the problem of metrics weighting more in the sum than others
#TODO Exact solution
#TODO Handle categorical data
#TODO Write unit tests

def create_groups(data : pd.DataFrame, criteria : list, n_groups : int = 2, n_iter : int = 100, equalize=[np.mean], scale=False) -> pd.DataFrame:  
    if any(column not in data.columns.values for column in criteria):
        raise ValueError("Column not found in dataframe")
    else:
        diff_scores = list()
        if scale:
            scaler = MinMaxScaler()
            data[criteria] = scaler.fit_transform(data[criteria].copy())
        for i in range(n_iter):
            data['subset'] = np.random.choice([i for i in range(n_groups)], size=len(data))
            try:
                total_diff = 0
                for metric in equalize:
                    sum_of_columns_diff = 0
                    group_values = data.groupby(['subset'])[criteria].apply(metric)
                    for column in criteria:
                        largest_diff = max(group_values[column]) - min(group_values[column])
                        sum_of_columns_diff += largest_diff
                    #We keep the biggest difference between 2 groups for each criteria as the treshold
                    total_diff += sum_of_columns_diff
                diff_scores.append(total_diff)
            except TypeError as e:
                raise ValueError('The metric could not be computed using the column values, is the data numeric ?')
            if len(diff_scores) == 1:
                min_diff = diff_scores[0]
                data['groups'] = data['subset']
            else:
                if min_diff > min(diff_scores):
                    min_diff = min(diff_scores)
                    data['groups'] = data['subset']
        if scale:
            data[criteria] = scaler.inverse_transform(data[criteria].copy())
    return data