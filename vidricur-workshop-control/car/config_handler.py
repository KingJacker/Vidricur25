import json

CONFIG_PATH = "/home/pi/project/Vidricur25/vidricur-workshop-control/car/config.json"

def read_config():
    with open(CONFIG_PATH, "r") as file:
        return json.loads(file.read())
    
def write_config(config):
    with open(CONFIG_PATH, "w") as file:
        file.write(json.dumps(config))

def get_steering_config():
    config = read_config()
    return config["steering"]["front"], config["steering"]["rear"], config["steering"]["max"]

def get_float_config():
    config = read_config()
    return config["floats"]["left"]["up"], config["floats"]["left"]["down"], config["floats"]["right"]["up"], config["floats"]["right"]["down"]

def get_config():
    return read_config()
