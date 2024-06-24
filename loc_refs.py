#utility for accessing global
#reference json
import json
import pathlib

def main(ref):
    with open(str(pathlib.Path(__file__).parent.resolve())+"\\refs\\loc_refs.json", "r") as f:
        j = json.loads(f.read())
    return j[ref]
def update(ref, value):
    with open(str(pathlib.Path(__file__).parent.resolve())+"\\refs\\loc_refs.json", "r") as f:
        j = json.loads(f.read())
    j[ref] = value
    with open(str(pathlib.Path(__file__).parent.resolve())+"\\refs\\loc_refs.json", "w") as f:
        json.dump(j, f)
if __name__ == "__main__":
    main()
