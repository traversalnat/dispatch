import gurobipy as grb
from gurobipy import *
import re

__author__ = "Zhihui Zhang"
__version__ = "1.0"
__email__ = "1726546320 [at] qq [dot] com"


def resolve(p, q, m_edge, n_tasks, max_q, show=False):
    # Create a new model
    model = Model()
    model.setParam("OutputFlag", 0)

    x = model.addVars(m_edge, n_tasks, n_tasks, vtype=GRB.BINARY, name="X_ikj")
    model.update()

    # C1约束 (每一个任务被分配且只分配一次)
    for j in range(n_tasks):
        model.addConstr(quicksum(x[i, k, j]
                                 for i in range(m_edge)
                                 for k in range(n_tasks)) == 1)
    model.update()
    # C2 约束 (n 个任务，m 个节点中有 n*m 个位置，每一个位置只能有一个任务)
    for i in range(m_edge):
        for k in range(n_tasks):
            model.addConstr(quicksum(x[i, k, j] for j in range(n_tasks)) <= 1)

    # C3 约束 (单位价格超过一定值时，不考虑)
    for i in range(m_edge):
        for k in range(n_tasks):
            model.addConstr(quicksum(x[i, k, j] * q[i]
                                     for j in range(n_tasks)) <= max_q)

    model.setObjective(quicksum(k * q[i] * p[i][j] * x[i, k, j]
                                for k in range(n_tasks)
                                for j in range(n_tasks)
                                for i in range(m_edge)
                                ), GRB.MINIMIZE)

    model.update()

    if show:
        model.Params.LogToConsole = True  # 显示求解过程

    model.Params.MIPGap = 0.0001  # 百分比界差
    model.Params.TimeLimit = 100  # 限制求解时间为 100s
    model.optimize()
    result = [[] for i in range(m_edge)]
    regex = re.compile(r"\[.*\]")
    for v in model.getVars():
        line = f"{v.varName}：{round(v.x,3)}"
        if "0.0" not in line:
            arr = v.varName
            arr = regex.search(arr).group()
            i, k, j = arr[1:-1].split(',')
            result[int(i)].append(int(j))
    return result


def participant(edge, func, min_price):
    # 价格从min_price到max_q递增
    price = min_price
    # 各个价格下，整数规划的结果，{[xikj]}
    best_price = min_price
    max_profit = 0
    max_rate = 0
    while True:
        if price > max_q:
            break
        q[pos] = price
        result = resolve(p, q, m_edge, n_tasks, max_q)
        profit, valid = func(len(result[pos]), price)
        print(pos, ":", profit, " with price ",
              price, " and r ", len(result[pos]))
        if not valid:
            price = price + 1.0
            continue
        if profit > max_profit:
            max_profit = profit
            best_price = price
            max_rate = len(result[pos])
        price = price + 1.0
    return best_price, max_rate
