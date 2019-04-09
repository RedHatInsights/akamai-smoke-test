import yaml

class Utils():
    def getData(path = './data/main.yml'):
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def getFlatData(data):
        ret = []
        for key in data:
            for val in data[key]:
                ret.append((key, val))
        return ret
