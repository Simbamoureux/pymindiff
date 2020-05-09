import pandas as pd
from math import ceil
from itertools import permutations
import numpy as np
from pymindiff.scale import MinMaxScaler
from pymindiff.partitions import set_partitions, get_groups_column_from_partitions


#TODO Write unit tests
#TODO Work on performance
#TODO Don't rely on pandas ?
#TODO integrate to Pypi
#TODO Handle missing data

def is_nominal_tolerance_met(data : pd.DataFrame, criteria_nominal : list = [], nominal_tolerance : list = []):
    """
    Checks that the tolerances for categorical columns are met. The tolerance is defined as the sum of the maximum frequency deviation 
    between groups for each categorical column passed in criteria_nominal.

    Parameters
    ----------
    data : pd.DataFrame 
        Input data
        
    criteria_nominal : list(str)
        Names of the columns to use for minimizing differences between groups. Those columns must be categorical.

    nominal_tolerance : list(int)
        Maximum accepted frequency deviation between groups for categorical columns. Must be the same length as criteria_nominal and
        passed in the same order as the column names.

    Returns
    -------
    bool
        Wether the grouping satisfies the tolerance for categorical variables
    """
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
    """
    Computes the group configurations to be considered

    Parameters
    ----------
    data_length : int 
        Length of the input data (rows)
        
    n_groups : int
        Number of groups to create
    
    n_iter : int
        Number of iterations. Each iteration tests a random group assignment and computes the difference between groups regarding the specified columns/metrics.
        This argument is not used if exact is True

    exact : bool
        If true, n_iter will be ignored and every possible group configuration will be tested.
        WARNING : The number of possible group configuration grows exponentially with the number of rows and groups.
            Use only if the number of observations/groups is low

    Returns
    -------
    bool
        Wether the grouping satisfies the tolerance for categorical variables
    """
    draw_groups = ([i for i in range(n_groups)] * (ceil(data_length / n_groups)))[:data_length]
    if exact:
        partitions = [elem for elem in set_partitions([i for i in range(data_length)], n_groups)]
        return get_groups_column_from_partitions(partitions, data_length)
    else:
        return [np.random.choice(draw_groups, size=data_length, replace=False) for i in range(n_iter)]


def get_total_diff(data, criteria, equalize):
    """
    Computes the total difference between groups for the continuous criterias specified and functions to equalize.
    The total difference is definded as the sum of the largest differences between 2 groups for each metric and criteria.

    data : pd.DataFrame
        Input data

    criteria : list
        Names of the columns to use for minimizing the metric values between groups. Those columns must be continuous. For categorical columns,
        see the "criteria_nominal" argument. 

    equalize : list
        List of functions to equalize between groups. These functions must accept arrays/pd.Series as input and
        return a numerical value.

    Returns
    -------
    total_diff : float
        Total difference between groups for this group configuration
    """
    total_diff = 0
    if len(criteria) == 0:
        #If there are only nominal criterias to minimize, return the first grouping below tolerance
        return 0
    for metric in equalize:
        sum_of_columns_diff = 0
        group_values = data.groupby(['subset'])[criteria].apply(metric)
        for column in criteria:
            largest_diff = max(group_values[column]) - min(group_values[column])
            sum_of_columns_diff += largest_diff
        #We keep the biggest difference between 2 groups for each criteria as the treshold
        total_diff += sum_of_columns_diff
    return total_diff


def create_groups(data : pd.DataFrame, criteria : list = [], criteria_nominal : list = [], nominal_tolerance : list = [], n_groups : int = 2, n_iter : int = 100, equalize=[np.mean], scale=False, exact=False, verbose=False) -> pd.DataFrame:
    """
    Creates groups having minimal differences using a random sampling approach

    Parameters
    ----------
    data : pd.DataFrame
        Input data, must contain all columns cited in criteria and/or criteria_nominal. If data contains a column named "groups", 
        the function will use this column as a baseline to try to improve on. The "groups" column is a vector of integers indicating
        the group number of each observation (row).

    criteria : list
        Names of the columns to use for minimizing the metric values between groups. Those columns must be continuous. For categorical columns,
        see the "criteria_nominal" argument. 

    criteria_nominal : list(str)
        Names of the columns to use for minimizing differences between groups. Those columns must be categorical.

    nominal_tolerance : list(int)
        Maximum accepted frequency deviation between groups for categorical columns. Must be the same length as criteria_nominal and
        passed in the same order as the column names.

    n_groups : int
        Number of groups to create
    
    n_iter : int
        Number of iterations. Each iteration tests a random group assignment and computes the difference between groups regarding the specified columns/metrics.
        This argument is not used if exact is True

    equalize : list
        List of functions to equalize between groups. These functions must accept arrays/pd.Series as input and return a numerical value.

    scale : bool
        If true, the input numerical columns will be scaled in a Min-Max fashion.

    exact : bool
        If true, n_iter will be ignored and every possible group configuration will be tested.
        WARNING : The number of possible group configuration grows exponentially with the number of rows and groups.
            Use only if the number of observations/groups is low

    verbose : bool
        If true, enable verbose mode

    Returns
    -------
    pd.DataFrame
        The input dataframe with an additional column named "groups" containing the group number of each observation (row)
    """ 
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
        #Groups already exists -> Try to improve diff score
        if 'groups' in data.columns.values:
            diff_scores.append(get_total_diff(data, criteria, equalize))
            min_diff = diff_scores[0]
        for permutation in permutations_to_consider:
            data['subset'] = permutation
            #Check that the tolerance is met for nominal criterias, if not go to next iteration
            if is_nominal_tolerance_met(data, criteria_nominal, nominal_tolerance):
                diff_scores.append(get_total_diff(data, criteria, equalize))
                if len(diff_scores) == 1:
                    min_diff = diff_scores[0]
                    data['groups'] = data['subset']
                else:
                    if min_diff > min(diff_scores):
                        min_diff = min(diff_scores)
                        data['groups'] = data['subset']
                #Best possible value found
                if min_diff == 0:
                    break
        if scale:
            data[criteria] = scaler.inverse_transform(data[criteria].copy())
    data = data.drop(columns=['subset'])
    if 'groups' not in data.columns.values:
        print("No grouping found, probably because of a low tolerance on nominal criterias")
        return data
    if verbose:
        print(diff_scores)
        print(min(diff_scores))
    return data