import requests, json

token = 'secret_StgyWD7f8ZQJsmU53hmFWABg5JhTrFw9esPzZ8hyGQa'

databaseId = '0ee91b3e98574184a4ba6fc735cf6eb6'

headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
    "Notion-Version": "2021-05-13"
}

headersHabitica = {

    "x-api-user": "df56587e-5b7f-4031-9e6c-76b51665ffdd",
    "x-api-key": "29fe8b70-a241-4a7a-a351-8cd67ea8e83c"
}


def readDatabaseOfNotion(databaseId, headers):
    readUrl = f"https://api.notion.com/v1/databases/{databaseId}/query"

    res = requests.request("POST", readUrl, headers=headers)
    data = res.json()
    print(res.status_code)
    # print(res.text)

    with open('./notion.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)


def readHabiticaData(headersHabitica):
    url = "https://habitica.com/api/v3/tasks/user?type=todos"

    res = requests.request("GET", url, headers=headersHabitica)
    data = res.json()
    print(res.status_code)
    # print(res.text)

    with open('./habitica.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)


def createTodoInHabitica(name, headersHabitica):

    name = suffixN2H(name)
    url = "https://habitica.com/api/v3/tasks/user"

    res = requests.post(url, headers=headersHabitica, json={"text": name, "type": "todo"})
    data = res.json()

    print(res.text)

def scoreTaskInHabitica(id):
    url = f"https://habitica.com/api/v3/tasks/{id}/score/up"
    res = requests.post(url, headers=headersHabitica)

    print(res.status_code)

def suffixN2H(taskName):
    return taskName+"_N2H"

def isAbsentInHabitica(taskName, habiticaList):

    taskName = suffixN2H(taskName)

    for i in habiticaList:
        if taskName == i['name']:
            return False

    return True

def getHabiticaList():

    lst = []
    f = open("habitica.json")
    data = json.load(f)

    for i in data['data']:
        name = i['text']
        id = i['id']

        dict = {'name':name , 'id':id}

        lst.append(dict)
    f.close()

    return lst



def getNotionList(condn):
    lst = []
    f = open("notion.json", encoding='utf-8')
    data = json.load(f)
    # print(data)

    for i in data['results']:
        try:
            status = i['properties']['Status']['select']['name']
            name = i['properties']['Name']['title'][0]['text']['content']
            endDate = i['properties']['End Date']['formula']['date']
            # print(name)

            if condn(status) and endDate is not None:
                lst.append(name)
        except:
            print("something went wrong. Check Notion")
    f.close()

    return lst


def notionDoneCondn(status):
    return status == 'Completed'


def notionNotDoneCondn(status):
    return status != 'Completed'


def getDoneListOfNotion():
    return getNotionList(notionDoneCondn)


def getNotDoneListOfNotion():
    return getNotionList(notionNotDoneCondn)


def getTaskId(name, habiticaList):

    name = suffixN2H(name)

    for i in habiticaList:
        if name == i['name']:
            return i['id']


def syncNotionToHabitica():
    print('Reading Notion DB')
    readDatabaseOfNotion(databaseId, headers)
    print('Reading Habitica DB')
    readHabiticaData(headersHabitica)
    habiticaList = getHabiticaList()
    notionDoneList = getDoneListOfNotion()

    for task in notionDoneList:
        print('Processing Completed Task ' + task)
        habiticaid = getTaskId(task,habiticaList)
        if habiticaid is not None:
            print('Scoring in Habitica for ' + habiticaid)
            scoreTaskInHabitica(habiticaid)

    notionNotDoneList = getNotDoneListOfNotion()

    for task in notionNotDoneList:
        print('Processing InComplete Task' + task)
        if isAbsentInHabitica(task,habiticaList):
            print('Missing in Habitica, Creating '+ task )
            createTodoInHabitica(task, headersHabitica)


syncNotionToHabitica()
