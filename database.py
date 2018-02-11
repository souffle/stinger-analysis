import redis

r = redis.StrictRedis()


def mark_file_as_processed(filename):
    r.set(filename, "processed")


def check_file_processed(filename):
    return r.get(filename)
