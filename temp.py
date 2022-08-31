import json

a = '[{"name":"eggs", "price":1},{"name":"rice", "price":9.99},{"name":"coffee", "price":9.99}]'

b = json.loads(a)




new_a = sorted(b, key= lambda k : (k['price'],k['name']))
print(new_a)





