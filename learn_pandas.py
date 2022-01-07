import pandas as pd
import numpy as np

# 'MS' = month start
dates = pd.date_range(start='1/1/2018', end='1/08/2020', freq='MS')

dates = pd.date_range('1/1/2000', periods=8)

df = pd.DataFrame(np.random.randn(8, 4), index=dates, columns=['A', 'B', 'C', 'D'])