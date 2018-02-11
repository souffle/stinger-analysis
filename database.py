import redis

def mark_file_as_processed(filename):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.set(filename, True)