# -*- coding: utf-8 -*-

# 참고 : https://developers.google.com/explorer-help/code-samples#python

import argparse
import configparser
import csv
import time

# import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

# scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
config = configparser.ConfigParser()
config.read('./config.ini')
api_key = config['KEY']['ApiKey']
api_service_name = "youtube"
api_version = "v3"
youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key)

# 채팅 내용 CSV로 저장
def convertDicToCSV(dicList, video_id, channel_id)->None:
    fieldnames = ['time','message','user']
    file_name = f"{channel_id}_{video_id}.csv"

    with open(file_name, "a", encoding='utf-8-sig', newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # writer.writeheader()
        for item in dicList:
            _time = item["snippet"]["publishedAt"]
            _message = item["snippet"]["textMessageDetails"]["messageText"]
            _user = item["authorDetails"]["displayName"]
            writer.writerow({'time':_time, 'message':_message, 'user':_user})
    csvfile.close()

    return

# 비디오 정보 가져오기
def get_livechat_id(video_id):
    request = youtube.videos().list(
        part="liveStreamingDetails,snippet,status",
        id=video_id
    )
    response = request.execute()
    channel_id = response["items"][0]["snippet"]["channelId"]
    chat_id = response["items"][0]["liveStreamingDetails"]["activeLiveChatId"]
    result = {"channel_id":channel_id, "chat_id":chat_id}

    return result


def main(video_id):
    _get_video_info = get_livechat_id(video_id) # 유튜브 비디오 아이디로 비디오 관련 정보 획득
    _chat_id = _get_video_info["chat_id"] # 실시간 채팅 ID 획득
    _channel_id = _get_video_info["channel_id"] # CSV 파일 이름에 채널 ID 추가를 위한 채널 ID 획득
    
    page_token = ""
    polling_time = 10000

    while True:
        print("Token = " + page_token)
        request = youtube.liveChatMessages().list(
            part="snippet,authorDetails",
            liveChatId=_chat_id,
            pageToken=page_token
        )
        response = request.execute()
        page_token = response["nextPageToken"] # 다음 채팅 정보 획득을 위한 토큰 획득
        convertDicToCSV(response["items"], video_id, _channel_id) # 실시간 채팅 획득 내용을 CSV에 작성
        
        interval_polling_time = response["pollingIntervalMillis"]
        if interval_polling_time > polling_time:
            time.sleep(interval_polling_time / 1000)
        else:
            time.sleep(polling_time / 1000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', help=' : Please set youtube video id (https://www.youtube.com/watch?v=[video_id])')
    args = parser.parse_args()
    main(args.v)
