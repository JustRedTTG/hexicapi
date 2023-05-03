import pickle, os

def save(file=None,*args):
    if type(file) == str:
        with open(file, 'wb') as f: pickle.dump(args, f)
    elif not file: return pickle.dumps(args)
def load(file):
    if type(file) == str and os.path.exists(file):
        with open(file,"rb") as f: return pickle.load(f)
    elif type(file) in [bytes, bytearray]: return pickle.loads(file)
    else: return None