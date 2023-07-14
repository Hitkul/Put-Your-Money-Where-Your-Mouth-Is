import json
import os
from tqdm import tqdm
from collections import defaultdict


counter = json.load(open("../data/counter.json",'r'))

with open("../data/private_users.txt",'r') as fp:
    private_users = fp.readlines()

with open("../data/users_not_found.txt",'r') as fp:
    user_not_found = fp.readlines()

private_users = [int(i.strip()) for i in private_users]
user_not_found = [int(i.strip()) for i in user_not_found]

user_index = defaultdict(dict)

error_ids = []
# for user_id in tqdm(range(1, counter['last id completed']+1)):
for user_id in tqdm(range(1, 300)):
    if user_id in private_users or user_id in user_not_found:
        continue
    
    try:
        user_info = json.load(open(f"../data/users/{user_id}/userinfo.json",'r'))
    except:
        error_ids.append(user_id)
        continue

    user_index[user_id]['name'] = user_info['username']
    user_index[user_id]['date'] = user_info['joined_date']
    user_index[user_id]['location'] = user_info['location']
    if user_info['img_link'] == "https://static.stickk.com/avatars/main_default.png":
        user_index[user_id]['default_image'] = True
    else:
        user_index[user_id]['default_image'] = False

    user_index[user_id]['commitments'] = []

    if os.path.exists(f"../data/users/{user_id}/completed.json"):
        completed = json.load(open(f"../data/users/{user_id}/completed.json",'r'))
        for k,v in completed.items():
            user_index[user_id]['commitments'].append(int(k.split("/")[-1]))

    
    user_index[user_id]['number_of_commitments'] = len(user_index[user_id]['commitments'])


with open(f"../data/user_index.json",'w') as fp:
    json.dump(user_index,fp,indent=4)

print(error_ids)

    

    

