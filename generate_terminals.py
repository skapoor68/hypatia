
with open("user_terminals_atlanta.basic.txt", "+w") as f:
    for i in range(0, 30000):
        # 0,Tokyo,35.6895,139.69171,0
        line = str(i) + ",Atlanta,18.1405,178.4233,0"
        f.write(line + "\n")

with open("ground_stations_sydney.basic.txt", "+w") as f:
    for i in range(0, 1000):
        # 0,Tokyo,35.6895,139.69171,0
        line = str(i) + ",Sydney,-33.86785,151.20732,0"
        f.write(line + "\n")