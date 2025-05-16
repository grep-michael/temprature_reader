import subprocess,json,time,os,argparse,pathlib

TEMPRATURE_LOCATOIN = "./temps/"

INC = 0
class DataCollector():
    def run(args):
        DataCollector.run_for(args.runtime,args.delay)

    def save_sensor_json():
        global INC
        sensors_call = subprocess.run(["sensors -j"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        if sensors_call.returncode != 0:
            return 
        sensor_json = json.loads(sensors_call.stdout.decode())
        with open("{}{}.json".format(TEMPRATURE_LOCATOIN,INC),"w") as f:
            json.dump(sensor_json,f,indent=4)
            INC += 1
    def run_for(runtime,delay=30):
        os.makedirs(TEMPRATURE_LOCATOIN, exist_ok=True)
        start = time.time()
        while 1:
            DataCollector.save_sensor_json()
            cur = time.time()
            diff = cur - start
            if diff > runtime:
                return
            time.sleep(delay)


def Analyzer(args):
    JSON_DATA = []
    def load_jsons():
        temp_loc = pathlib.Path(TEMPRATURE_LOCATOIN)
        json_files = list(temp_loc.glob("*.json"))
        json_files = sorted(json_files, key=lambda path: path.name)
        for file in json_files:
            with open(file,"r") as f:
                data = json.load(f)
                JSON_DATA.append(data)    
    
    totaled_json = {}
    def fill_total_json():
        def recurive(JSON:dict,AVERAGED:dict):
            for i in JSON:

                if type(JSON[i]) == dict: #subdirectory
                    AVERAGED.setdefault(i,{})
                    recurive(JSON[i],AVERAGED[i])
                
                if type(JSON[i]) == float or type(JSON[i]) == int: #some number we want to average
                    AVERAGED.setdefault(i,[])
                    AVERAGED[i].append(JSON[i])
                
                if type(JSON[i]) == str:
                    AVERAGED.setdefault(i,"")
                    AVERAGED[i] = JSON[i]
                


        for i in JSON_DATA:
            recurive(i,totaled_json)

    def average_the_json_dict():
        def recurive(averaged_dict:dict):
            for i in averaged_dict:

                if type(averaged_dict[i]) == dict: #subdirectory
                    recurive(averaged_dict[i])
                
                if type(averaged_dict[i]) == list: #list of numbers, probably numbers
                    averaged_dict[i] = sum(averaged_dict[i]) / len(averaged_dict[i])



        copy = totaled_json.copy()
        recurive(copy)
        return copy
    
    load_jsons()
    fill_total_json()
    average_json = average_the_json_dict()

    print(json.dumps(average_json, indent = 4))


parser = argparse.ArgumentParser(
        description="tool for analysing computer tempreatures using lm-sensors"
    )

subparsers = parser.add_subparsers(
        title="commands", 
        dest="command", 
        required=True,
        help="Available operations"
    )

collect_parser = subparsers.add_parser("collect", help="collect tempature data")

collect_parser.add_argument(
    "-r","--runtime",
    type=int,
    default=120,
    help="span of time in seconds to collect data"
)
collect_parser.add_argument(
    "-d","--delay",
    type=int,
    default=30,
    help="time in seconds to wait between grabbing and saving sensor info"
)

analyze_parser = subparsers.add_parser("analyze", help="analyze tempature data")

args = parser.parse_args()

if __name__ == "__main__":
    if args.command == "collect":
        DataCollector.run(args)
    if args.command == "analyze":
        Analyzer(args)