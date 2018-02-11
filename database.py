import redis

r = redis.StrictRedis()

def mark_file_as_processed(filename):
    r.set(filename, True)

def check_file_processed(filename):
    return r.get(filename)
