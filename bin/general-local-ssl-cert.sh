#!/usr/bin/env bash

if [ -z $1 ] ; then
  echo "Usage: $0 <hostname>"
  exit
fi

HOSTNAME=${1}
OUTDIR="${PWD}/certs"

mkdir -p "${OUTDIR}"

openssl req \
    -newkey rsa:2048 \
    -x509 \
    -nodes \
    -keyout "${OUTDIR}/${HOSTNAME}.key" \
    -new \
    -out "${OUTDIR}/${HOSTNAME}.crt" \
    -subj /CN=\*.${HOSTNAME} \
    -reqexts SAN \
    -extensions SAN \
    -config <(cat /System/Library/OpenSSL/openssl.cnf \
        <(printf "[SAN]\nsubjectAltName=DNS:\*.${HOSTNAME}")) \
    -sha256 \
    -days 3650