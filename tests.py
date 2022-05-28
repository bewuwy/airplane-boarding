from boarding import *
import configparser
import json


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

    test_types = []
    print(testsCfg.get("tests", "types"))
    for i in json.loads("[" + testsCfg.get("tests", "types") + "]"):
        test_types.append(i)

    tests = int(testsCfg.get("tests", "n"))

    print(f"plane with {n} rows and {m} seats, corridors at {corridors}")

    all_results = {}
    for t in test_types:
        print()
        turnResults = []
        percentileResults = {"bottom": [], "top": []}
        t_opts = {}
        s_opt = {}

        if isinstance(t, list):
            if "barging_time" in t[1]:
                barging_time = t[1]["barging_time"]
                t_opts = {"barging_time": barging_time}

            if t[0] == "section":
                s_opt = t[1]
            if "packing_time" in t[1]:
                packing_time = t[1]["packing_time"]
                s_opt["packing_time"] = packing_time

            t = t[0]

        for i in range(tests):
            # print(f"{i + 1}/{tests} {t}") # , end='\r')

            plane = Plane(m, n, corridors)
            plane.createPassengers(t, s_opt)

            t_num = 0
            while plane.passengers:
                t_num, percentile = plane.next_turn(t_opts)
                
            turnResults.append(t_num)
            percentileResults["bottom"].append(percentile[0])
            percentileResults["top"].append(percentile[1])

        if t == "section":
            t += " (width " + str(s_opt["section_width"]) + ")"

        print(f"\nresults for {t} passengers distribution ({tests} tests):")
        print(f"average turns: {sum(turnResults) / tests}")
        print(f"turns range: {min(turnResults)}-{max(turnResults)}")
        print(f"average bottom percentile: {sum(percentileResults['bottom']) / tests}")
        print(f"average top percentile: {sum(percentileResults['top']) / tests}")
        print(t_opts, s_opt)
        
        # print("turn results:")
        # print(turnResults)

        all_results[sum(turnResults) / tests] = t

    best_results = list(all_results.keys())
    best_results.sort()

    print()
    for i in range(min(len(best_results), 5)):
        print(f"{i + 1}.: {all_results[best_results[i]]} - {best_results[i]}")
