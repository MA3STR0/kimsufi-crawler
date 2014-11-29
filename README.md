Kimsufi Avaliability Crawler
============================

> Crawler that will send you email notifications as soon as servers on Kimsufi/OVH become available for purchase.

**TL;DR**

    git clone kimsufi-crawler
    cd kimsufi-crawler
    cp config.json.example config.json
    vim config.json   # edit config.json file to set up your nofitication preferences
    sudo pip install tornado>=4.0.0
    python crawler.py

About
-----

Dedicated servers on [Kimsufi](www.kimsufi.com) are currently offered with amazing prices, however they are always out of stock. There is pretty much zero chance to get one without using some sort of crawler that would notify you as aoon as servers are available for purchase. This is exactly what this software does. Clone the repo, set it up and run the crawler; you will receive an email notification when a server of your choice will be available. Then you have 5-10 minutes to order it.

Set it up
---------

_Following steps have been tested on Mac and Linux_

- Clone this repo (`git clone kimsufi-crawler`) or download and unpack archive
- Taking `config.json.example` as a template, create a file `config.json` and correct configuration according to your preferences:
  - `from_email`, `from_pwd`, `from_smtp_host`, `from_smtp_port`: email account configuration that crawler should use for sending notifications
  - `to_email`: your email, will be used as a recipient of notifications
  - `servers`: list of servers that should be tracked (eg `["KS-1", "KS-2", "KS-3"]`)
  - `zones`: list of datacenter locations that interest you (eg `["rbx", "bhs"]`)
    - `bhs` is Beauharnois, Canada (best for Americas),
    - `rbx` is Roubaix, France (best for Western Europe),
    - `sbg` is Strasbourg, France (best for Central Europe)

- Crawler runs on Python 2.7-3.4 and tornado framework (tested on 4.0.2), assuming that you already have Python/pip, just get tornado with `sudo pip install tornado>=4.0.0`. You can also set up virtual-env if you like.
- Run with `python crawler.py`
- Get and enjoy awesome Kimsufi servers!
