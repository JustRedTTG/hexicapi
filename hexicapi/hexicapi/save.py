import pickle, os

def save(file,*args):
    with open(file, 'wb') as f: pickle.dump(args, f)
def load(file):
    if os.path.exists(file):
        with open(file,"rb") as f: args = pickle.load(f)
        return args
    else: return None