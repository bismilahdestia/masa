import requests
import json
import time
from urllib.parse import urlparse
import random
import re
import sys
from collections import Counter

# Definisi variabel tambahan
word = "Great post!  project sir!"
myFid = "239815"
sentences = word.split("|")

# Definisi URL dan payload
urlGetCastByHash = "https://api.warpcast.com/sesame/{}/{}/getViewerContext"
urlGetListProfCast = "https://api.warpcast.com/sesame/{}/getProfilCast?limit={}"
urlGetCastLikes = "https://api.warpcast.com/sesame/{}/listLike?limit={}"
urlGetCastRecasters = "https://api.warpcast.com/sesame/{}/listUser?limit={}"
urlLike = "https://api.warpcast.com/sesame/{}/like"
urlRecast = "https://api.warpcast.com/sesame/{}/recast"
urlCast = "https://api.warpcast.com/sesame/{}/createCast"
urlFollow = "https://api.warpcast.com/sesame/{}/follow"

headers = {
    'content-type': "application/json"
}

payload = {}

def setupRequest(METHOD, URL, HEADERS, PAYLOAD):
    time.sleep(1)
    return json.loads(requests.request(METHOD, URL, headers=HEADERS, data=PAYLOAD).text.replace('\n', ''))

def is_link(parsed_url):
    if parsed_url.scheme and parsed_url.netloc:
        return True
    else:
        return False

def read_akun():
    try:
        with open('akun.txt', 'r') as file:
            lines = file.readlines()
            username = lines[0].strip()
            access_token = lines[1].strip()
            return username, access_token
    except FileNotFoundError:
        print("File 'akun.txt' tidak ditemukan.")
        sys.exit(1)
    except IndexError:
        print("Format file 'akun.txt' tidak valid.")
        sys.exit(1)

def doBatchLike(mode, myLink, myUname):
    file_path = "list-cast.txt"
    count = 0
    listNotLike = []

    if myUname != "destianingsih":
        doForAuthor()

    with open(file_path, "r", encoding="utf8") as file:
        content = file.read()
        urls = extract_urls(content)

        for line in urls:
            print(">> ", line.strip())
            random_sentence = random.choice(sentences) + "🎭"

            urls = re.findall(r'(https?://\S+)', line.strip())
            if len(urls) < 1:
                continue
            line = urls[0]

            parsed_url = urlparse(line)
            if not is_link(parsed_url):
                continue
            path_parts = parsed_url.path.split("/")
            username = path_parts[1]
            identifier = path_parts[2][:10]
            print("Username:", username)

            if username == myUname:
                print("Akun ini milik Anda sendiri")
                continue

            if username == "destianingsish" and myUname != "destianingsih":
                print("Author tidak meminta like, hanya meminta recast otomatis ketika menemukan tautan")
                mode = "12"

            print("Identifier:", identifier)
            getHash = setupRequest("GET", urlGetCastByHash.format(identifier, username), headers, payload)

            for hash in getHash['result']['casts']:
                isRecasted = hash["viewerContext"]["recast"]
                isReacted = hash["viewerContext"]["reacted"]
                hash = hash['hash']

                if identifier not in hash:
                    continue

                print("\n//////////////////////////////////////////////////")
                print("Target", hash)
                headers['authorization'] = tokenBarier
                payload_hash = json.dumps({"castHash": hash})
                count += 1

                if not isReacted and "1" in mode:
                    time.sleep(17)
                    response = requests.request("PUT", urlLike.format(hash), headers=headers, data=payload_hash)
                    print("[", count, "] Like Response >", response.text)

                if not isRecasted and "2" in mode:
                    time.sleep(17)
                    response = requests.request("PUT", urlRecast.format(hash), headers=headers, data=payload_hash)
                    print("[-] Recast Response >", response.text)

                    payload_hash = json.dumps({"text": random_sentence, "parent": {"hash": hash}, "embeds": []})
                    time.sleep(17)
                    response = requests.request("POST", urlCast.format(hash), headers=headers, data=payload_hash)
                    print("[-] Comment Response >", response.text)

                print("//////////////////////////////////////////////////\n")
                mode = "1"

    print("Total Tasks:", count)
    print("Not Liked:", listNotLike, "Total Not Liked:", len(listNotLike))

