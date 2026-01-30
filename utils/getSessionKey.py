def getSessionKey(arr):
    ids = [int(item["id"]) for item in arr]
    ids.sort()
    return "_".join(str(id) for id in ids)
