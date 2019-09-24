# nord-sirius

![CloudBerg Little Printer](https://i.vimeocdn.com/video/222115839_1280x720.jpg)

This repository is a fork of [genmon/sirius](https://github.com/genmon/sirius), developed and maintained by [Nord Projects](https://nordprojects.co).

Want to try it out? We have an instance running at http://littleprinter.nordprojects.co which all are welcome to use!

# How to use

Want to get your Little Printer online?

- Hack the Berg Cloud bridge. Follow our [step-by-step guide](https://docs.google.com/document/d/1JT1f2ClVdAnjrnby92V9ONBnN05EFQGYpLG5ijl5KRI/edit?usp=sharing) here.

  - If you've already got a hacked bridge using the alpha.littleprinter.com
    backend, use the guide above but start at step 6.

- Once it's paired with this server, you can use Device Keys with our iOS app,
  [Little Printers](https://itunes.apple.com/us/app/little-printers/id1393105914?ls=1&mt=8),
  which is also [open source](https://github.com/nordprojects/littleprinters-ios-app)!

### Using the device key API

Use Device Keys to print through an API. Create a device key from the web
interface, and go to that URL to view API documentation.

# Developing Sirius

## Running on Heroku

We run an instance of this server on Heroku, at [littleprinter.nordprojects.co](https://littleprinter.nordprojects.co). You are welcome to use our instance!

If you want to run it yourself, this app will run on Heroku, but you need a
static IP address due to the way the Berg Bridge connects. We have a droplet
at Digital Ocean running nginx to forward the HTTPS connection on to Heroku.

It should also be possible to run in Docker, dokku, or directly with gunicorn,
but we don't use it that way :).

## Running locally via Docker

There's a development Docker setup that adds Postgres for you, by running:

```sh
docker-compose -f docker-compose.yml -f docker-compose.development.yml up
```

Or if you have your own database, you can configure the `DEV_DATABASE_URL` environment variable in `.env`, and then simply run:

```
docker-compose up
```

### Environment variables

The server can be configured with the following variables:

```
TWITTER_CONSUMER_KEY=...
TWITTER_CONSUMER_SECRET=...
FLASK_CONFIG=...
DATABASE_URL=...
```

These can be set in the `.env` file, and an example is available in `.env.sample` in your checkout.

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
