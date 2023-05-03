import matplotlib.pyplot as plt
import pickle5 as pickle
import gurobipy as gb
import matplotlib.patches as mpatches
import matplotlib.image as mpimg
import numpy as np
import random

# Load pickle file, B = bins, R = items
with open('G11/G1/B.pickle', 'rb') as handle:
    B = pickle.load(handle)

# B = {0: (0, [300, 155, 2, 140, 0, 0, 0]), 1: (0, [300, 155, 2, 140, 0, 0, 0]), 2: (1, [192, 155, 2, 200, 0, 0, 0]), 3: (1, [192, 155, 2, 200, 0, 0, 0])}

with open('G11/G1/R.pickle', 'rb') as handle:
    R = pickle.load(handle)


#R ={0: (150, 28, 0, 0, 1, 0), 1: (150, 28, 0, 0, 0, 0), 2: (200, 30, 0, 1, 0, 0), 3: (78, 62, 1, 0, 0, 1), 4: (97, 39, 1, 1, 0, 0), 5: (82, 29, 1, 0, 0, 0), 23: (120, 26, 1, 1, 0, 1)}#, 6: (91, 54, 1, 0, 0, 0), 7: (109, 24, 1, 0, 0, 0), 8: (60, 28, 1, 0, 0, 0), 9: (79, 42, 1, 0, 0, 0), 10: (111, 23, 0, 1, 0, 0), 11: (84, 46, 1, 0, 0, 0)}#, 12: (51, 34, 1, 0, 0, 0), 13: (76, 28, 1, 0, 0, 0), 14: (93, 27, 1, 0, 0, 0), 15: (55, 35, 1, 0, 0, 0), 16: (67, 24, 0, 1, 0, 0), 17: (77, 55, 1, 0, 0, 0), 18: (98, 62, 1, 0, 0, 0), 19: (93, 54, 1, 0, 0, 0), 20: (93, 61, 1, 0, 0, 0), 21: (65, 41, 1, 0, 0, 0), 22: (117, 30, 1, 0, 0, 0), 23: (120, 26, 1, 1, 0, 1), 24: (112, 54, 0, 0, 0, 0)}

# Define sets
bin_set = B.keys()
item_set = list(R.keys())[0:10]
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
    z_b[i] = m.addVar(vtype=gb.GRB.CONTINUOUS, name = 'zb_'+str(i))
    z_t[i] = m.addVar(vtype=gb.GRB.CONTINUOUS, name = 'zt_'+str(i))
    x_l[i] = m.addVar(vtype=gb.GRB.CONTINUOUS, name = 'xl_'+str(i))
    x_r[i] = m.addVar(vtype=gb.GRB.CONTINUOUS, name = 'xr_'+str(i))
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
            m.addConstr(R[i][4] * p[i, j] + R[k][5] * p[k, j], gb.GRB.LESS_EQUAL, 1)

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

print('ADDED CONSTRAINTS')
m.update()
m.setParam('Timelimit', 1.5*60*60)
m.optimize()
m.update()

for i in item_set:
    for k in item_set:
        #Constraint Radioactive/perishable
        for j in bin_set:
            m.addConstr(R[i][4] * p[i, j] + R[k][5] * p[k, j], gb.GRB.LESS_EQUAL, 1, name = 'Perish constraint')


print('ADDED per/rad CONSTRAINTS')

m.update()
m.setParam('TimeLimit', 0.5*60*60)
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

# define the radioactive image file name and read the image
img_radio = 'radioactive.png'
img_rad = mpimg.imread(img_radio)

# define the perishable image file name and read the image
img_perisc = 'perishable.jpg'
img_per = mpimg.imread(img_perisc)

# define the fragile image file name and read the image
img_fragile = 'fragile_test.png'
img_frag = mpimg.imread(img_fragile)

