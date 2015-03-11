Kimsufi/So-you-Start Avaliability Crawler
============================

> Crawler that will notify as soon as OVH servers on Kimsufi/So-you-Start become available for purchase.

**TL;DR**

    git clone kimsufi-crawler
    cd kimsufi-crawler
    cp config.json.example config.json
    vim config.json   # edit config.json file to set up your nofitication preferences
    sudo pip install "tornado>=4.0.0"
    python crawler.py

About
-----

Dedicated servers on [Kimsufi](http://www.kimsufi.com) and [So you Start](http://www.soyoustart.com) have amazing prices, however they are always out of stock. This crawler will notify you as aoon as servers are available for purchase; it can send emails, show Mac OS notifications, open popup windows, or even trigger sms. Then hurry up, you have around 5 minutes to complete your order :)

Set it up
---------

_Following steps have been tested on Mac and Linux_

- Clone this repo (`git clone kimsufi-crawler`) or download and unpack archive
- Taking `config.json.example` as a template, create a file `config.json` and correct configuration according to your preferences:
  - `servers`: list of servers that should be tracked, eg `["KS-1", "SYS-IP-1", "GAME-2"]` etc

  - `zones`: list of datacenter locations that interest you, eg `["rbx", "bhs"]`
    - `bhs` is Beauharnois, Canada (best for Americas),
    - `rbx` is Roubaix, France (best for Western Europe),
    - `sbg` is Strasbourg, France (best for Central Europe)

  - `notifier`: notification mechanism, choose between:
    - `"email"`: default, requires additional email account settings
    - `"popup"`: simple popup window, platform-independent
    - `"osx"`: Mavericks-like notifications
    - `"smsapi"`: sms through smsapi.pl gateway, requires account

  - `to_email`: your email to receive notifications
  - `from_email`: email account of the crawler.
  - `from_pwd`, `from_smtp_host`, `from_smtp_port`: smtp configuration of crawler email account

- Crawler runs on Python 2.7+ and Tornado framework 4.0+. Assuming that you already have Python/pip, just get Tornado with `sudo pip install "tornado>=4.0.0"`. You can also set up virtualenv if you like.
- Run with `python crawler.py`
- Get and enjoy awesome cheap servers!


**For advanced email/smtp configuration**

You can add more options to the config.json if you need:

- "use_starttls": true, // forcing encrypted SMTP session using TLS (true by default)
- "from_user": "sender@domain.com"  // if smtp user is different from `from_email`
- "from_smtp_port": 587 // if you have non-standard (587) smtp port
