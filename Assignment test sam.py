import matplotlib.pyplot as plt
import pickle5 as pickle
import gurobipy as gb
import matplotlib.patches as mpatches

# Load pickle file, B = bins, R = items
with open('G11/G1/B.pickle', 'rb') as handle:
    B = pickle.load(handle)

# B = {0: (0, [300, 155, 2, 140, 0, 0, 0]), 1: (0, [300, 155, 2, 140, 0, 0, 0]), 2: (1, [192, 155, 2, 200, 0, 0, 0]), 3: (1, [192, 155, 2, 200, 0, 0, 0])}

with open('G11/G1/R.pickle', 'rb') as handle:
    R = pickle.load(handle)

#R ={0: (150, 28, 0, 0, 1, 0), 1: (150, 28, 0, 0, 0, 0), 2: (200, 30, 0, 1, 0, 0)} #, 3: (78, 62, 1, 0, 0, 1), 4: (97, 39, 1, 1, 0, 0), 5: (82, 29, 1, 0, 0, 0), 6: (91, 54, 1, 0, 0, 0), 7: (109, 24, 1, 0, 0, 0), 8: (60, 28, 1, 0, 0, 0), 9: (79, 42, 1, 0, 0, 0), 10: (111, 23, 0, 1, 0, 0), 11: (84, 46, 1, 0, 0, 0), 12: (51, 34, 1, 0, 0, 0), 13: (76, 28, 1, 0, 0, 0), 14: (93, 27, 1, 0, 0, 0), 15: (55, 35, 1, 0, 0, 0), 16: (67, 24, 0, 1, 0, 0), 17: (77, 55, 1, 0, 0, 0), 18: (98, 62, 1, 0, 0, 0), 19: (93, 54, 1, 0, 0, 0), 20: (93, 61, 1, 0, 0, 0), 21: (65, 41, 1, 0, 0, 0), 22: (117, 30, 1, 0, 0, 0), 23: (120, 26, 1, 1, 0, 1), 24: (112, 54, 0, 0, 0, 0)}

# Define sets
bin_set = B.keys()
item_set = list(R.keys()) #[0:11]
a_set = ['Original','Rotated']
l_set = [1,2]
print(item_set)
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
m1 = {}
o = {}
eta1 = {}
eta3 = {}
for j in bin_set:
    u[j] = m.addVar(obj=B[j][1][3], vtype=gb.GRB.BINARY, name='u_' + str(j))