for bin in u:
    if u[bin].X == 1:
        plt.figure()
        plt.ylim(0, B[bin][1][1])
        plt.xlim(0, B[bin][1][0])
        plt.title('ULD %s' %(str(bin)))
        # plt.plot([0,0,B[bin][1][0],B[bin][1][0], 0], [0, B[bin][1][1],B[bin][1][1], 0, 0])
        for i in item_set:
            if p[i, bin].X == 1:
                x = [x_l[i].X, x_r[i].X, x_r[i].X, x_l[i].X, x_l[i].X]
                z = [z_b[i].X, z_b[i].X, z_t[i].X, z_t[i].X, z_b[i].X]
                if R[i][5] == 1:
                    # fill the plot with the radioactive image
                    plt.imshow(img_rad, extent=(x_l[i].X, x_r[i].X, z_b[i].X, z_t[i].X), alpha=0.8)
                elif R[i][4] == 1:
                    # fill the plot with the perishable image
                    plt.imshow(img_per, extent=(x_l[i].X, x_r[i].X, z_b[i].X, z_t[i].X), alpha=0.8)
                else:
                    # Generate a random RGB color
                    color = tuple(random.uniform(0, 1) for i in range(3))
                    rect = plt.Rectangle((x_l[i].X, z_b[i].X), x_r[i].X - x_l[i].X, z_t[i].X - z_b[i].X,
                                         facecolor=color, alpha=0.5)
                    plt.gca().add_patch(rect)
                if R[i][3] == 1:
                    # define the limits of the top right corner of the x and z coordinates
                    x_topright = x_r[i].X
                    z_topright = z_t[i].X

                    # calculate the size of the square image based on the smaller dimension of x and z
                    img_size = min(x_topright - x_l[i].X, z_topright - z_b[i].X)
                    img_size = img_size * 1.55

                    # calculate the center of the square image
                    x_center = x_topright - img_size / 2
                    z_center = z_topright - img_size / 2

                    # fill the plot with the fragile image
                    plt.imshow(img_frag, extent=(x_center, x_topright, z_center, z_topright), alpha=1, zorder=10)
                # create outlining
                plt.plot(x,z, 'k')

                # create textblock. if not rotatable, make red
                if R[i][2] != 1:
                    if r[i,'Rotated'].X == 1:
                        x_text = x_r[i].X - (x_r[i].X - x_l[i].X) / 2
                        z_text = z_t[i].X - (z_t[i].X - z_b[i].X) / 2
                        plt.text(x_text, z_text, str(i) + ', R', color='black',
                                 bbox=dict(facecolor='#FF8888', edgecolor='black', boxstyle='round,pad=0.3'))
                    else:
                        x_text = x_r[i].X - (x_r[i].X - x_l[i].X) / 2
                        z_text = z_t[i].X - (z_t[i].X - z_b[i].X) / 2
                        plt.text(x_text, z_text, i, color='black',
                                 bbox=dict(facecolor='#FF8888', edgecolor='black', boxstyle='round,pad=0.3'))
                else:
                    if r[i,'Rotated'].X == 1:
                        x_text = x_r[i].X - (x_r[i].X - x_l[i].X)/2
                        z_text = z_t[i].X - (z_t[i].X - z_b[i].X)/2
                        plt.text(x_text, z_text, str(i) + ', R', color='black',
                                 bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
                    else:
                        x_text = x_r[i].X - (x_r[i].X - x_l[i].X)/2
                        z_text = z_t[i].X - (z_t[i].X - z_b[i].X)/2
                        plt.text(x_text, z_text, i, color='black',
                                 bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
        plt.ylabel('Height')
        plt.xlabel('Length')
        plt.grid()
        plt.show()

##Create Pickle file
#Make list of IDs of bins used

bins_used = []
for i in bin_set:
    if u[i].X == 1:
        bins_used.append(i)

print('bins used', bins_used)
#Create dict where keys are the IDs of the bins used, and the values are IDs of items
dict_bins_items = {}
for j in bin_set:
    if u[j].X == 1:
        item_list = []
        for i in item_set:
            if p[i,j].X == 1:
                item_list.append(i)
        dict_bins_items[j] = item_list
print('dict items in bins',dict_bins_items)
#Create dict where key is item ID and values are list of 4 elements containing
    #horizontal position of lower left vertex, vertical position of lower left vertex
    #horizontal extention and vertical extention

dict_item_location = {}
for i in item_set:
    item_location = []
    item_location.append(x_l[i].X)
    item_location.append(z_b[i].X)
    horizontal_extention = x_r[i].X - x_l[i].X
    vertical_extention = z_t[i].X - z_b[i].X
    item_location.append(horizontal_extention)
    item_location.append(vertical_extention)
    dict_item_location[i] = item_location

print('item locations', dict_item_location)

#Create pickle files

with open('bins_used.pickle','wb') as handle:
    pickle.dump(bins_used,handle,protocol=pickle.HIGHEST_PROTOCOL)

with open('items_in_bins.pickle','wb') as handle:
    pickle.dump(dict_bins_items,handle,protocol=pickle.HIGHEST_PROTOCOL)

with open('item_location.pickle','wb') as handle:
    pickle.dump(dict_item_location,handle,protocol=pickle.HIGHEST_PROTOCOL)


m.params.LogFile='2DBBP.log'
