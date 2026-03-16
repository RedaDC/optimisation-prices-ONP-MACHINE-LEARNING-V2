
import urllib.request
import os
import time

IMG_DIR = r"c:\Users\reda\Downloads\optimisation-machine-learning--master (1)\assets\images"

def download_image(urls, filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
    }
    
    for url in urls:
        print(f"Trying {url} for {filename}...")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as response:
                content = response.read()
                if len(content) > 2000: # Ensure it's not a small error page
                    path = os.path.join(IMG_DIR, filename)
                    with open(path, 'wb') as f:
                        f.write(content)
                    print(f"  Successfully downloaded {filename} ({len(content)} bytes)")
                    return True
                else:
                    print(f"  Content too small ({len(content)} bytes), skipping...")
        except Exception as e:
            print(f"  Error: {e}")
        time.sleep(2)
    return False

if __name__ == "__main__":
    tasks = [
        (['https://upload.wikimedia.org/wikipedia/commons/b/b5/Shrimp_Panaeus_japonicus.jpg', 
          'https://upload.wikimedia.org/wikipedia/commons/4/41/Pandalus_borealis.jpg',
          'https://upload.wikimedia.org/wikipedia/commons/1/10/Penaeus_monodon.jpg'], 'crevette.jpg'),
        (['https://upload.wikimedia.org/wikipedia/commons/e/ee/Sole_commune_%28Solea_solea%29_en_rade_de_Brest_%28Ifremer_00558-67035_-_20671%29.jpg',
          'https://upload.wikimedia.org/wikipedia/commons/4/47/Solea_solea_1.jpg'], 'sole.jpg'),
        (['https://upload.wikimedia.org/wikipedia/commons/e/ea/Great_white_shark_Dyer_Island.jpg',
          'https://upload.wikimedia.org/wikipedia/commons/2/23/Carcharodon_carcharias.jpg'], 'requin.jpg')
    ]
    
    for urls, filename in tasks:
        download_image(urls, filename)
        # Duplicate for crevette_rose
        if filename == 'crevette.jpg':
            import shutil
            shutil.copy(os.path.join(IMG_DIR, 'crevette.jpg'), os.path.join(IMG_DIR, 'crevette_rose.jpg'))
            print("  Copied to crevette_rose.jpg")
