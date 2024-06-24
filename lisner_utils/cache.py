#utilities for saving and restoring copies of files
import os
import re
def replace(path):
    cache = re.sub("\.(?=[^\.]*?$)", "_temp.", path)
    if os.path.exists(path):
        if os.path.exists(cache):
            os.remove(cache)
        os.rename(path, cache)

def restore(path):
    cache = re.sub("\.(?=[^\.]*?$)", "_temp.", path)
    if os.path.exists(cache):
        if os.path.exists(path):
            os.remove(path)
        os.rename(cache, path)
