#utility for accessing global
#reference json
import json
import pathlib

def main(ref):
    with open(str(pathlib.Path(__file__).parent.resolve())+"\\refs\\loc_refs.json") as f:
        j = json.loads(f.read())
    return j[ref]
if __name__ == "__main__":
    main()
