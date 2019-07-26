import random


def get_header():
    agentlist = []
    x = open('timeagent.txt', 'r')
    temp = x.readlines()
    # print(temp)
    x.close()
    for item in temp:
        if temp != '\n':
            # # print(item.strip())
            if item.strip() != '':
                agentlist.append(item.strip())
    head = random.choice(agentlist)
    headers = {'User-Agent': head}
    return headers