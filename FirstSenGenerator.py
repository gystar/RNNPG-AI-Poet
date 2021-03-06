#!/usr/bin/env python
# coding: utf-8

# In[1]:


import kenlm
import operator
import random
import time
# import classification

path = {
    # Ping/Ze tonal of all characters
    "TONAL_PATH": "./dataset/pingshui.txt",
    # category of words
    "SHIXUEHANYING_PATH": "./dataset/shixuehanying.txt",
    # first sentences
    "CANDIDATE_PATH": "./shengcheng/candidates.txt",
    "TOP_RESULT": "./shengcheng/top.txt",
}

# In[2]:


FIVE_PINGZE = [[[0, -1, 1, 1, -1], [1, 1, -1, -1, 1], [0, 1, 1, -1, -1], [0, -1, -1, 1, 1]],
               [[0, -1, -1, 1, 1], [1, 1, -1, -1, 1], [0, 1, 1, -1, -1], [0, -1, -1, 1, 1]],
               [[0, 1, 1, -1, -1], [0, -1, -1, 1, 1], [0, -1, 1, 1, -1], [1, 1, -1, -1, 1]],
               [[1, 1, -1, -1, 1], [0, -1, -1, 1, 1], [0, -1, 1, 1, -1], [1, 1, -1, -1, 1]]]

SEVEN_PINGZE = [[[0, 1, 0, -1, -1, 1, 1], [0, -1, 1, 1, -1, -1, 1], [0, -1, 0, 1, 1, -1, -1], [0, 1, 0, -1, -1, 1, 1]],
                [[0, 1, 0, -1, 1, 1, -1], [0, -1, 1, 1, -1, -1, 1], [0, -1, 0, 1, 1, -1, -1], [0, 1, 0, -1, -1, 1, 1]],
                [[0, -1, 1, 1, -1, -1, 1], [0, 1, 0, -1, -1, 1, 1], [0, 1, 0, -1, 1, 1, -1], [0, -1, 1, 1, -1, -1, 1]],
                [[0, -1, 0, 1, 1, -1, -1], [0, 0, -1, -1, -1, 1, 1], [0, 1, 0, -1, 1, 1, -1], [0, -1, 1, 1, -1, -1, 1]]]


# In[3]:


def read_character_tone():
    # get tonal dictionary of each character
    ping = []
    ze = []
    pingshui = {}
    j = -1
    with open(path["TONAL_PATH"], "r", encoding='utf-8') as f:
        isPing = False
        for line in f.readlines():
            j += 1
            line = line.strip()
            if line:
                if line[0] == '/':
                    isPing = not isPing
                    continue
                for i in line:
                    if isPing:
                        ping.append(i)
                    else:
                        ze.append(i)
                    if i not in pingshui.keys():
                        pingshui[i] = [j]
                    else:
                        pingshui[i].append(j)
    return {"Ping": ping, "Ze": ze}, pingshui


def read_shixuehanying():
    # get shixuehanying
    categories = []
    labels = []  # [[1,2,...],[n,n+1,...],...]
    words = []
    class1=[]
    with open(path["SHIXUEHANYING_PATH"], 'r', encoding='utf-8') as f:
        while True:
            line = f.readline()
            line = line.strip()
            if line:
                if line[0] == '<':
                    if line[1] == 'b':
                        titles = line.split('\t') 
                        #print(titles+"\n")
                        #class1.append(titles[1])
                        categories.append(titles[2])
                        labels.append([])
                else:
                    line = line.split('\t')
                    if len(line) == 3:
                        tmp = line[2].split(' ')
                        tmp.append(line[1])
                        #print(tmp)
                    else:
                        tmp = line[1]
                    #print(line[0],line[1])
                    
                    if len(tmp) >= 10:
                        labels[-1].append(len(words))
                        #print(len(words),line[1])
                        class1.append(line[1])
                        words.append(tmp)
            else:
                break
    #print(labels)
    return categories, labels, words,class1


# In[4]:


def user_input():
    # get structure, subject, words
    categories, labels, words,class1 = read_shixuehanying()
    while True:  # choose 5 or 7
        print("Please choose poem structure:\npress 5: 5-char quatrain\npress 7: 7-char quatrain\n")
        chars = input()
        chars = int(chars)
        if chars == 5 or chars == 7:
            break
        else:
            print("Invalid input. Please try again.")

    while True:  # choose subject
        print("Please choose poem subject:\n")
        print(u"0: random")
        for i in range(0, len(categories)):
            print(str(i + 1) + ": " + categories[i])

        label = input()
        label = int(label)
        if label == 0:
            label = int(random.uniform(0, len(labels)))
            break
        if not 1 <= label <=996:
            print("Invalid input. Please try again.")
            continue
        else:
            label -= 1
            break

    random.seed(int(time.time()))
    # print(labels)
    fir_tar = labels[label][int(random.uniform(0, len(labels[label])))]
    # sec_tar = labels[label][int(random.uniform(0, len(labels[label])))]
    # target_labels = [fir_tar] if fir_tar == sec_tar else [fir_tar, sec_tar]  # labels needed
    for i in range(0, len(labels[label])):
        print(str(labels[label][i]) + ": " + class1[labels[label][i]])
    label1 = input()
    label1 = int(label1)
    target_labels = [label1]
    word = []
    for i in target_labels:
        word += words[i]
    print(target_labels)
    return word, target_labels, chars


# In[5]:


