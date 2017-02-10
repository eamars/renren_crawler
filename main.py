__author__ = "Ran Bao"

import threading
import queue
import time
import urllib.request
import gzip
from lxml import html
import random
import os
import re

# import settings
import settings


def initiate_http_request(url: str, additional_headers: list=None):
    # build http header
    request = urllib.request.Request(url)
    request.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36")
    request.add_header("Accept", "*/*")
    request.add_header("Accept-Encoding", "gzip, deflate, sdch")
    request.add_header("Accept-Language", "en,zh-CN;q=0.8,zh;q=0.6")

    # add additional headers
    if additional_headers is not None:
        for pair in additional_headers:
            request.add_header(pair[0], pair[1])

    # get http response
    response = None
    retries = 0

    while True:
        try:
            retries += 1

            # the response will return as if the response were successfully fetched
            response = urllib.request.urlopen(request).read()
            break

        # handle http error
        except urllib.request.HTTPError as e:
            print("HTTPError: ", e)

            # the program will try to fetch the content unless the error code is 404
            if e.code == 404:
                break

            print("Retry in {} seconds ({}/{})".format(settings.BACKOFF_TIMER, retries, settings.MAX_RETRIES))
            time.sleep(settings.BACKOFF_TIMER)

        # handle unknown error
        except Exception as e:
            print("OtherError: ", e)

        # if the maximum retries exceeded the threshold, then break
        if retries >= settings.MAX_RETRIES:
            break

    return response


# worker thread
def worker(args):
    task_queue: queue.Queue = args # add type annotation for parameters

    # get thread id
    thread_id = threading.current_thread().name
    print(thread_id, "starts")

    while True:
        task = task_queue.get()

        # stop on receiving None
        if task is None:
            break

        # print accepted task
        print(thread_id, "receives", task)

        # print approximate number of tasks left in the queue
        print(thread_id, "{} tasks left".format(task_queue.qsize()))

        # ============= Task start =============
        # get a random delay between each tasks
        # time.sleep(random.randint(1, 5))

        downloaded_folder = task[0]
        album_name = task[1]
        image_url = task[2]

        album_path = downloaded_folder + "/" + album_name
        image_path = album_path + "/" + image_url.split("/")[-1]

        # create folder for each album
        if not os.path.exists(album_path):
            os.mkdir(album_path)

        # download image
        image_fp = open(image_path, "wb")
        response = initiate_http_request(image_url, settings.image_request_headers)

        image_fp.write(response)
        image_fp.close()


        # ============== Task end ==============


# main thread
def main():
    # create fifo queue
    task_queue = queue.Queue()

    # create thread pool
    thread_pool = []

    # initialize workers
    for _ in range(settings.NUM_WORKERS):
        thread = threading.Thread(target=worker, args=[task_queue])
        thread.start()
        thread_pool.append(thread)

    # ============= Task allocation start =============

    # read http response
    response = initiate_http_request("http://photo.renren.com/photo/{}/albumlist/v7#".format(settings.renren_id), settings.additional_headers)

    # decompress and decode with utf-8
    text = gzip.decompress(response).decode("utf-8")

    # parse with lxml
    parsed_body = html.fromstring(text)

    # extract js
    js = parsed_body.xpath("//script/text()")

    # get js for album
    album_js = js[3]
    album_raw = re.findall(r"'albumList':\s*(\[.*?\]),", album_js)[0]
    album_list = eval(album_raw)

    # get real address for each album
    album_url_dict = {}
    for album in album_list:
        if album["sourceControl"] == 99: # have access to this album
            album_url = "http://photo.renren.com/photo/"
            album_url += str(album["ownerId"]) + "/"
            album_url += "album-" + album["albumId"] + "/v7"

            album_url_dict[album['albumId']] = {}
            album_url_dict[album['albumId']]['album_url'] = album_url
            album_url_dict[album['albumId']]['photo_count'] = album['photoCount']
            album_url_dict[album['albumId']]['album_name'] = album['albumName']

    # fetch image list in each album
    image_dict = {}

    for key in album_url_dict:
        value = album_url_dict[key]
        album_url = value["album_url"]

        response = initiate_http_request(album_url, settings.additional_headers)
        text = gzip.decompress(response).decode("utf-8")
        parsed_body = html.fromstring(text)

        js = parsed_body.xpath("//script/text()")
        text = js[3]
        image_list = re.findall(r'"url":"(.*?)"', text)
        image_dict[key] = image_list

    #
    for key in image_dict:
        album_id = key
        image_list = image_dict[key]
        album_name = album_url_dict[album_id]["album_name"]

        # remove \\ in each url
        image_list_updated = [i.replace("\\", '') for i in image_list]

        # send tasks to each thread
        for image_url in image_list_updated:
            # pack album name with each image and deliver to worker thread
            task = ("downloaded", album_name, image_url)
            task_queue.put(task)


    # ============== Task allocation end ==============

    # approximate number of tasks in the queue
    print("{} tasks were assigned to workers".format(task_queue.qsize()))

    # complete tasks
    for _ in range(settings.NUM_WORKERS):
        task_queue.put(None)

    print("Waiting...")

    # wait until all threads terminated
    for thread in thread_pool:
        thread.join()

    # complete tasks
    print("Done")


if __name__ == "__main__":
    main()