
import hashlib
import mechanicalsoup as ms
import os
import requests

from pydub import AudioSegment

OUT_FOLDER = './audio_dataset'

def chunk(iterable, chunk_size):
    for i in range(0, len(iterable), chunk_size):
        yield iterable[i:i + chunk_size]

def download_song(url, meta, dest_dir, genre):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    response = requests.get(url)

    hasher = hashlib.md5()
    for c in chunk(response.content, 4096):
        hasher.update(c)
    h = hasher.hexdigest()

    tmp_filename = os.path.join('/tmp', h)


    with open(tmp_filename, 'wb') as f:
        f.write(response.content)

    try:
        song = AudioSegment.from_file(os.path.join('/tmp', h))
        song = song[:60000]
        song.export(os.path.join(dest_dir, h), format='wav')

        with open('./{}.txt'.format(genre), 'a') as f:
            meta['name'] = h
            f.write('{name}:{artist},{track},{album}:{genre}\n'.format(**meta))
    except:
        print("Failed to convert to wav.")

    os.remove(os.path.join('/tmp', h))

uri = 'http://freemusicarchive.org/genre/{genre}/?page={page}&per_page=10'

def download_genre(genre):
    browser = ms.Browser()
    done = False
    urls = set()

    count = len([os.listdir('./{}/{genre}'.format(OUT_FOLDER, genre=genre))])

    meta_filename = '{}.txt'.format(genre)
    meta_db = set()

    with open(meta_filename, 'r') as f:
        for line in f:
            meta = dict()

            filename = line.split(':')[0]
            meta = line.split(':')[1]
            genres = line.split(':')[2]
            meta_db.add(meta)



    for i in range(1, 500):
        if done or count >= 500:

            break

        print("Downloading page {} of {}".format(i, genre))

        page = browser.get(uri.format(genre=genre, page=i))
        playlist = page.soup.select('.playlist')
        if not playlist or not len(playlist) >= 1:
            print("Skipping this page, errors...")
            continue
        playlist = playlist[0]

        for songdiv in playlist.children:
            if 'select' not in dir(songdiv):
                continue

            meta = {
                'artist': 'none,',
                'album': 'none',
                'track': songdiv.select('.ptxt-track')[0].a.text,
                'genre': ",".join([x.text for x in songdiv.select('.ptxt-genre')[0].select('a')])
            }


            # We only want one song per artist... otherwise too much data
            count += 1

            # Sometimes artist is missing
            artist_div =  songdiv.select('.ptxt-artist')[0]
            if artist_div.a:
                meta['artist'] = artist_div.a.text

            # Sometimes the album is missing...
            album_div = songdiv.select('.ptxt-album')[0]
            if album_div.a:
                meta['album'] = album_div.a.text

            m = '{artist},{track},{album}'.format(**meta)
            if m in meta_db:
                print(
                    " -> already got {} by {}"
                    .format(meta['track'], meta['artist']))
                continue

            print(
                " -> downloading {} by {}"
                .format(meta['track'], meta['artist']))

            download_url = songdiv.select('.playicn')[0].a['href']

            if download_url in urls:
                done = True
                break
            urls.add(download_url)

            download_song(
                download_url,
                meta,
                './{}/{genre}'.format(OUT_FOLDER, genre=genre),
                genre)

for genre in ['Electronic', 'Jazz', 'Metal', 'Classical']
    download_genre(genre)


