Renren Album Crawler
====================

Acknowledgement: The downloaded web page and images may contain materials that are not suitable for you.

A simple multi-threaded web crawlers that downloads pictures from [人人 (Chinese contents)](http://www.renren.com/), inspired by [pein0119's code](https://github.com/pein0119/renren_photos_crawler).

Features:
 - Download albums from your renren gallery.
 - Parallel fetching contents from website.
 - Requires given [Cookie](https://en.wikipedia.org/wiki/HTTP_cookie) with existing login information.
 
Installation
------------

Download and build from source:

        git clone https://github.com/eamars/renren_crawler.git

Requirements
------------
 - MacOS Sierra 10.12.3
 - Python 3.6
 - lxml

You can install external dependencies with 

        pip3 install lxml
        
Configuration
-------------
You need to replace your own cookie in "Cookie" field in `additional_headers` and `image_request_headers` in `settings.py`.

Additionally, you will need to provide your own Renren ID in `renren_id` field in `settings.py`.

Usage
-----
As soon as you have pasted your own cookie in `settings.py`, you can download your entire renren gallery with one command:
        
        python3 main.py

The downloaded images with corresponding album name will be located in `downloaded` folder at the same directory with the place you executed the command.
