import matplotlib.pyplot as plt
import pickle5 as pickle
import gurobipy as gb
import matplotlib.patches as mpatches

# Load pickle file, B = bins, R = items
with open('G11\G1\B.pickle', 'rb') as handle:
    B = pickle.load(handle)

# B = {0: (0, [300, 155, 2, 140, 0, 0, 0]), 1: (0, [300, 155, 2, 140, 0, 0, 0]), 2: (1, [192, 155, 2, 200, 0, 0, 0]), 3: (1, [192, 155, 2, 200, 0, 0, 0])}

with open('G11\G1\R.pickle', 'rb') as handle:
    R = pickle.load(handle)

# R ={0: (118, 28, 1, 0, 1, 0), 1: (105, 46, 1, 1, 0, 0), 2: (97, 57, 1, 1, 0, 0), 3: (78, 62, 1, 0, 0, 1), 4: (97, 39, 1, 1, 0, 0), 5: (82, 29, 1, 0, 0, 0), 6: (91, 54, 1, 0, 0, 0), 7: (109, 24, 1, 0, 0, 0), 8: (60, 28, 1, 0, 0, 0), 9: (79, 42, 1, 0, 0, 0), 10: (111, 23, 0, 1, 0, 0), 11: (84, 46, 1, 0, 0, 0), 12: (51, 34, 1, 0, 0, 0), 13: (76, 28, 1, 0, 0, 0), 14: (93, 27, 1, 0, 0, 0), 15: (55, 35, 1, 0, 0, 0), 16: (67, 24, 0, 1, 0, 0), 17: (77, 55, 1, 0, 0, 0), 18: (98, 62, 1, 0, 0, 0), 19: (93, 54, 1, 0, 0, 0), 20: (93, 61, 1, 0, 0, 0), 21: (65, 41, 1, 0, 0, 0), 22: (117, 30, 1, 0, 0, 0), 23: (120, 26, 1, 1, 0, 1), 24: (112, 54, 0, 0, 0, 0)}

# Define sets
bin_set = B.keys()
item_set = R.keys()
a_set = ['Original','Rotated']
l_set = [1, 2]

L = 0
H = 0
for bin in bin_set:
    if B[bin][1][0] > L:
        L = B[bin][1][0]
    if B[bin][1][1] > H:
        H = B[bin][1][1]

m = gb.Model('2DBPP')

# Decision variables

p = {}
u = {}
r = {}
z_b = {}
z_t = {}
x_l = {}
x_r = {}
xp = {}
zp = {}
g = {}
beta = {}
v = {}
h = {}
s = {}
eta1 = {}
eta3 = {}

for i in item_set:
    z_b[i] = m.addVar(vtype=gb.GRB.INTEGER)
    z_t[i] = m.addVar(vtype=gb.GRB.INTEGER)
    x_l[i] = m.addVar(vtype=gb.GRB.INTEGER)
    x_r[i] = m.addVar(vtype=gb.GRB.INTEGER)
    g[i] = m.addVar(vtype=gb.GRB.BINARY)
    for a in a_set:
        r[i,a] = m.addVar(vtype=gb.GRB.BINARY)
    for j in bin_set:
        p[i,j] = m.addVar(vtype=gb.GRB.BINARY)
        u[j] = m.addVar(obj=B[j][1][3],vtype=gb.GRB.BINARY)
        for k in item_set:
            xp[i, k] = m.addVar(vtype=gb.GRB.BINARY)
            zp[i, k] = m.addVar(vtype=gb.GRB.BINARY)
            v[i, k] = m.addVar(vtype=gb.GRB.INTEGER)
            h[i, k] = m.addVar(vtype=gb.GRB.BINARY)
            s[i, k] = m.addVar(vtype=gb.GRB.BINARY)
            eta1[i, k] = m.addVar(vtype=gb.GRB.BINARY)
            eta3[i, k] = m.addVar(vtype=gb.GRB.BINARY)
            for l in l_set:
                beta[i, k, l] = m.addVar(vtype=gb.GRB.BINARY)

print('ADDED DECISION VARIABLES')

m.update()
m.setObjective(m.getObjective(), gb.GRB.MINIMIZE)

print('OBJECTIVE SET')
# Cost minimization

for j in bin_set:
    # constraint 0
    m.addConstr(gb.quicksum(R[i][0] * R[i][1] * p[i, j] for i in item_set), gb.GRB.LESS_EQUAL, B[j][1][0] * B[j][1][1] * u[j])

