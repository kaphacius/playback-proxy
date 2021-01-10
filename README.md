# Welcome to playback-proxy 👋
![Version](https://img.shields.io/badge/version-0.1.0-blue.svg?cacheSeconds=2592000)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A proxy tool that records communication (requests, websockets) between client and server. This recording can later be used for tests as a mock backend. It works in 2 modes, **RECORD** and **PLAYBACK**, capturing and reproducing the server responses respectively. 

## Supported Features
- Record multiple calls to the same endpoint. These will be reproduced in the same order during **PLAYBACK** as they were requested.
- Record web socket events. These will be reproduced based on the last request and time before socket was received. This means that if the socket was received 2 seconds after a particular call in **RECORD** mode, during **PLAYBACK** it will be sent 2 seconds after that particular call is requested.
- Specify a list of endpoints that are recorded only once. Same response will be used during **PLAYBACK** for every call. See `SAVE_SINGLE` parameter in the `.env` file 
- Specify a list of endpoints that are not printed to the log. See `IGNORE_LOG` parameter in the `.env` file

## Unsupported (yet) Features
- Saving responses in any other format (json, plaintext) than binary
- Using `https` and `wss` protocols
- Support for HAR files as records
- Support for optional delay
- Any other ideas people might have

## Install
```sh
git clone https://github.com/kaphacius/playback-proxy.git
```

## Setup
Install all dependencies with
```sh
pip3 install requirements.txt
```

## 🚀 Usage
There are 2 modes of running the tool: RECORD and PLAYBACK.
- During RECORD, all communication between client and server is stored.
- Duruing PLAYBACK, the socket uses previously stored responses when being requested.

Firstly, set up an `.env` [file](https://github.com/kaphacius/playback-proxy/blob/main/template.env) with mandatory and optional parameters. Copy the and rename [*template.env*](https://github.com/kaphacius/playback-proxy/blob/main/template.env) to a desired name.
Mandatory parameters:
- `PROTOCOL` - protocol used for communication (only http for now)
- `ENDPOINT` - the address of the server to which the proxy will connect to
- `MODE` - current mode. Can be changed later during when launching the proxy.
- `RECORDS_PATH` - relative path to where all of the recordings will be stored. Must exists before running.
- `RECORDING` - name of the current recording. This will be appended to RECORDS_PATH and a folder will be created to store saved data. Can be changed later when launching the proxy.

Make the starter script executable:
```sh
chmod +x proxy-starter.sh
```
Then, run the proxy in ***RECORD*** mode. Specify the name of the current recording `RECORDING`. This will create a folder (or use an existing one) where the responses will be saved. Set relative path to your specific `.env` file via `PATH_TO_ENV_FILE`. Specify address and port where the client will be connecting via `PROXY_SERVER_ADDRESS` and `PROXY_PORT`. 
```sh
./proxy-starter.sh -m RECORD -r {RECORDING} -e {PATH_TO_ENV_FILE} -a {PROXY_SERVER_ADDRESS} -p {PROXY_PORT}
```
Perform necessary interactions with the backend and stop the proxy by pressing `Ctrl+C`.

Finally, run the proxy in ***PLAYBACK*** mode. Interact with the server the same way as during recording - receive the same responses.
```sh
./proxy-starter.sh -m PLAYBACK -r {RECORDING} -e {PATH_TO_ENV_FILE} -a {PROXY_SERVER_ADDRESS} -p {PROXY_PORT}
```

## Author

👤 **Yurii Zadoianchuk**

* Github: [@kaphacius](https://github.com/kaphacius)

## 🤝 Contributing

Contributions, issues and feature requests are welcome!

Feel free to check [issues page](https://github.com/kaphacius/playback-proxy/issues). 

## Show your support

Give a ⭐️ if this project helped you!

## 📝 License

Copyright © 2021 [Yurii Zadoianchuk](https://github.com/kaphacius).

This project is [MIT](https://opensource.org/licenses/MIT) licensed.

***
_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_
