import pickle
import pandas as pd

with open('output.pkl', 'rb') as f:
    data = pickle.load(f)
labels = data['label']
ty = data['bet_type']
mean = data['mean']

cost = data['total_cost']
s=  set()
#total_profit =data['total_profit']
for i in range(0,len(labels)):
    if mean[i]>0.06:
        #s.add(labels[i])
        print('类型:',labels[i],'方向:',ty[i],'盈利率:',mean[i],'回测场数:',cost[i]//100)