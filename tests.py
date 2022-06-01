from boarding import *
import configparser
import json
import matplotlib.pyplot as plt


def calculatePercentile(list_, bottom=0.05, top=0.95):
        list_.sort()
        
        len_ = len(list_)
        
        if len_ == 0:
            return 0, 0
        
        bottomPercentile = list_[int(len_ * bottom)]
        topPercentile = list_[int(len_ * top)]
        
        return bottomPercentile, topPercentile


if __name__ == "__main__":
    print("\n"*3)
    
    # load config
    config = configparser.RawConfigParser()
    config.read(r'config.txt')
    
    testsCfg = configparser.RawConfigParser()
    testsCfg.read(r'tests.txt')
    
    # tests config
    tests = []
    for i in json.loads("[" + testsCfg.get("tests", "types") + "]"):
        tests.append(i)
    print(tests)

    tests_number = int(testsCfg.get("tests", "n"))
    
    # plane and passengers config
    m, n = int(config.get("airplane", "seats")), int(config.get("airplane", "rows"))
    corridors = config.get("airplane", "corridors").split(",")
    for i in range(len(corridors)):
        corridors[i] = int(corridors[i])

    options = {}
    options["packing_time"] = []
    for i in config.get("passengers", "packingTime").split(","):
        options["packing_time"].append(int(i))
        
    options["barging_time"] = int(config.get("passengers", "bargingTime"))
    options["naughty_chance"] = float(config.get("passengers", "naughtyChance"))

    # loaded config
    print(f"plane with {n} rows and {m} seats, corridors at {corridors}")

    total_time_results = {}
    top_time_results = {}
    bot_time_results = {}
    for t in tests:
        print()
        options_ = options.copy()
        if isinstance(t, list):
            for i in t[1]:
                options_[i] = t[1][i]
            
            t = t[0]
        
        turnResults = []
        percentileResults = {"bottom": [], "top": []}

        for i in range(tests_number):
            # print(f"{i + 1}/{tests_number} {t}", end='\r')

            plane = Plane(m, n, corridors)
            plane.createPassengers(t, options_)

            t_num = 0
            while plane.passengers:
                t_num, boardingTimeList = plane.next_turn(options_)
                
            turnResults.append(t_num)
            percentile = calculatePercentile(boardingTimeList)
            percentileResults["bottom"].append(percentile[0])
            percentileResults["top"].append(percentile[1])

        
        if "title" in options_:
            t = options_["title"]

        print(f"\nresults for {t} passengers distribution ({tests_number} tests):")
        print(f"average total time: {sum(turnResults) / tests_number}")
        print(f"total time range: {min(turnResults)}-{max(turnResults)}")
        print(f"average boarding time bottom percentile: {sum(percentileResults['bottom']) / tests_number}")
        print(f"average boarding time top percentile: {sum(percentileResults['top']) / tests_number}")
        print(options_)
        
        # print("turn results:")
        # print(turnResults)

        total_time_results[t] = turnResults
        top_time_results[t] = percentileResults["top"]
        bot_time_results[t] = percentileResults["bottom"]

    # dump to csv
    with open(f"out.csv", "w") as f:
        for i in total_time_results:
            f.write(f"{i}, {str(total_time_results[i])[1:-1]}\n")
            f.write("\n")
            
        f.write(f"range")
        for i in range(300-5, 600+10, 5):
            f.write(f", {i}")
        f.write("\n")

    # matplotlib
    
    for i in total_time_results:
        plt.hist(total_time_results[i], label=i,  alpha=0.4)

    plt.legend(loc='best')
    plt.xlabel("total turns time")
    plt.ylabel("frequency")
    plt.title("Total turns time distribution")
    
    plt.show()
    plt.cla()
    
    for i in top_time_results:
        plt.hist(top_time_results[i], label=i,  alpha=0.4)

    plt.legend(loc='best')
    plt.xlabel("top percentile boarding time")
    plt.ylabel("frequency")
    plt.title("Top percentile (95th) boarding time distribution")
    
    plt.show()
    plt.cla()
    
    for i in bot_time_results:
        plt.hist(bot_time_results[i], label=i,  alpha=0.4)

    plt.legend(loc='best')
    plt.xlabel("bottom percentile boarding time")
    plt.ylabel("frequency")
    plt.title("Bottom percentile (5th) boarding time distribution")
    
    plt.show()
    plt.cla()
