#!/bin/bash

cd /usr/local/aclu
git clone git@github.com:aclu-national/voter-apple-wallet.git
wget -qO- https://deb.nodesource.com/setup_10.x | sudo -E bash -
sudo apt-get install -y nodejs imagemagick
sudo chown www-data:www-data /usr/local/aclu/voter-apple-wallet/passes
cd voter-apple-wallet
npm install