for i in item_set:
    z_b[i] = m.addVar(vtype=gb.GRB.INTEGER, name = 'zb_'+str(i))
    z_t[i] = m.addVar(vtype=gb.GRB.INTEGER, name = 'zt_'+str(i))
    x_l[i] = m.addVar(vtype=gb.GRB.INTEGER, name = 'xl_'+str(i))
    x_r[i] = m.addVar(vtype=gb.GRB.INTEGER, name = 'xr_'+str(i))
    g[i] = m.addVar(vtype=gb.GRB.BINARY, name = 'g_'+str(i))
    for a in a_set:
        r[i,a] = m.addVar(vtype=gb.GRB.BINARY, name = 'r_'+str(i)+','+str(a))
    for j in bin_set:
        p[i,j] = m.addVar(vtype=gb.GRB.BINARY, name = 'p_'+str(i)+','+str(j))
    for k in item_set:
        print(i,k)
        xp[i, k] = m.addVar(vtype=gb.GRB.BINARY, name = 'xp_'+str(i)+','+str(k))
        zp[i, k] = m.addVar(vtype=gb.GRB.BINARY, name = 'zp_'+str(i)+','+str(k))
        v[i, k] = m.addVar(vtype=gb.GRB.INTEGER, name = 'v_'+str(i)+','+str(k))
        h[i, k] = m.addVar(vtype=gb.GRB.BINARY, name = 'h_'+str(i)+','+str(k))
        s[i, k] = m.addVar(vtype=gb.GRB.BINARY, name = 's_'+str(i)+','+str(k))
        m1[i, k] = m.addVar(vtype=gb.GRB.BINARY, name = 'm_'+str(i)+','+str(k))
        o[i, k] = m.addVar(vtype=gb.GRB.BINARY, name='o_' + str(i) + ',' + str(k))
        eta1[i, k] = m.addVar(vtype=gb.GRB.BINARY, name = 'eta1_'+str(i)+','+str(k))
        eta3[i, k] = m.addVar(vtype=gb.GRB.BINARY, name = 'eta3_'+str(i)+','+str(k))
        for l in l_set:
            beta[i, k, l] = m.addVar(vtype=gb.GRB.BINARY, name = 'beta'+str(i)+','+str(k)+','+str(l))

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
    m.addConstr(gb.quicksum(p[i,j] for j in bin_set), gb.GRB.EQUAL, 1, name = 'Constraint 4')
    # constraint 2
    m.addConstr(x_r[i], gb.GRB.LESS_EQUAL, gb.quicksum(B[j][1][0] * p[i,j] for j in bin_set), name = 'Constraint 5')
    # constraint 3
    m.addConstr(z_t[i], gb.GRB.LESS_EQUAL, gb.quicksum(B[j][1][1] * p[i,j] for j in bin_set), name = 'Constraint 7')
    # constraint 4
    m.addConstr(x_r[i] - x_l[i], gb.GRB.EQUAL, r[i,'Original'] * R[i][0] + r[i,'Rotated'] * R[i][1], name = 'Constraint 8')
    # constraint 5
    m.addConstr(z_t[i] - z_b[i], gb.GRB.EQUAL, r[i,'Original'] * R[i][1] + r[i,'Rotated'] * R[i][0], name = 'Constraint 10')
    # constraint 6
    m.addConstr(gb.quicksum(r[i,a] for a in a_set), gb.GRB.EQUAL, 1, name = 'Constraint 11')
    # constraint 11
    m.addConstr(r[i, 'Rotated'], gb.GRB.LESS_EQUAL, R[i][2], name = 'Constraint Rotate')
    for k in item_set:
        # constraint 8
        m.addConstr(x_r[k], gb.GRB.LESS_EQUAL, x_l[i] + (1 - xp[i, k]) * L, name = 'Constraint 14')
        # constraint 9
        m.addConstr(x_l[i] + 1, gb.GRB.LESS_EQUAL, x_r[k] + xp[i, k] * L, name = 'Constraint 15')
        # constraint 10
        m.addConstr(z_t[k], gb.GRB.LESS_EQUAL, z_b[i] + (1 - zp[i, k]) * H, name = 'Constraint 18')
        for j in bin_set:
            if i < k:
                # constraint 7
                m.addConstr(xp[i, k] + xp[k, i] + zp[i, k] + zp[k, i], gb.GRB.GREATER_EQUAL, (p[i, j] + p[k, j]) - 1, name = 'Constraint 13')
            # if i != k:
            #     # constraint 14
            #     m.addConstr(R[i][4] + R[k][5], gb.GRB.LESS_EQUAL, p[i, j] + p[k, j] - 1)

for i in item_set:
    # constraint 12
    m.addConstr(gb.quicksum(gb.quicksum(beta[i, j, k] for j in item_set) for k in l_set)+ 2 * g[i], gb.GRB.EQUAL, 2, name = 'Constraint Docent')

# Test constraints
for i in item_set:
    m.addConstr(gb.quicksum(beta[i,j,1] for j in item_set), gb.GRB.LESS_EQUAL, 1)
    m.addConstr(gb.quicksum(beta[i, j, 2] for j in item_set), gb.GRB.LESS_EQUAL, 1)

for k in item_set:
    # constraint 13
    m.addConstr(gb.quicksum(s[i, k] for i in item_set), gb.GRB.LESS_EQUAL, len(item_set) * (1 - R[k][3]), name = 'Constraint 51')

