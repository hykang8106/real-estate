import pandas as pd
import numpy as np

# 'MS' = month start
dates = pd.date_range(start='1/1/2018', end='1/08/2020', freq='MS')
dates = pd.date_range(start='20180101', end='20200801', freq='MS')

dates = pd.date_range('1/1/2000', periods=8)

df = pd.DataFrame(np.random.randn(8, 4), index=dates, columns=['A', 'B', 'C', 'D'])

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.ticker import PercentFormatter

# Create a random number generator with a fixed seed for reproducibility
rng = np.random.default_rng(19680801)

N_points = 100000
n_bins = 20

dist1 = rng.standard_normal(N_points)

plt.figure()

plt.hist(dist1, bins=n_bins)
plt.show(block=False)


'''
# Generate two normal distributions
dist1 = rng.standard_normal(N_points)
dist2 = 0.4 * rng.standard_normal(N_points) + 5

fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)

# We can set the number of bins with the *bins* keyword argument.
axs[0].hist(dist1, bins=n_bins)
axs[1].hist(dist2, bins=n_bins)

plt.show(block=False)
'''