import os

users = os.listdir("../data/users/")
users1 = os.listdir("../data/users1/")

users = [int(i) for i in users]
users1 = [int(i) for i in users1]

print(f"len users {len(users)}")
print(f"len users1 {len(users1)}")

print(f"min max users {min(users),max(users)}")
print(f"min max users1 {min(users1),max(users1)}")

users = set(users)
users1 = set(users1)

print(f"set users len {len(users)}")
print(f"set users1 len {len(users1)}")

print(f"intersection len {len(users & users1)}")
print(f"union len {len(users | users1)}")

print("intersection values")

print(list(users & users1)[-10:])