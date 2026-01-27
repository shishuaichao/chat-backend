
# eg:
# data = {"a": "user1", "b": "avatar.jpg"}
# valid_fields = {"a", "b", "c"}

def get_valid_data(data, valid_fields):
  arr = [v for v in data.items()]
  keysStr = ''
  valuesStr = ''
  for item in arr:
    if item[0] in valid_fields: 
      keysStr += f', {item[0]}=%s'
      valuesStr += f', {item[1]}'
  return {
    "keys": keysStr[2:],
    "values": valuesStr[2:]
  }
