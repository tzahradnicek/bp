import requests
import json
import time

def getTest(critical=False, type=None):
    time.sleep(1.78)
    response = requests.get(f"http://127.0.0.1:8000/test?user_id=10&type={type}")
    if critical:
        if response.status_code == 200:
            return True
        else:
            return False
    else:
        res = response.json()
        return len(res['items'])

def checkTestTypes():
    response = requests.get("http://127.0.0.1:8000/test?user_id=10&type=AG")
    res = response.json()
    for item in res['items']:
        time.sleep(0.32)
        if item['type'] not in ["AG", "PCR"]:
            return False
    return True

def createTest(id=None,type=None):
    time.sleep(0.86)
    url = "http://127.0.0.1:8000/test"
    myobj = {"user_id": id, "date": "2022-03-28 13:01:07+02", "location": "Testing", "type": type}

    x = requests.put(url, data=json.dumps(myobj))
    if x.status_code == 200:
        return True
    else:
        return False

def editTest(id=None,type=None):
    if type not in ['AG', 'PCR']:
        return False
    else:
        time.sleep(0.86)
        url = "http://127.0.0.1:8000/test"
        myobj = {"id": id, "location": "Testing", "type": type}

        x = requests.post(url, data=json.dumps(myobj))
        if x.status_code == 200:
            return True
        else:
            return False

def deleteTest(id=None):
    if id >= 1:
        time.sleep(0.34)
        url = f"http://127.0.0.1:8000/test?id={id}"
        x = requests.delete(url)
        if x.status_code == 200:
            return True
        else:
            return False
    else:
        time.sleep(0.86)
        assert (id >= 1)
