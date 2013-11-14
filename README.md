ddvisualizer
============

## dohodathi
[website](http://www.dohodathi.de/)

## Requirements

Packages ...
```shell
sudo apt-get install libpq-dev python-dev
```

Templating doned by [Jinja2](http://jinja.pocoo.org/).

```shell
pip install jinja2
```

You could simply use a [Virtual Environment](https://pypi.python.org/pypi/virtualenv) and install from the rquirements file.

```shell
pip install -r requirements.txt
```

## Functionality

```shell
python visualizer.py -psql|-mysql|-sqllite DB_URI [-n name]
```
