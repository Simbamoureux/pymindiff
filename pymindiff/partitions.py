def set_partitions(iterable, k=None):
    """
    Yield the set partitions of *iterable* into *k* parts. Set partitions are
    not order-preserving.

    >>> iterable = 'abc'
    >>> for part in set_partitions(iterable, 2):
    ...     print([''.join(p) for p in part])
    ['a', 'bc']
    ['ab', 'c']
    ['b', 'ac']


    If *k* is not given, every set partition is generated.

    >>> iterable = 'abc'
    >>> for part in set_partitions(iterable):
    ...     print([''.join(p) for p in part])
    ['abc']
    ['a', 'bc']
    ['ab', 'c']
    ['b', 'ac']
    ['a', 'b', 'c']

    """
    L = list(iterable)
    n = len(L)
    if k is not None:
        if k < 1:
            raise ValueError(
                "Can't partition in a negative or zero number of groups"
            )
        elif k > n:
            return

    def set_partitions_helper(L, k):
        n = len(L)
        if k == 1:
            yield [L]
        elif n == k:
            yield [[s] for s in L]
        else:
            e, *M = L
            for p in set_partitions_helper(M, k - 1):
                yield [[e], *p]
            for p in set_partitions_helper(M, k):
                for i in range(len(p)):
                    yield p[:i] + [[e] + p[i]] + p[i + 1 :]

    if k is None:
        for k in range(1, n + 1):
            yield from set_partitions_helper(L, k)
    else:
        yield from set_partitions_helper(L, k)


def get_groups_column_from_partitions(partitions, data_length):  
    """
    Transforms the partitions returned by set_partitions into vectors containing the group numbers

    Parameters
    ----------
    partitions : list 
        list of partition values returned by the set_partitions function
        
    data_length : int
        Number of lines in the input dataframe

    Returns
    -------
    list
        A list containing all the groups column values corresponding to each partition
    """
    permutations_values = [[i for i in range(data_length)] for elem in partitions]
    for i in range(len(partitions)):
        for j in permutations_values[i]:
            value = permutations_values[i][j]
            for k in range(len(partitions[i])):
                team = partitions[i][k]
                if value in team:
                    permutations_values[i][j] = k
    return permutations_values