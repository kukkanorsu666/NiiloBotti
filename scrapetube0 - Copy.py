import scrapetube

videos = scrapetube.get_channel("UC7WlCq3wvnxgBEbVA9Dyo9w")


for video in videos:
    videoid = video['videoId']
    print("https://www.youtube.com/watch?v=" + videoid)
    break
    #print(video['videoId'])
    

