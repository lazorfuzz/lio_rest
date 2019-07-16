from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json
import os

def find():
  memes_repo = 'https://www.reddit.com/r/memes/top/.json'
  req = Request(memes_repo)
  req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36')
  with urlopen(req) as client:
    data = client.read()
  reddit_memes = json.loads(data)
  memes_list = reddit_memes['data']['children']
  for meme in memes_list:
    try:
      url = meme['data']['url']
      if '.jpg' in url or '.png' in url or '.jpeg' in url:
        api_endpoint = os.environ['API_ENDPOINT']
        post_data = urlencode({'url': url, 'meme_auth': os.environ['AUTH'], 'temp': '1'}).encode('ascii')
        req = Request(url=api_endpoint, method='POST', data=post_data)
        with urlopen(req) as client:
          data = client.read()
        print('Added', url)
    except: pass

if __name__ == '__main__':
  find()