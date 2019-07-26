import requests

url = "https://gss3.baidu.com/6LZ0ej3k1Qd3ote6lo7D0j9wehsv/tieba-smallvideo-transcode/1204669_d2597d031c78b63edb4d382eac011e44_0.mp4"

while True:
    try:
        response = requests.get(url, stream=True)
        with open("video.mp4", 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        print("视频下载完成")
        break
    except Exception as e:
        print("下载出错", e)
