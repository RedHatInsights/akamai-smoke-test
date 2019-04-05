import yaml

class Utils():
    def getData(path = './data/main.yml'):
        with open(path, 'r') as f:
            return yaml.safe_load(f)
