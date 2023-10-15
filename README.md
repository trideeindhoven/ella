# Ella
A forensic tool to crawl and store website content

## What is "Ella"
Apart from this tool, Ella is a cat known for being very inquisite. It only seemed appropriate to name the tool after her.  
![Ella the cat](ella.jpg "Ella the cat")
## Why have you made this tool?
In 2023, after a year of researching, i worked with investigative journalist platform "[Follow The Money](https://www.ftm.eu "Follow The Money")" (FTM) to publish an article about security malpractises of the Chinese firm [Yealink](https://www.yealink.com "Yealink").
As a direct consequence of this article i was legally threatened with consequences that would ruin my life completely.
Because Yealink and Dutch distributor [Lydis](https://www.lydis.nl "Lydis") were sometimes creative with the truth i felt i had to help them a bit remembering facts.
## So what does this tool do?
This tool takes a list of url's from urls.csv. It then starts a new, headless, Firefox browser and visits the url. The result of this crawl is stored in a .har file. This is an industry-standard way of storing pretty much everything about the visit to the website, including headers, timing information, http-codes, etc.
Ella then downloads all external PDF files and also stores them. This package of PDF files and .har files is then push to a remote github.com repository, so that it no longer resides on hardware that i personally administrate. This automatically means the data crawled is now stored, timstamped and immutable on an external, public server available for, say, a judge to look at.
## So how do i install Ella?
It is easiest to create a python3 venv environment and run everything in there:

(optionally if not yet installed:)

    sudo apt install python3-venv
    sudo apt install firefox
Next install Ella and it's venv:

    git clone https://github.com/trideeindhoven/ella.git
    cd ella
    python3 -m venv venv
    venv/bin/pip3 install selenium-wire GitPython requests
    cd github
    ssh-keygen -f ./ella -N ""
now use this key in github as a deploy key in your repository>

    cd ..
    cp config.py.example config.py
Now edit config.py and
create urls.py (see example)

    venv/bin/python3 ./ella.py
