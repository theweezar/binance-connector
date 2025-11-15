import pandas as pd

data = {'Value': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
df = pd.DataFrame(data)

# Calculate a 3-period rolling mean
df['Rolling_Mean'] = df['Value'].rolling(window=2).sum()

df['Another'] = df['Value'] > 2 * 1.5

print(df)
