# Pinterest Board Scraper
Fork of the repos https://github.com/ankitshekhawat/pinterest-scraper, this version has automatic login and can scrap and download a list of Pinterest bourds and sub-boards.
## Requirements:

- Python 3
- Selenium (pip3 install selenium)
- [Chrome driver](https://sites.google.com/chromium.org/driver/downloads) ( Download and place in the directory) 
- aria2c (a command line download utility)
	- Mac: `brew install aria2`
	- Ubuntu: `sudo apt install aria2`
	- Centos/Fedora: `sudo yum install aria2`

- A [Pinterest](http://www.pinterest.com) Account

## How to Run:

- `mv ./config_sample.py ./config.py`
- Add your username, password, pinterest URL, boards URL and output directory to config.py
- Then execute:
	- `./scraper.py`
