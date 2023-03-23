import pickle5 as pickle
import gurobipy as gb

with open('G11\G1\B.pickle', 'rb') as handle:
    B = pickle.load(handle)

with open('G11\G1\R.pickle', 'rb') as handle:
    R = pickle.load(handle)

bin_set = B.keys()
item_set = R.keys()
a_set = [1,2]

m = gb.Model('2DBPP')

# Decision variables

p = {}
u = {}
r = {}
z_b = {}
z_t = {}
x_l = {}
x_r = {}
x = {}
z = {}

for i in item_set:
    z_b[i] = m.addVar(vtype=gb.GRB.INTEGER)
    z_t[i] = m.addVar(vtype=gb.GRB.INTEGER)
    x_l[i] = m.addVar(vtype=gb.GRB.INTEGER)
    x_r[i] = m.addVar(vtype=gb.GRB.INTEGER)
    for a in a_set:
        r[i,a] = m.addVar(vtype=gb.GRB.BINARY)
    for j in bin_set:
        p[i,j] = m.addVar(vtype=gb.GRB.BINARY)
        u[j] = m.addVar(vtype=gb.GRB.BINARY)
        for k in item_set:
            x[i,k,j] = m.addVar(vtype=gb.GRB.BINARY)
            z[i, k, j] = m.addVar(vtype=gb.GRB.BINARY)

