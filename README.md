# 🕸️ Recursive web crawler

### About the task

This crawler does not implement functionality to continue loading after an interruption. Which, however, can be added without rewriting the program from scratch. 
What I also think should be implemented can be found in the TODO lists in the source code.

You could have done with the standard libraries, but due to time constraints I did not do so.
In a real project I would use the [scrapy](https://scrapy.org/) library.

### How to run

Recommended way, via Docker: `docker build . -t ${PWD##*/} && docker run --rm -v $(pwd):/app ${PWD##*/} "https://yahoo.com" "mirror"`
Where the second-to-last parameter is the url and the last one is the directory.


Alternatively: ```pip install -r requirements.txt
crawler.py [OPTIONS] START_URL DESTINATION ```


```❯ python3 crawler.py --help
Usage: crawler.py [OPTIONS] START_URL DESTINATION

  Recursive website crawler. Supports parametrization of the number of
  simultaneous threads, setting a directory for downloading files, limiting
  maximum number of requests within one session and verbose output. See
  crawler.py --help for more details on parameters.

Arguments:
  START_URL    [required]
  DESTINATION  [required]

Options:
  --max-requests INTEGER          [default: 128]
  --parallel-workers INTEGER      [default: 4]
  --verbose / --no-verbose        [default: False]
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.

  --help                          Show this message and exit.
```

