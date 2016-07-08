# fosdem-video-script

Utility script to find videos provided by http://video.fosdem.org.


## Installation

```
docker build -t orzen/fosdem-video .
```

## Usage

The script is constructing a JSON file with the scraped data. In order for the
script to work, this file must be stored and accessible for the script when
searching.

```
docker run -it -v $(pwd):/home/fosdem orzen/fosdem-video [args]
```

Alternatively (this is the command shown above in a shell script)

```
./fosdem-video-script.sh [args]
```
