Kimsufi/So-you-Start Avaliability Crawler
============================

> Crawler that will notify you when Kimsufi servers (or So-you-Start, or OVH) become available for purchase.



    git clone https://github.com/MA3STR0/kimsufi-crawler.git
    cd kimsufi-crawler
    cp config.json.example config.json
    vim config.json   # edit config.json file to set up your nofitication preferences
    sudo pip install -r requirements.txt
    python crawler.py

About
-----

Dedicated servers on [Kimsufi](http://www.kimsufi.com) and [So you Start](http://www.soyoustart.com) have amazing prices, however they are always out of stock. This crawler will notify you as aoon as servers are available for purchase; it can send emails, show Mac OS notifications, open popup windows, or even trigger sms. Then hurry up, you have around 2 minutes to complete your order :)


Set it up
---------

**Runs on Linux, Mac and Widnows with Python 2.7+ or Python 3.4+**

- Clone this repo (`git clone https://github.com/MA3STR0/kimsufi-crawler.git`) or download and unpack archive
- Taking `config.json.example` as a template, create a file `config.json` and correct configuration according to your preferences:
  - `servers`: list of servers that should be tracked, eg `["KS-1", "KS-2 SSD", "GAME-2"]` etc. All supported server names can be found in mapping file [mapping/server_types.json](/mapping/server_types.json) as values)

  - `region`: desired location of server, `canada` or `europe`

  - `notifier`: notification mechanism, choose between:
    - `"email"`: default, requires additional email account settings
    - `"popup"`: simple popup window, platform-independent
    - `"popup_pywin"`: simple popup window, displays on top of all other windows (Windows only, requires pywin32 package)
    - `"osx"`: Mac OS-X desktop notifications (using terminal-notifier)
    - `"smsapi"`: sms through smsapi.pl gateway, requires account
    - `"xmpp"`: send jabber/xmpp message, requires account - needs xmpppy
    - `"pushover"`: send Pushover message, requires account - needs chump
    - `"pushbullet"`: send Pushbullet message, requires account - needs pushbullet

  - `to_email`: your email to receive notifications
  - `from_email`: email account of the crawler.
  - `from_pwd`, `from_smtp_host`: smtp configuration of crawler email account
  - `xmpp_jid`, `xmpp_password`, `xmpp_recipient`, `xmpp_send_test`: xmpp configuration of sending jabber account
  - `pushover_application_id`, `pushover_user_id`: your Pushover configuration, messages are sent to all devices assigned to user
  - `pushbullet_apikey`: your Pushbullet API key, notification sent to all devices.

- Crawler runs on Python 2.7+ and Tornado framework 4.0+. Assuming that you already have Python/pip, just get Tornado and the notifier dependencies with `sudo pip install -r requirements.txt`. You can also set up virtualenv if you like.
- Run with `python crawler.py`. If no error messages come, you're ready.
- (optional) If your pip install command fails due to xmpppy being on pre-release version (eg. 0.5.0rc1) use: `sudo pip install --pre -r requirements.txt`
- (optional) In case of problems with easygui installation on Ubuntu, you can get it also with `sudo apt-get install python-easygui`
- (optional) It's a good idea to register an account on Kimsufi/OVH in advance; just pick any available server on www.kimsufi.com and sign up without paying. This way later you will only need to log in and enter payment details, which saves a lot of time.

**Test everything**

You may test the whole chain by setting some popular servers in your
config.json, for example ["KS-3A", "KS-3B", "KS-2E"]. Since those are always
available, you should receive a notification immediately.

**Config check**

Crawler makes an initial check of the config file during startup, so if you have any syntax errors or missing software dependencies - console logs will let you know.


Advanced configuration
----------------------

You can add more options to the config.json if you need:

- `"crawler_interval": 8` // overriding default periodic callback interval in seconds (should be more than 7.2 to avoid rate-limit)
- `"request_timeout": 30` // http timeout for API requests.
- `"from_smtp_port": 587` // use non-standard smtp port
- `"use_starttls": true` // forcing encrypted SMTP session using TLS (true by default)
- `"use_ssl": false` // forcing encrypted SMTP session using SSL (false by default)
- `"from_user": "sender@domain.com"`  // if smtp user is different from `from_email`
- `"from_smtp_port": 587` // if you have non-standard smtp port

**Versions**

These instructions are based on Version 2 of the crawler. You can access last stable release of v1 by browsing through [release history](https://github.com/MA3STR0/kimsufi-crawler/releases)