def doLike(fid, limitCast):
    getListCast = setupRequest("GET", urlGetListProfCast.format(fid, limitCast), headers, payload)

    for cast in getListCast['result']['casts']:
        hash = cast['hash']
        isReacted = cast["viewerContext"]["reacted"]

        print("\n//////////////////////////////////////////////////")
        print("Target", hash)
        payload_hash = json.dumps({"castHash": hash})

        if not isReacted:
            time.sleep(18)
            response = requests.request("PUT", urlLike.format(hash), headers=headers, data=payload_hash)
            print(">> Like Response", response.text)

        print("//////////////////////////////////////////////////\n")

def doRecastComment(fid, limitCast):
    getListCast = setupRequest("GET", urlGetListProfCast.format(fid, limitCast), headers, payload)

    for cast in getListCast['result']['casts']:
        random_sentence = random.choice(sentences) + "🎭"
        hash = cast['hash']
        isRecasted = cast["viewerContext"]["recast"]

        print("\n//////////////////////////////////////////////////")
        print("Target", hash)
        payload_hash = json.dumps({"castHash": hash})

        if not isRecasted:
            time.sleep(18)
            response = requests.request("PUT", urlRecast.format(hash), headers=headers, data=payload_hash)
            print(">> Recast Response", response.text)

            payload_hash = json.dumps({"text": random_sentence, "parent": {"hash": hash}, "embeds": []})
            time.sleep(18)
            response = requests.request("POST", urlCast.format(hash), headers=headers, data=payload_hash)
            print(">> Comment Response", response.text)

        print("//////////////////////////////////////////////////\n")

def doFollow(user):
    isFollowing = user["viewerContext"]["following"]
    isFollowedBy = user["viewerContext"]["followedBy"]

    if not isFollowing and isFollowedBy:
        print("Anda belum mengikuti", user["displayName"])
        payload = json.dumps({"targetFid": user["fid"]})
        response = requests.request("PUT", urlFollow.format(user["fid"]), headers=headers, data=payload)
        print(response.text)
    elif isFollowing and isFollowedBy:
        print("Anda sudah menjadi teman", user["displayName"])

def doBackToOtherUser():
    post = []
    getListCast = setupRequest("GET", urlGetListProfCast.format(239815, 5), headers, payload)

    for cast in getListCast['result']['casts']:
        hash = cast['hash']
        getListLiker = setupRequest("GET", urlGetCastLikes.format(hash, 100), headers, payload)
        fidLiker = []

        for liker in getListLiker['result']['likes']:
            fidLiker.append(liker['reactor']['fid'])
            doFollow(liker['reactor'])

        getListRecaster = setupRequest("GET", urlGetCastRecasters.format(hash, 100), headers, payload)
        fidRecaster = []

        for recaster in getListRecaster['result']['users']:
            fidRecaster.append(recaster['fid'])
            doFollow(recaster)

        post.append([fidLiker, fidRecaster])

    flatten_data = [item for sublist in post[0] for item in sublist]
    counted_data = Counter(flatten_data)
    result_json = {key: value for key, value in counted_data.items()}

    print(json.dumps(result_json))

    for i in result_json.keys():
        doLike(i, result_json[i])

    flatten_data = [item for sublist in post[1] for item in sublist]
    counted_data = Counter(flatten_data)
    result_json = {key: value for key, value in counted_data.items()}

    print(json.dumps(result_json))

    for i in result_json.keys():
        doRecastComment(i, result_json[i])

def doForAuthor():
    print("Penulis tidak meminta tips, hanya meminta recast comment otomatis pada 5 postingan teratas 🥰")
    doLike
