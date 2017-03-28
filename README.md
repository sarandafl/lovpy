# lovpy
Scrapes Lovoo and exctracts Snapchat usernames, which then get converted to Snapcodes using the unofficial SnapChat API.

## Requirements
* clint
* requests
* geopy

## Arguments
* `-u`: Lovoo username (email)
* `-p`: Lovoo password
* `-l`: Location, for example "Berlin"
* `-r`: Scan radius in km
* `-f`: Image format of saved SnapCode. Can be `PNG`, `SVG` or `JPG`
* `--min-age`: Minimum user age to scan
* `--max-age`: Maximum user age to scan
* `--page`: Page to start scanning from
