import json
import socket
import urllib3
import requests
import random
import tagme
tagme.GCUBE_TOKEN = "66152d56-2c00-4d00-90e6-753efb229a69-843339462"
import wikipediaapi

user_agent = 'DualCAN/1.0 (contact: rogerskelamen@gmail.com)'
wiki_wiki = wikipediaapi.Wikipedia(language='en', user_agent=user_agent)

def get_news(json_file, label):
    lists = []
    count = 0
    total_desc=0
    with open(json_file, 'r') as f:
        content = json.load(f)
        for news_id, news in content.items():
            if count > 300:
                break
            Dict = {}
            Dict['label'] = label
            Dict['id'] = news['origin_id']
            if label == "fake":
                Dict['text'] = news['generated_text']
            if label == "real":
                Dict['text'] = news['generated_text_t015']
            entity_desc_list=[]
            try:
                # get entity_desc from wiki
                annotations=tagme.annotate(Dict['text'])
                if(annotations==None):
                    continue
                entitylist=[]
                    # Print annotations with a score higher than 0.1
                for ann in annotations.get_annotations(0.3):
                    A,B,score=str(ann).split(" -> ")[0],str(ann).split(" -> ")[1].split(" (score: ")[0],str(ann).split(" -> ")[1].split(" (score: ")[1].split(")")[0]
                    entitylist.append(B)

                wiki_list=[]
                for entity in entitylist:
                    page_py = wiki_wiki.page(entity)
                    wiki_list.append(page_py.title)
                wiki_list=list(set(wiki_list))
                for name in wiki_list:
                    page_py=wiki_wiki.page(name)
                        #print("name:",page_py.title)
                    try:
                        entity_desc_list.append(page_py.summary)
                    except json.decoder.JSONDecodeError:
                        print("small,JSONERROR")
                        continue
                    except TimeoutError:
                        print("small,TimeoutError")
                        continue
                    except socket.timeout:
                        print("small,socker.timeout")
                        continue
                    except urllib3.exceptions.ReadTimeoutError:
                        print("small,urllib3.exceptions.ReadTimeoutError")
                        continue
                    except requests.exceptions.ReadTimeout:
                        print("small,requests.exceptions.ReadTimeout")
                        continue
            except (TimeoutError,requests.exceptions.ReadTimeout,urllib3.exceptions.ReadTimeoutError,socket.timeout) as e:
                print("big,TimeoutError")
                continue
            Dict['desc_list']=entity_desc_list
            Dict['desc_list']=entity_desc_list
            print("len:",len(Dict['desc_list']))
            total_desc+=len(Dict['desc_list'])
            lists.append(Dict)
            count+=1
            print("epoch:", news_id," | label:", news['generated_label']," | count:", count)

    return total_desc, lists


def get_data():
    fake_jsonfile = './fakenews/gossipcop_v3-1_style_based_fake.json'
    totdesc_fake, list_fake = get_news(fake_jsonfile, "fake")
    real_jsonfile = './fakenews/gossipcop_v3-5_style_based_legitimate.json'
    totdesc_real, list_real = get_news(real_jsonfile, "real")
    lists = list_fake + list_real

    # with open("data/fake.json", "a") as f:
    #     for Dict in list_fake:
    #         json.dump(Dict,f)
    #         f.write('\n')

    # with open("data/real.json", "a") as f:
    #     for Dict in list_real:
    #         json.dump(Dict,f)
    #         f.write('\n')

    random.shuffle(lists)
    train_size=int(len(lists)*0.75*0.9)
    valid_size=train_size+int(len(lists)*0.075)
    print("train_size:",train_size)
    print("valid_size",valid_size-train_size)
    print("test_size",len(lists)-valid_size)
    print("average_desc_number:",(totdesc_fake+totdesc_real)/len(lists))

    with open("data/train.json", "a") as f:
        for Dict in lists[0:train_size]:
            json.dump(Dict,f)
            f.write('\n')

    with open("data/dev.json","a") as f:
        for Dict in lists[train_size:valid_size]:
            json.dump(Dict,f)
            f.write('\n')

    with open("data/test.json","a") as f:
        for Dict in lists[valid_size:]:
            json.dump(Dict,f)
            f.write('\n')

if __name__ == '__main__':
    get_data()