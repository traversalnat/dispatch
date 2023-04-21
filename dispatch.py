import gurobipy as grb
from gurobipy import *
import re

__author__ = "Zhihui Zhang"
__version__ = "1.0"
__email__ = "1726546320 [at] qq [dot] com"


# Create a new model
model = Model()

# 3 edge server (include MEC)
prices = [3.2, 2.3, 2.5]
# frequence，节点速率(Hz)
freq = [300, 100, 200]
# task size,  任务大小(Hz)
task_size = [10000, 8000, 7200, 6900, 2100, 3212, 3242, 8981, 98128]
# p_ij, 任务j在节点i上的运行速度
rates = []
for i in freq:
    r = []
    for j in task_size:
        if i == 0:
            r.append(0)
        else:
            r.append(j/i)
    rates.append(r)

# 任务数量
n_tasks = len(task_size)
# 节点数量
m_edge = len(freq)

# [qi, ] 常数
q = prices

# [[pij, ], ] 常数
p = rates

x = model.addVars(m_edge, n_tasks, n_tasks, lb=0, ub=1, vtype=GRB.CONTINUOUS, name="X_ikj")
model.update()

# C1约束
for j in range(n_tasks):
    model.addConstr(quicksum(x[i, k, j]
                             for i in range(m_edge)
                             for k in range(n_tasks)) >= 1)
model.update()
# C2 约束

for i in range(m_edge):
    for k in range(n_tasks):
        model.addConstr(quicksum(x[i, k, j] for j in range(n_tasks)) <= 1)

model.setObjective(quicksum(k * q[i] * p[i][j] * x[i, k, j]
    for k in range(n_tasks)
    for j in range(n_tasks)
    for i in range(m_edge)
    ), GRB.MINIMIZE)

model.update()

model.setParam('IntFeasTol', 1e-9)

model.setParam("OutputFlag", 0)
model.Params.LogToConsole=True # 显示求解过程
model.Params.MIPGap=0.0001 # 百分比界差
model.Params.TimeLimit=100 # 限制求解时间为 100s
model.optimize()

result = [[] for i in range(m_edge)]
regex = re.compile(r"\[.*\]")
for v in model.getVars():
    line = f"{round(v.x,3)}" 
    if "0.0" not in line:
        arr = v.varName
        arr = regex.search(arr).group()
        i, k, j = arr[1:-1].split(',')
        result[int(i)].append(int(j))

for i in range(len(result)):
    print(i, ":", result[i])
