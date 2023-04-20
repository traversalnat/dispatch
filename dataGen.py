import random

# 生成服从指数分布的随机数
beta = 10 # 指数分布的参数

sample = [round(random.expovariate(1/beta),2) for _ in range(10)]

print(sample)
