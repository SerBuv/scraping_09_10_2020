import requests
import json
from pprint import pprint

id = '102309248'
token = 'da4f6e9e174b0b24e91c6be32bf4ec111dd605b5071b2402bf9bc68a70e0aa233a79157cb533d64a6cbd4'

url = f'https://api.vk.com/method/groups.get?extended=1&user_id={id}&v=5.52&access_token={token}'
r = requests.get(url)

with open('community.json', 'w') as f:
    json.dump(r.json(), f)

print(f'Пользователь c id={id} подписан на следующие сообщества: ')

r1 = r.json()['response']
r2 = r1['items']
n = 1
for i in r2:
    print(f'{n}) {i["name"]}')
    n = n + 1