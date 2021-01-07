# Welcome to playback-proxy 👋
![Version](https://img.shields.io/badge/version-0.1.0-blue.svg?cacheSeconds=2592000)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A proxy tool that records communication (requests, websockets) between client and server. This recording can later be used for tests as a mock backend. It works in 2 modes, **RECORD** and **PLAYBACK**, capturing and reproducing the server responses respectively. 

## Supported Features
- Record multiple calls to the same endpoint. These will be reproduced in the same order during **PLAYBACK** as they were requested.
- Record web socket events. These will be reproduced based on the last request and time before socket was received. This means that if the socket was received 2 seconds after a particular call in **RECORD** mode, during **PLAYBACK** it will be sent 2 seconds after that particular call is requested.
- Specify a list of endpoints that are recorded only once. Same response will be used during **PLAYBACK** for every call. See _SAVE_SINGLE_ parameter in the `.env` file 
- Specify a list of endpoints that are not printed to the log. See _IGNORE_LOG_ parameter in the `.env` file

## Unsupported (yet) Features
- Saving responses in any other format (json, plaintext) than binary
- Using `https` and `wss` protocols
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
Set up an [`.env` file](https://github.com/kaphacius/playback-proxy/blob/main/template.env)

## 🚀 Usage
```sh
./proxy-starter.sh -m {MODE} -r {RECORDING_NAME} -e {PATH_TO_ENV_FILE} -a {PROXY_SERVER_ADDRESS} -p {PROXY_PORT}
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
