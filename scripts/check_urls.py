import urllib.request

images = {
    "essaouira_boats": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1000",
    "agadir_port": "https://images.unsplash.com/photo-1534067783941-51c9c23ecefd?auto=format&fit=crop&w=1000",
    "market": "https://images.unsplash.com/photo-1539650116574-8efeb43e2750?auto=format&fit=crop&w=1000",
    "fisherman": "https://images.unsplash.com/photo-1538334465-a83d1c16ac30?auto=format&fit=crop&w=1000",
    "industrial": "https://images.unsplash.com/photo-1590432130760-b8da8f6d214a?auto=format&fit=crop&w=1000"
}

headers = {'User-Agent': 'Mozilla/5.0'}

for name, url in images.items():
    print(f"Checking {name}: {url}")
    try:
        req = urllib.request.Request(url, headers=headers, method='HEAD')
        with urllib.request.urlopen(req) as response:
            print(f"  Status: {response.status}")
    except Exception as e:
        print(f"  Error: {e}")
