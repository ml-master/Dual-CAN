import json
import random

fake_jsonfile = './data/fake.json'
real_jsonfile = './data/real.json'

lists = []

with open(fake_jsonfile, 'r') as f:
    for line in f:
        lists.append(json.loads(line))
with open(real_jsonfile, 'r') as f:
    for line in f:
        lists.append(json.loads(line))

for dict in lists:
    dict['tweet_list'] = dict['desc_list']
    if dict['label'] == 'legitimate':
        dict['label'] = 'real'

random.shuffle(lists)
train_size=int(len(lists)*0.75*0.9)
valid_size=train_size+int(len(lists)*0.075)
print("train_size:",train_size)
print("valid_size",valid_size-train_size)
print("test_size",len(lists)-valid_size)

with open("data/train.json", "a") as f:
    for Dict in lists[0:train_size]:
        json.dump(Dict,f)
        f.write('\n')

with open("data/eval.json","a") as f:
    for Dict in lists[train_size:valid_size]:
        json.dump(Dict,f)
        f.write('\n')

with open("data/test.json","a") as f:
    for Dict in lists[valid_size:]:
        json.dump(Dict,f)
        f.write('\n')