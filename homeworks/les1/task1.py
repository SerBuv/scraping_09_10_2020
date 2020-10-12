import requests
import json
from pprint import pprint
url = 'https://api.github.com'
username = 'serbuv'
r = requests.get(f'{url}/users/{username}/repos')
print(f'У пользователя {username} следующие репозитории: ')
n = 1
for i in r.json():
    print(f'{n}) {i["name"]}')
    n = n + 1
#pprint(r.json())
with open('rep.json', 'w') as f:
    json.dump(r.json(), f)