# CTF_Parser

Notification system for the FH Dortmund ctf news

## Requirements

* pythno3
* requirements from `requirements.txt`
* a bot created with the [botfather](https://core.telegram.org/bots)
* A telegram channel or supergroup with the bot as an admin
* Aplace to run this script repeatedly e. g. AWS Lambda or a VM with a cronjob

## Usage

Install the requirements

```shell
pip3 install -r requirements.txt
````

Run the script

```shell
python3 main.py <token>
```
