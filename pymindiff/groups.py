import pandas as pd
import numpy as np

#TODO Multiple criterias
#TODO Multiple groups
#TODO Custom metrics
#TODO different metrics ?
#TODO Exact solution
#TODO Handle categorical data
#TODO Write unit tests

def create_groups(data : pd.DataFrame, criteria : str, n_groups : int = 2, n_iter : int = 100) -> pd.DataFrame:
    if criteria not in data.columns.values:
        raise ValueError("Column not found in dataframe")
    else:
        diff_scores = list()
        for i in range(n_iter):
            data['subset'] = np.random.choice([i for i in range(n_groups)], size=len(data))
            try:
                group_values = sorted(data.groupby(['subset'])[criteria].mean().values)
                #We keep the biggest difference between 2 groups as the treshold
                diff_scores.append(np.abs(group_values[0] - group_values[-1]))
                print(np.abs(group_values[0] - group_values[-1]))
            except TypeError as e:
                raise ValueError('The metric could not be computed using the column values, is the data numeric ?')
            if len(diff_scores) == 1:
                min_diff = diff_scores[0]
                data['groups'] = data['subset']
            else:
                if min_diff > min(diff_scores):
                    min_diff = min(diff_scores)
                    data['groups'] = data['subset']
    return data