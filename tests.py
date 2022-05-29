from boarding import *
import configparser
import json


def calculatePercentile(list_, bottom=0.05, top=0.95):
        list_.sort()
        
        len_ = len(list_)
        
        if len_ == 0:
            return 0, 0
        
        bottomPercentile = list_[int(len_ * bottom)]
        topPercentile = list_[int(len_ * top)]
        
        return bottomPercentile, topPercentile


if __name__ == "__main__":
    # load config
    config = configparser.RawConfigParser()
    config.read(r'config.txt')
    
    testsCfg = configparser.RawConfigParser()
    testsCfg.read(r'tests.txt')
    
    m, n = int(config.get("airplane", "seats")), int(config.get("airplane", "rows"))
    corridors = config.get("airplane", "corridors").split(",")
    for i in range(len(corridors)):
        corridors[i] = int(corridors[i])

    tests = []
    for i in json.loads("[" + testsCfg.get("tests", "types") + "]"):
        tests.append(i)
    print(tests)

    tests_number = int(testsCfg.get("tests", "n"))
    
    packing_time = []
    for i in config.get("passengers", "packingTime").split(","):
        packing_time.append(int(i))

    print(f"plane with {n} rows and {m} seats, corridors at {corridors}")

    total_time_results = {}
    
    for t in tests:
        print()
        turnResults = []
        percentileResults = {"bottom": [], "top": []}
        options = {}

        if isinstance(t, list):
            options = t[1]
            t = t[0]

        for i in range(tests_number):
            # print(f"{i + 1}/{tests} {t}", end='\r')

            plane = Plane(m, n, corridors)
            plane.createPassengers(t, options)

            t_num = 0
            while plane.passengers:
                t_num, boardingTimeList = plane.next_turn(options)
                
            turnResults.append(t_num)
            percentile = calculatePercentile(boardingTimeList)
            percentileResults["bottom"].append(percentile[0])
            percentileResults["top"].append(percentile[1])

        if t == "section":
            t += " (width " + str(options["section_width"]) + ")"

        print(f"\nresults for {t} passengers distribution ({tests_number} tests):")
        print(f"average total time: {sum(turnResults) / tests_number}")
        print(f"total time range: {min(turnResults)}-{max(turnResults)}")
        print(f"average boarding time bottom percentile: {sum(percentileResults['bottom']) / tests_number}")
        print(f"average boarding time top percentile: {sum(percentileResults['top']) / tests_number}")
        print(options)
        
        # print("turn results:")
        # print(turnResults)

        total_time_results[t] = turnResults

    # dump to csv
    with open(f"out.csv", "w") as f:
        for i in total_time_results:
            f.write(f"{i}, {str(total_time_results[i])[1:-1]}\n")
            f.write("\n")
            
        f.write(f"range")
        for i in range(300-5, 600+10, 5):
            f.write(f", {i}")
        f.write("\n")