for i in item_set:
    # constraint 1
    m.addConstr(gb.quicksum(p[i,j] for j in bin_set), gb.GRB.EQUAL, 1)
    # constraint 2
    m.addConstr(x_r[i], gb.GRB.LESS_EQUAL, gb.quicksum(B[j][1][0] * p[i,j] for j in bin_set))
    # constraint 3
    m.addConstr(z_t[i], gb.GRB.LESS_EQUAL, gb.quicksum(B[j][1][1] * p[i,j] for j in bin_set))
    # constraint 4
    m.addConstr(x_r[i] - x_l[i], gb.GRB.EQUAL, r[i,'Original'] * R[i][0] + r[i,'Rotated'] * R[i][1])
    # constraint 5
    m.addConstr(z_t[i] - z_b[i], gb.GRB.EQUAL, r[i,'Original'] * R[i][1] + r[i,'Rotated'] * R[i][0])
    # constraint 6
    m.addConstr(gb.quicksum(r[i,a] for a in a_set), gb.GRB.EQUAL, 1)
    # constraint 11
    m.addConstr(r[i, 'Rotated'], gb.GRB.LESS_EQUAL, R[i][2])
    for k in item_set:
        # constraint 8
        m.addConstr(x_r[k], gb.GRB.LESS_EQUAL, x_l[i] + (1 - xp[i, k]) * L)
        # constraint 9
        m.addConstr(x_l[i] + 1, gb.GRB.LESS_EQUAL, x_r[k] + xp[i, k] * L)
        # constraint 10
        m.addConstr(z_t[k], gb.GRB.LESS_EQUAL, z_b[i] + (1 - zp[i, k]) * H)
        for j in bin_set:
            if i < k:
                # constraint 7
                m.addConstr(xp[i, k] + xp[k, i] + zp[i, k] + zp[k, i], gb.GRB.GREATER_EQUAL, (p[i, j] + p[k, j]) - 1)
            # if i != k:
            #     # constraint 14
            #     m.addConstr(R[i][4] + R[k][5], gb.GRB.LESS_EQUAL, p[i, j] + p[k, j] - 1)

for i in item_set:
    # constraint 12
    m.addConstr(gb.quicksum(gb.quicksum(beta[i, j, k] + 2 * g[i] for j in bin_set) for k in [1,2]), gb.GRB.EQUAL, 2)

for k in item_set:
    # constraint 13
    m.addConstr(gb.quicksum(s[i, k] for i in item_set), gb.GRB.LESS_EQUAL, len(item_set) * (1 - R[k][3]))

# stability constraints
for i in item_set:
    # constraint 15
    m.addConstr(z_b[i], gb.GRB.LESS_EQUAL, (1 - g[i]) * H)
    for k in item_set:
        # constraint 16
        m.addConstr(z_t[k] - z_b[i], gb.GRB.LESS_EQUAL, v[i, k])
        # constraint 17
        m.addConstr(z_b[i] - z_t[k], gb.GRB.LESS_EQUAL, v[i, k])
        # constraint 18
        m.addConstr(h[i, k], gb.GRB.LESS_EQUAL, v[i, k])
        # constraint 19
        m.addConstr(v[i, k], gb.GRB.LESS_EQUAL, h[i, k] * H)
        for j in bin_set:
            # constraint 20
            m.addConstr(p[i, j] - p[k, j], gb.GRB.LESS_EQUAL, 1 - s[i, k])
            # constraint 21
            m.addConstr(p[k, j] - p[i, j], gb.GRB.LESS_EQUAL, 1 - s[i, k])
        for l in l_set:
            # constraint 22
            m.addConstr(beta[i, k, l], gb.GRB.LESS_EQUAL, s[i, k])
        # constraint 23
        m.addConstr(x_l[k], gb.GRB.LESS_EQUAL, x_l[i] + eta1[i, k] * L)
        # constraint 24
        m.addConstr(x_r[i], gb.GRB.LESS_EQUAL, x_r[k] + eta3[i, k] * L)

print('ADDED CONSTRAINTS')

m.update()
m.optimize()

status = m.status

if status == gb.GRB.Status.UNBOUNDED:
    print('The model cannot be solved because it is unbounded')

elif status == gb.GRB.Status.OPTIMAL or True:
    f_objective = m.objVal
    print('***** RESULTS ******')
    print('\nObjective Function Value: \t %g' % f_objective)

elif status != gb.GRB.Status.INF_OR_UNBD and status != gb.GRB.Status.INFEASIBLE:
    print('Optimization was stopped with status %d' % status)


for bin in u:
    if u[bin].X == 1:
        plt.figure()
        plt.plot([0,0,B[bin][1][0],B[bin][1][0], 0], [0, B[bin][1][1],B[bin][1][1], 0, 0])
        for i in item_set:
            if p[i, bin].X == 1:
                x = [x_l[i].X, x_r[i].X, x_r[i].X, x_l[i].X, x_l[i].X]
                z = [z_b[i].X, z_b[i].X, z_t[i].X, z_t[i].X, z_b[i].X]
                plt.plot(x,z)
        plt.show()

m.params.LogFile='2DBBP.log'


# plt.figure()
# plt.plot([0, 0, B[0][1][0], B[0][1][0], 0], [0, B[0][1][1], B[0][1][1], 0, 0])
# x = [x_l[0].X, x_r[0].X, x_r[0].X, x_l[0].X, x_l[0].X]
# z = [z_b[0].X, z_b[0].X, z_t[0].X, z_t[0].X, z_b[0].X]
# plt.plot(x, z)
#
# x = [x_l[24].X, x_r[24].X, x_r[24].X, x_l[24].X, x_l[24].X]
# z = [z_b[24].X, z_b[24].X, z_t[24].X, z_t[24].X, z_b[24].X]
# plt.plot(x, z)