Kimsufi/So-you-Start Avaliability Crawler
============================

> Crawler that will notify you when Kimsufi servers (or So-you-Start, or OVH) become available for purchase.

**TL;DR**

    git clone https://github.com/MA3STR0/kimsufi-crawler.git
    cd kimsufi-crawler
    cp config.json.example config.json
    vim config.json   # edit config.json file to set up your nofitication preferences
    sudo pip install "tornado>=4.0.0"
    python crawler.py

About
-----

Dedicated servers on [Kimsufi](http://www.kimsufi.com) and [So you Start](http://www.soyoustart.com) have amazing prices, however they are always out of stock. This crawler will notify you as aoon as servers are available for purchase; it can send emails, show Mac OS notifications, open popup windows, or even trigger sms. Then hurry up, you have around 2 minutes to complete your order :)


Set it up
---------

**Runs on Linux and Mac with Python 2.7+ or Python 3.4+**

- Clone this repo (`git clone https://github.com/MA3STR0/kimsufi-crawler.git`) or download and unpack archive
- Taking `config.json.example` as a template, create a file `config.json` and correct configuration according to your preferences:
  - `servers`: list of servers that should be tracked, eg `["KS-1", "KS-2 SSD", "GAME-2"]` etc. All supported server names can be found in mapping file [mapping/server_types.json](/mapping/server_types.json) as values)

  - `region`: desired location of server, `canada` or `europe`

  - `notifier`: notification mechanism, choose between:
    - `"email"`: default, requires additional email account settings
    - `"popup"`: simple popup window, platform-independent
    - `"osx"`: Mac OS-X desktop notifications (using terminal-notifier)
    - `"smsapi"`: sms through smsapi.pl gateway, requires account

  - `to_email`: your email to receive notifications
  - `from_email`: email account of the crawler.
  - `from_pwd`, `from_smtp_host`: smtp configuration of crawler email account

- Crawler runs on Python 2.7+ and Tornado framework 4.0+. Assuming that you already have Python/pip, just get Tornado with `sudo pip install "tornado>=4.0.0"`. You can also set up virtualenv if you like.
- Run with `python crawler.py`
- It's a good idea to register an account on Kimsufi/OVH in advance; just pick any available server on www.kimsufi.com and sign up without paying. This way later you will only need to log in and enter payment details, which saves a lot of time.
- Get and enjoy awesome cheap servers!

**Config check**

Crawler makes an initial check of the config file during startup, so if you have any syntax errors or missing software dependencies - console logs will let you know.

Advanced configuration
----------------------

You can add more options to the config.json if you need:

- `"crawler_interval": 8`    // overriding default periodic callback timeout in seconds (10 by default, should be more than 7.2)
- `"from_smtp_port": 25` // use non-standard smtp port (587 by default)
- `"use_starttls": true` // forcing encrypted SMTP session using TLS (true by default)
- `"use_ssl": false` // forcing encrypted SMTP session using SSL (false by default)
- `"from_user": "sender@domain.com"`  // if smtp user is different from `from_email`
- `"from_smtp_port": 587` // if you have non-standard (587) smtp port

**Versions**

These instructions are based on Version 2 of the crawler. You can access last stable release of v1 by browsing through [release history](https://github.com/MA3STR0/kimsufi-crawler/releases)
