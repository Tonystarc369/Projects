#1,1,1,1,2,2,2,3,3,3]
#ms)
#)
#
#print(l)

car = {"brand": "Ford", "model": "Mustang", "year": 1964}

#for key in car:
 #   print(key,car[key])

#for key in car.values():
#    print(key)

for key, value in car.items():
    print(f"{key}: {value}")