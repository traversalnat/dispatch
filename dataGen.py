import random

# 生成服从指数分布的随机数
# beta 指数分布的参数
# num 参数数量
def genSample(beta, num):
    return [round(random.expovariate(1/beta),2) for _ in range(num)]
