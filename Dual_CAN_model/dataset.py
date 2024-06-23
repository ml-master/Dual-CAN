from typing import List, Dict
from nltk import tokenize
import torch
from torch.utils.data import Dataset
import nltk

from utils import Vocab

# custom nltk data directory
import os
custom_nltk_data_dir = os.path.expandvars('$HOME') + "/Dual-CAN/.nltk_data/"

# if not exists, create custom nltk directory
if not os.path.exists(custom_nltk_data_dir):
    os.makedirs(custom_nltk_data_dir)

# download punkt tokenizer to custom nltk directory and append to nltk.data.path
nltk.data.path.append(custom_nltk_data_dir)
nltk.download('punkt', download_dir=custom_nltk_data_dir)

class KB_CoDataset(Dataset):
    def __init__(
        self,
        data: List[Dict],
        vocab: Vocab,
        label_mapping: Dict[str, int],
        max_sent_len: int,
        max_sent_num: int,    # max sent_num for a news article
        max_desc_sent_num: int,    # max sent_num for a news KB description
        max_single_desc: int, # max sentence for a single entity description
        max_single_tweet: int,
        max_tweet_sent_num: int,
        mode="train"
    ):
        self.data = data
        self.vocab = vocab
        self.label_mapping = label_mapping
        self._idx2label = {idx: label for label, idx in self.label_mapping.items()}
        self.max_sent_len = max_sent_len
        self.max_sent_num = max_sent_num
        self.max_desc_sent_num = max_desc_sent_num
        self.max_single_desc=max_single_desc
        self.max_tweet_sent_num = max_tweet_sent_num
        self.max_single_tweet=max_single_tweet
        self.mode=mode

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, index) -> Dict:
        instance = self.data[index]
        return instance

    def num_classes(self) -> int:
        return len(self.label_mapping)

    def collate_fn(self, samples: List[Dict]) -> Dict:
        # TODO: get each news has same max sentence count
        padded_sent_list=[]
        padded_desc_list=[]
        padded_tweet_list=[]
        label_list=[]
        id_list=[]
        for instance in samples:
            if(self.mode=="test"):
                id_list.append(instance['id'])
            #else:
            label_list.append(self.label2idx(instance['label']))
            #end if else
            sent_list=[]
            for sent in tokenize.sent_tokenize(instance['text']):
                sent_list.append(sent)
            
            desc_list=[]
            for desc in instance['desc_list']:
                count=0
                for sent in tokenize.sent_tokenize(desc):
                    desc_list.append(sent)
                    count+=1
                    if(count>self.max_single_desc):
                        break

            tweet_list=[]
            for tweet in instance['tweet_list']:
                count=0
                for sent in tokenize.sent_tokenize(tweet):
                    tweet_list.append(sent)
                    count+=1
                    if(count>self.max_single_tweet):
                        break
            
            #endfor
            padded_sent_list.append(sent_list)
            padded_desc_list.append(desc_list)
            padded_tweet_list.append(tweet_list)
        
        batch={}
        if(self.mode=="test"):
            batch["id_list"]=id_list
        #else:
        label_list=torch.tensor(label_list)
        batch["label_list"]=label_list
        

        padding_sent=self.vocab.encode_batch(batch=padded_sent_list,max_sent_len=self.max_sent_len,max_sent_num=self.max_sent_num)
        padding_sent=sum(padding_sent,[])
        padding_sent=torch.tensor(padding_sent)
        batch["texts"]=padding_sent

        padding_desc=self.vocab.encode_batch(batch=padded_desc_list,max_sent_len=self.max_sent_len,max_sent_num=self.max_desc_sent_num)
        padding_desc=sum(padding_desc,[])
        padding_desc=torch.tensor(padding_desc)
        batch["descs"]=padding_desc

        padding_tweet=self.vocab.encode_batch(batch=padded_tweet_list,max_sent_len=self.max_sent_len,max_sent_num=self.max_tweet_sent_num)
        padding_tweet=sum(padding_tweet,[])
        padding_tweet=torch.tensor(padding_tweet)
        batch["tweets"]=padding_tweet
        return batch

            
    def label2idx(self, label: str):
        return self.label_mapping[label]

    def idx2label(self, idx: int):
        return self._idx2label[idx]

