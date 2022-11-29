# moodle-a11ycat

This is CLI tool for Moodle accessibility testing.

It works by downloading course materials from Moodle, converting them to HTML, then scanning that HTML against WCAG standards. Please note that this tool is very much a work in progress, and is not yet ready for production use.


## Requirements

`Python 3.10+`

`nodejs 18.8+`

`npm 8.18+`

## Setup 

```
pip install -r requirements.txt
npm i --global access-sniff
python3 main.py

Copy `local.env` to `.env` fill out
```