# stability constraints
for i in item_set:
    # constraint 15
    m.addConstr(z_b[i], gb.GRB.LESS_EQUAL, (1 - g[i]) * H, name = 'Constraint 27')
    for k in item_set:
        #Test constraint

        # constraint 16
        m.addConstr(z_t[k] - z_b[i], gb.GRB.LESS_EQUAL, v[i, k], name = 'Constraint 28')
        # constraint 17
        m.addConstr(z_b[i] - z_t[k], gb.GRB.LESS_EQUAL, v[i, k], name = 'Constraint 29')

        # TEST CONSTRAINTS
        m.addConstr(v[i,k], gb.GRB.LESS_EQUAL, z_t[k]-z_b[i] + 2*H*(1-m1[i,k]), name = 'Constraint 30')
        m.addConstr(v[i,k], gb.GRB.LESS_EQUAL, z_b[i]-z_t[k]+2*H*m1[i,k], name = 'Constraint 31')


        # constraint 18
        m.addConstr(h[i, k], gb.GRB.LESS_EQUAL, v[i, k], name = 'Constraint 32')
        # constraint 19
        m.addConstr(v[i, k], gb.GRB.LESS_EQUAL, h[i, k] * H, name = 'Constraint 33')
        # Test constraint

        m.addConstr(1-s[i, k], gb.GRB.LESS_EQUAL, h[i, k]+o[i, k], name = 'Test constraint 35')
        m.addConstr(h[i, k]+o[i, k], gb.GRB.LESS_EQUAL, 2*(1-s[i, k]), name='Test constraint 35-2')
        m.addConstr(o[i,k], gb.GRB.EQUAL, xp[i,k]+xp[k,i])

        for j in bin_set:
            # constraint 20
            m.addConstr(p[i, j] - p[k, j], gb.GRB.LESS_EQUAL, 1 - s[i, k], name = 'Constraint 36')
            # constraint 21
            m.addConstr(p[k, j] - p[i, j], gb.GRB.LESS_EQUAL, 1 - s[i, k], name = 'Constraint 37')
        for l in l_set:
            # constraint 22
            m.addConstr(beta[i, k, l], gb.GRB.LESS_EQUAL, s[i, k], name = 'Constraint 38')

        # Test constraints
        m.addConstr(eta1[i,k], gb.GRB.LESS_EQUAL, 1-beta[i,k,1], name = 'Constraint 39')
        m.addConstr(eta3[i,k], gb.GRB.LESS_EQUAL, 1-beta[i,k,2], name = 'Constraint 40')

        # constraint 23
        m.addConstr(x_l[k], gb.GRB.LESS_EQUAL, x_l[i] + eta1[i, k] * L, name = 'Constraint eta1')
        # constraint 24
        m.addConstr(x_r[i], gb.GRB.LESS_EQUAL, x_r[k] + eta3[i, k] * L, name = 'Constraint eta3')
        #m.addConstr(x_r[i], gb.GRB.GREATER_EQUAL, x_l[k] - (eta3[i,k])*L) # This one is the latest test

        #Constraint Radioactive/perishable
        model.addConstr(R[i][4] * p[i, j] + R[k][5] * p[k, j], gb.GRB.LESS_EQUAL, 1)


print('ADDED CONSTRAINTS')

m.update()
m.setParam('TimeLimit', 2*60*60)
m.optimize()
m.write('betas.lp')
m.write('betas.sol')
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
                x_text = x_r[i].X - (x_r[i].X - x_l[i].X)/2
                z_text = z_t[i].X - (z_t[i].X - z_b[i].X)/2
                plt.text(x_text,z_text, i)
        plt.show()

# m.params.LogFile='2DBBP.log'


# plt.figure()
# plt.plot([0, 0, B[0][1][0], B[0][1][0], 0], [0, B[0][1][1], B[0][1][1], 0, 0])
# x = [x_l[0].X, x_r[0].X, x_r[0].X, x_l[0].X, x_l[0].X]
# z = [z_b[0].X, z_b[0].X, z_t[0].X, z_t[0].X, z_b[0].X]
# plt.plot(x, z)
#
# x = [x_l[24].X, x_r[24].X, x_r[24].X, x_l[24].X, x_l[24].X]
# z = [z_b[24].X, z_b[24].X, z_t[24].X, z_t[24].X, z_b[24].X]
# plt.plot(x, z)