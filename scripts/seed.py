import requests, os, json, datetime

BASE=os.getenv('BASE','http://localhost:5000')

# def post(path, payload):
#     r = requests.post(f"{BASE}{path}", json=payload)
#     print(path, r.status_code, r.json())
#     return r.json()

def post(path, payload):
    r = requests.post(f"{BASE}{path}", json=payload)
    try:
        data = r.json()
    except Exception:
        data = r.text  # fallback if JSON parse fails
    print(path, r.status_code, data)
    return data


def main():
    requests.post(f"{BASE}/initdb")
    # c = post('/colleges', {'name':'AI Institute'})
    # col_id = c['id']
    c = post('/colleges', {'name':'AI Institute'})
    if 'id' not in c:
      print("College already exists, skipping…")
      return
    col_id = c['id']

    s1 = post('/students', {'name':'Asha', 'email':'asha@example.com', 'college_id':col_id})
    s2 = post('/students', {'name':'Rahul','email':'rahul@example.com','college_id':col_id})
    today = datetime.date.today().strftime('%Y-%m-%d')
    e1 = post('/events', {'title':'Intro to LLMs','type':'Seminar','date':today,'college_id':col_id})
    e2 = post('/events', {'title':'Hackathon','type':'Workshop','date':today,'college_id':col_id})

    post('/register', {'student_id':s1['id'],'event_id':e1['id']})
    post('/register', {'student_id':s2['id'],'event_id':e1['id']})
    post('/register', {'student_id':s1['id'],'event_id':e2['id']})

    post('/attendance', {'student_id':s1['id'],'event_id':e1['id'],'status':'present'})
    post('/attendance', {'student_id':s2['id'],'event_id':e1['id'],'status':'absent'})
    post('/attendance', {'student_id':s1['id'],'event_id':e2['id'],'status':'present'})

    post('/feedback', {'student_id':s1['id'],'event_id':e1['id'],'rating':5,'comment':'Great!'})
    post('/feedback', {'student_id':s2['id'],'event_id':e1['id'],'rating':3})

if __name__ == "__main__":
    main()
