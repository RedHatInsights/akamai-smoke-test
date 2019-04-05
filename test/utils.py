import yaml

class Utils():
    def getData():
        with open('./data/main.yml', 'r') as f:
            return yaml.safe_load(f)
