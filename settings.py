'''The configuration file for renren_crawler'''
__author__ = "Ran Bao"

# specify the number of worker threads
NUM_WORKERS = 8

# specify how long the program should wait when network error occurs
BACKOFF_TIMER = 5

# specify maximum retries
MAX_RETRIES = 3

# renren id
renren_id = 0 # paste your renren id here

# additional headers
additional_headers = [
    ("Host", "www.renren.com"),
    ("Referer", "http://www.renren.com/SysHome.do"),
    ("Cache-Control", "max-age=0"),
    ("Cookie", "paste-your-cookie-here")
]

image_request_headers = [
    ("Host", "fmn.rrimg.com"),
    ("Cache-Control", "max-age=0"),
    ("Cookie", "paste-your-cookie-here")
]