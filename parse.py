with open("data", "r") as f:
    for line in f.readlines():
        if "0.0" in line:
            continue
        else:
            print(line)
