import pandas as pd

data=pd.read_csv(r'command-structure-dataset/user-group-management.csv')

data['in'] =[i.lower() for i in data['in']]
data.to_csv('test.csv',index=False)