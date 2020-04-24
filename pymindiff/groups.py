import pandas as pd
import numpy as np

#TODO : Multiple criterias
#TODO : Multiple groups
#TODO : Custom metrics
#TODO : different metrics ?
#TODO : Exact solution
#TODO : Handle categorical data
def create_groups(data, criteria, n_groups = 2,n_iter=100):
    if criteria not in data.columns.values:
        raise ValueError("Column not found in dataframe")
    else:
        diff_scores = list()
        for i in range(n_iter):
            data['subset'] = np.random.choice([0,1], size=len(data))
            try:
                diff_scores.append(np.abs(data.loc[data.subset == 0][criteria].mean() - data.loc[data.subset == 1][criteria].mean()))
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