# judge if the given sentence follows the given tonal pattern
tonal_hash, pingshui = read_character_tone()


def judge_tonal_pattern(row, chars):
    # remove poem with duplicated characters
    if len(row) != len(set(row)):
        return -1
    # judge rhythm availability
    tone = FIVE_PINGZE if chars == 5 else SEVEN_PINGZE
    for i in range(0, 4):
        for j in range(0, chars + 1):
            if j == chars:
                return i
            if tone[i][0][j] == 0:
                continue
            elif tone[i][0][j] == 1 and row[j] in tonal_hash["Ping"]:
                continue
            elif tone[i][0][j] == -1 and row[j] in tonal_hash["Ze"]:
                continue
            else:
                break
    return -1


# In[6]:


def generate_all_candidates():
    # based on user option of chars, tonal and keywords, generate all possible candidates of the first sentence
    vec, subject, chars = user_input()
    candidates = []
    result = []
    vec.sort(key=lambda x: len(x))
    indexes = [0, 0, 0, 0, 0, 0]  # len
    for i in range(0, len(vec)):
        if (len(vec[i])) > 5:
            continue
        indexes[len(vec[i])] += 1
    for i in range(1, len(indexes)):
        indexes[i] += indexes[i - 1]

    if chars == 5:
        # 5
        for i in range(indexes[4], len(vec)):
            candidates.append(vec[i])
        # 4-1
        for i in range(0, indexes[1]):
            for j in range(indexes[3], indexes[4]):
                candidates.append(vec[i] + vec[j])
                candidates.append(vec[j] + vec[i])
        # 3-2
        for i in range(indexes[1], indexes[2]):
            for j in range(indexes[2], indexes[3]):
                candidates.append(vec[i] + vec[j])
                candidates.append(vec[j] + vec[i])
        # 2-2-1
        for i in range(indexes[1], indexes[2]):
            for j in range(i + 1, indexes[2]):
                for k in range(0, indexes[1]):
                    candidates.append(vec[i] + vec[j] + vec[k])
                    candidates.append(vec[i] + vec[k] + vec[j])
                    candidates.append(vec[j] + vec[i] + vec[k])
                    candidates.append(vec[j] + vec[k] + vec[i])
                    candidates.append(vec[k] + vec[j] + vec[i])
                    candidates.append(vec[k] + vec[i] + vec[j])

    elif chars == 7:
        # 5-2
        for i in range(indexes[4], len(vec)):
            for j in range(indexes[1], indexes[2]):
                candidates.append(vec[i] + vec[j])
                candidates.append(vec[j] + vec[i])
        # 4-3
        for i in range(indexes[3], indexes[4]):
            for j in range(indexes[2], indexes[3]):
                candidates.append(vec[i] + vec[j])
                candidates.append(vec[j] + vec[i])
        # 3-3-1
        for i in range(indexes[2], indexes[3]):
            for j in range(i + 1, indexes[3]):
                for k in range(0, indexes[1]):
                    candidates.append(vec[i] + vec[j] + vec[k])
                    candidates.append(vec[i] + vec[k] + vec[j])
                    candidates.append(vec[j] + vec[i] + vec[k])
                    candidates.append(vec[j] + vec[k] + vec[i])
                    candidates.append(vec[k] + vec[j] + vec[i])
                    candidates.append(vec[k] + vec[i] + vec[j])
        # 3-2-2
        for i in range(indexes[1], indexes[2]):
            for j in range(i + 1, indexes[2]):
                for k in range(indexes[2], indexes[3]):
                    candidates.append(vec[i] + vec[j] + vec[k])
                    candidates.append(vec[i] + vec[k] + vec[j])
                    candidates.append(vec[j] + vec[i] + vec[k])
                    candidates.append(vec[j] + vec[k] + vec[i])
                    candidates.append(vec[k] + vec[j] + vec[i])
                    candidates.append(vec[k] + vec[i] + vec[j])
    # select candidates with given tonal patterns
    # print(candidates)
    for i in candidates:
        j = judge_tonal_pattern(i, chars)
        if j == -1:
            continue
        result.append(i)
    return result, subject, chars


# In[7]:


def find_best_sentences(n=10):
    candidates = []
    # while True:
    candidates, subject, chars = generate_all_candidates()
    # write the candidates into the candidates file
    with open(path["CANDIDATE_PATH"], 'w', encoding='utf-8') as output:
        for string in candidates:
            for j in range(0, len(candidates[0])):
                tmp = string[j]
                output.write(tmp + " ")
            output.write("\n")

    model = kenlm.Model("first.poem.lm")
    with open(path["CANDIDATE_PATH"], 'r', encoding='utf-8') as f:
        context = f.readlines()
    candidate_score = {}
    for line in context:
        line = line.rstrip('\n')
        candidate_score[line] = model.score(line)
    candidate_score = sorted(candidate_score.items(), key=lambda x: x[1], reverse=True)
    result = candidate_score[0: min(n, len(candidate_score))]

    # write the result to file
    with open(path['TOP_RESULT'], 'w', encoding='utf-8') as output:
        # print ("Top " + str(n) + " results:")
        for i in result:
            # print(i)
            s = i[0].replace(' ', '')
            output.write(s + "\n")
            # print(s)
    output.close()

    res = random.choice(result)[0]
    res = res.replace(' ', '')
    # print("The first sentence is: " + res)
    return chars

# In[8]:


# find_best_sentences()


# In[ ]:
