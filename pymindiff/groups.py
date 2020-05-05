import pandas as pd
from math import ceil
from itertools import permutations
import numpy as np
from pymindiff.scale import MinMaxScaler
from pymindiff.partitions import set_partitions, get_groups_column_from_partitions


#TODO Address the problem of metrics weighting more in the sum than others
#TODO Add the possibility to pass data that already had been optimized to optimize again and try to find better groups
#TODO Write unit tests
#TODO Use partitions of same-ish length to find exact solution too ?
#TODO Write README
#TODO Write docs
#TODO Work on performance
#TODO Don't rely on pandas ?
#TODO integrate to Pypi

def is_nominal_tolerance_met(data : pd.DataFrame, criteria_nominal : list = [], nominal_tolerance : list = []):
    if len(criteria_nominal) == 0:
        return True
    else:
        for column_criteria, tol in zip(criteria_nominal, nominal_tolerance):
            nominal_check = data.groupby([column_criteria, 'subset']).size()
            nominal_diff_values = [max(nominal_check[i].values) - min(nominal_check[i].values) for i in data[column_criteria].unique()]
            if max(nominal_diff_values) > tol:
                return False
        return True


def get_permutations(data_length, n_groups, n_iter, exact):
    draw_groups = ([i for i in range(n_groups)] * (ceil(data_length / n_groups)))[:data_length]
    if exact:
        partitions = [elem for elem in set_partitions([i for i in range(data_length)], n_groups)]
        return get_groups_column_from_partitions(partitions, data_length)
    else:
        return [np.random.choice(draw_groups, size=data_length, replace=False) for i in range(n_iter)]


def create_groups(data : pd.DataFrame, criteria : list = [], criteria_nominal : list = [], nominal_tolerance : list = [], n_groups : int = 2, n_iter : int = 100, equalize=[np.mean], scale=False, exact=False) -> pd.DataFrame: 
    assert len(criteria) > 0 or len(criteria_nominal) > 0, "No critera passed !"
    assert len(criteria_nominal) == len(nominal_tolerance), "Not enough or too many tolerances, please pass as many tolerance values as there are nominal criterias to consider"
    if any(column not in data.columns.values for column in criteria + criteria_nominal):
        raise ValueError("At least one column was not found in the dataframe")
    else:
        permutations_to_consider = get_permutations(len(data), n_groups, n_iter, exact)
        diff_scores = list()
        if scale:
            scaler = MinMaxScaler()
            data[criteria] = scaler.fit_transform(data[criteria].copy())
        for permutation in permutations_to_consider:
            data['subset'] = permutation
            total_diff = 0
            #Check that the tolerance is met for nominal criterias, if not go to next iteration
            if is_nominal_tolerance_met(data, criteria_nominal, nominal_tolerance):
                if len(criteria) == 0:
                    #If there are only nominal criterias to minimize, return the first grouping below tolerance
                    data['groups'] = data['subset']
                    return data
                for metric in equalize:
                    sum_of_columns_diff = 0
                    group_values = data.groupby(['subset'])[criteria].apply(metric)
                    for column in criteria:
                        largest_diff = max(group_values[column]) - min(group_values[column])
                        sum_of_columns_diff += largest_diff
                    #We keep the biggest difference between 2 groups for each criteria as the treshold
                    total_diff += sum_of_columns_diff
                diff_scores.append(total_diff)
                if len(diff_scores) == 1:
                    min_diff = diff_scores[0]
                    data['groups'] = data['subset']
                else:
                    if min_diff > min(diff_scores):
                        min_diff = min(diff_scores)
                        data['groups'] = data['subset']
        if scale:
            data[criteria] = scaler.inverse_transform(data[criteria].copy())
    if 'groups' not in data.columns.values:
        print("No grouping found, probably because of a low tolerance on nominal criterias")
        #TODO Delete the subset column even if a result is found
        data = data.drop(columns=['subset'])
    print(diff_scores)
    return data