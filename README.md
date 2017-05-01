# Sirius - An alternative website for your CloudBerg Little Printer

This repository is a fork of [genmon/sirius](https://github.com/genmon/sirius).
The main project doesn't seem to be maintained anymore.

Differences with the original project :

 * Update requirements.txt to fix some bugs
 * Improve documentation


## Using it

*More documentation will be added soon*

### Interesting links

Before everything else, you might want to understant how to update your CloudBerg Little Printer to use it with Sirius. It seems that before you just had to give your CloudBerg Bridge MAC address and someone pushed the update on your device. Now, it appears that the only option to update your CloudBerg Bridge to use it with Sirius is to root your device. The following links might help you :

  * [Updating the Bridge](https://github.com/genmon/sirius/wiki/Updating-the-Bridge)
  * [Rooting Your BERG Cloud Bridge](http://pipt.github.io/2013/04/15/rooting-berg-cloud-bridge.html)
  * [Getting Little Printer online](http://joerick.me/hardware/2017/03/09/little-printer)
  * [Installing Sirius on Mac / Linux / Raspberry Pi](https://gist.github.com/hako/f8944cfa7b8fb8115f6d)

### Installation

Install and run Sirius on Debian:

```
apt install python python-pip libpq-dev postgresql phantomjs libfreetype6-dev fontconfig libgstreamer1.0-dev python-dev wget libjpeg-dev zlib1g-dev
git clone https://github.com/genmon/sirius
cd sirius

pip install -r requirements.txt

wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.8-linux-x86_64.tar.bz2
tar jxf phantomjs-1.9.8-linux-x86_64.tar.bz2
sudo mv phantomjs-1.9.8-linux-x86_64/bin/phantomjs /usr/local/bin/phantomjs

./manage.py db upgrade head

~/.local/bin/gunicorn -k flask_sockets.worker manage:app -b 0.0.0.0:5002 -w 1
```

Navigate browser to http://127.0.0.1:5002/

You should configure your BergCloud Bridge to point to your Sirius instance.

### Environment variables

The server can be configured with the following variables:

```
TWITTER_CONSUMER_KEY=...
TWITTER_CONSUMER_SECRET=...
FLASK_CONFIG=...
```

For dokku this means using e.g.:

```
dokku config:set sirius FLASK_CONFIG=heroku
dokku config:set sirius TWITTER_CONSUMER_KEY=DdrpQ1uqKuQouwbCsC6OMA4oF
dokku config:set sirius TWITTER_CONSUMER_SECRET=S8XGuhptJ8QIJVmSuIk7k8wv3ULUfMiCh9x1b19PmKSsBh1VDM
```

### Creating fake printers and friends

Resetting the actual hardware all the time gets a bit tiresome so
there's a fake command that creates unclaimed fake little printers:

```console
$ ./manage.py fake printer
[...]
Created printer
     address: 602d48d344b746f5
       DB id: 8
      secret: 66a596840f
  claim code: 5oop-e9dp-hh7v-fjqo
```

Functionally there is no difference between resetting and creating a new printer so we don't distinguish between the two.

To create a fake friend from twitter who signed up do this:

```console
$ ./manage.py fake user stephenfry
```

You can also claim a printer in somebody else's name:

```console
$ ./manage.py fake claim b7235a2b432585eb quentinsf 342f-eyh0-korc-msej testprinter
```

## Sirius Architecture

### Layers

The design is somewhat stratified: each layer only talks to the one
below and above. The ugliest bits are how database and protocol loop
interact.

```
UI / database
----------------------------
protocol_loop / send_message
----------------------------
encoders / decoders
----------------------------
websockets
----------------------------
```

### Information flow (websockets)

The entry point for the bridge is in `sirius.web.webapp`. Each new
websocket connection spawns a gevent thread (specified by running the
flask_sockets gunicorn worker) which runs
`sirius.protocol.protocol_loop.accept` immediately. `accept` registers
the websocket/bridge_address mapping in a global dictionary; it then
loops forever, decoding messages as they come in.


### Claim codes

Devices are associated with an account when a user enters a "claim
code". This claim code contains a "hardware-xor" which is derived via
a lossy 3-byte hash from the device address. The XOR-code for a device
is always the same even though the address changes!

The claim codes are meant to be used "timely", i.e. within a short
window of the printer reset. If there are multiple, conflicting claim
codes we always pick the most recently created code.

We are also deriving this hardware xor when a device calls home with
an "encryption_key_required". In that case we connect the device to
the claim code via the hardware-xor and send back the correct
encryption key.
