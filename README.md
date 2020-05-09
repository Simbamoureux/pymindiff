# pymindiff

pymindiff is a Python 3 package that can be used to assign elements to a
specified number of groups and minimize differences between created
groups.

This package is inspired (but not a direct portage !) by the equivalent package in R : https://github.com/m-Py/minDiff.

## Installation

## Usage

``` 
from pymindiff.groups import create_groups

res = create_groups(data, criteria=['example'], n_groups=2, n_iter = 100, equalize = [np.mean])
```

To reproduce the examples found in this documentation, use the Tips dataset
```
import pandas as pd

data = pd.read_csv(
    "https://raw.githubusercontent.com/pandas-dev/pandas/master/doc/data/tips.csv",
)
```

The `tips` dataset contains study data regarding the amount tipped in restaurant depending on different factors.
In this data, each row represents a customer, and information regarding this customer
 and the amount tipped and billed by the restaurant.

Imagine you wish to assign customers to three different categories and want to create a similar 
groups of customers in each category. As a first step, we might want to match average customer tip values.

To do so, we pass our data set to the function `create_groups` and
specify which variable should be made equal in how many sets.

```
result = create_groups(data, criteria=['tip'], n_groups=3, n_iter=100)
```

By passing the column `tip` to the argument `criteria` we inform
`create_groups` that tip is a continuous variable, for which we want to
minimize the differences between groups. `create_groups` returns a
`pandas.DataFrame` that is saved into the object `result`. `result` is actually
the same as the input data, but it has one additional column:
`groups` - this is the group assignment variable that was created.

Let's see the result : 

```
result.groupby('groups').tip.mean()

> groups
> 0    2.992195
> 1    2.987531
> 2    3.015185
> Name: tip, dtype: float64
```

Not bad ! But how did this work ? In the function call above, we specified another parameter, `n_iter=100` (which is also the default value if we do not specify a value for n_iter). This means that the function randomly assigned all cases (i.e. customers) to three groups 100 times, and returned the most equal group assignment. In the default case, what is considered most equal is the assignment that has the minimum difference in group means; but we can specify different criteria if we want to (see below). By varying the parameter `n_iter` we can increase our chances of creating equal groups. If we conduct 10,000 repetitions, the groups will be very similar with regards to tip. Note that it is possible to pass a data set that has been optimized previously; in this case, the program does not start all over, but only tries find more similar groups than the previous best assignment:

### Considering multiple columns

We can pass more than one criteria to `create_groups`. Let's imagine we
also want customers to have been billed a similar amount:

```
result = create_groups(data, criteria=['tip', 'total_bill'], n_groups=3, n_iter=100)

result.groupby('groups')[['tip', 'total_bill']].mean()

>	tip	total_bill
> groups		
> 0	3.037927	19.656220
> 1	3.036667	19.661852
> 2	2.919753	20.041358
```

### Considering categorical columns

We might also want to make groups such that there is an even number of smokers in each group. Using the `criteria_nominal` and `nominal_tolerance` arguments, we can specify which categorical columns should be used, and what is the maximal tolerated frequency deviation between groups for each categorical variable.

For instance, if we choose to create two groups with a similar number of smokers we could use

```
result = create_groups(data, criteria_nominal=['smoker'], nominal_tolerance=[1], n_groups=2, n_iter=100)

result.groupby(['groups', 'smoker']).size()

> groups  smoker
> 0       No        76
>         Yes       46
> 1       No        75
>         Yes       47
> dtype: int64
```

If we wish to limit the deviation in frequency of smokers to 3 between groups, we can replace the `nominal_tolerance` with the value `[3]`

The `nominal_tolerance` argument takes an array of the same length as `criteria_nominal` containing the
 maximal frequency deviation for each column between groups.

### Use more than one categorical column

It is possible to use multiple categorical columns the same way you would use multiple continuous columns : 

```
result = create_groups(data, criteria_nominal=['smoker', 'sex'], nominal_tolerance=[4,2],n_groups=2, n_iter=100)
```

*WARNING* : Sometimes, it is impossible to find a group verifying the tolerance constraint defined,
especially when there are numerous categorical columns to consider, prefer starting with large
`nominal_tolerances` values and reducing it afterwards

### Specifying the equalizing function

You can specify which equalizing function to use by passing it in the `equalize` argument. The function will 
be used in a groupby operation and thus must allow for a pd.Serie or np.array input and return a single value.

Here is an example using the numpy.sum function :

```
result = create_groups(data, criteria=['tip'], n_groups=3, n_iter=100, equalize=[numpy.sum])

result.groupby('groups').tip.sum()

> groups
> 0    244.06
> 1    244.65
> 2    242.87
> Name: tip, dtype: float64
```

*WARNING* : Be careful of the way the equalizing functions handle missing data, this can cause unexpected behaviors.

### Using more than one function

Maybe you realized that a list is actually passed into the `equalize` argument and not a function, this is because we can pass as many equalizing functions as needed.

Imagine we wish to create groups with similar average tip values, but also want to make sure that the standard deviation of tips in each group is similar : 

```
result = create_groups(data, criteria=['tip'], n_groups=3, n_iter=100, equalize=[numpy.sum, numpy.std])
```

### Finding the exact solution

Until then, we minimized the difference between groups by randomly assigning customers to groups and checking which random grouping returned the lowest difference. But it is also possible to compute the exact solution that will try every possible group configuration to find the best one in regard to the criterias to minimize. This can be done by setting the `exact` argument to `True`. As the number of possible assignments grow exponentially with  the number of customers (rows) and groups, this option is reserved for small datasets.

This code produces the best assignment for the first 20 customers into 2 groups.

```
result = create_groups(data.iloc[:20], criteria=['tip'], n_groups=2, exact=True)
result.groupby('groups').tip.mean()

> groups
> 0    2.928
> 1    2.928
> Name: tip, dtype: float64

CPU times: user 6.03 s, sys: 127 ms, total: 6.15 s
```

WARNING : When conducting random group assignments, the number of customers in each group will be made as 
equal as possible, but when `exact=True`, the function will return the best possible assignment without trying to 
equalize the number of customers in each group.

### Scaling the continuous columns

It is useful to scale the continuous criteria to avoid that columns with large values make up for most 
of the difference between groups. For instance, let's say we wish to minimize the difference between average `tips` and `total_bill` value between groups, tips' unit is in `$`, and total bill's unit is in `cents`.

Most of the time, due to total bill's values being bigger, the difference between the average total bill for each group will be larger than the difference between tips. This causes total bill to be more or less the only criteria considered when minimizing difference between groups. This is the case because of how the difference between groups is calculated (see below). Scaling the columns addresses this problem by scaling the columns before computing the differences between groups. The output data remains the same because the data is descaled before being returned.

## How is the difference value of an assignment calculated ?

The difference between groups is calculated by summing the maximum difference between groups over all criterias and all equalizing functions. This operation is done only for assignments that respect the given tolerance over categorical columns (`criteria_nominal` and `nominal_tolerance` arguments)

## Feedback / Reporting bugs / Contributing / Get in touch

This package was done as a side project on my free time, and may receive changes in the future. Any feedback/Bug report/Contribution is appreciated.
Get in touch at clementlombard@orange.fr or directly on Github.