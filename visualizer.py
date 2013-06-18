#! python
# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import psycopg2
import urlparse
import json
import datetime
import codecs
from jinja2 import Environment
from jinja2 import PackageLoader


TEMPLATE_GENERIC = 'templates/visualizer.html'
HTML_OUT = 'output.html'
JSON_OUT = 'output.json'

DEFAULT_NAME = 'dohodathi - Visualizer'
DEFAULT_MAXDATA = 10

DB_OPTIONS = ['-psql', '-sqlite']


class ConnectError(Exception):
    def __str__(self):
        msg = ('Connection could not be stablished.  '
               'DB-Options: {0}  '
               'POSTGRES-URI: postgres://USERNAME:PASSWORD@HOSTNAME/DATABASE  '
               'MySQL: not implemented yet'
               'SQLite-URI: path/to/the/file.db  '
               ''.format(str(DB_OPTIONS))
               )
        return repr(str(msg))


class Connector(object):
    def getTableData(self, table):
        self.cur.execute("SELECT * FROM " + str(table))
        desc = [tuple[0] for tuple in self.cur.description]
        rows = self.cur.fetchall()
        return desc, rows


class connectSQLite(Connector):
    def __init__(self, db_uri):
        if not os.path.exists(db_uri):
            raise ConnectError
        try:
            self.conn = sqlite3.connect(db_uri)
            self.cur = self.conn.cursor()
        except sqlite3.Error:
            raise ConnectError('...')
            SystemExit

    def getTables(self):
        self.cur.execute("SELECT name FROM sqlite_master WHERE type = \"table\"")
        data = self.cur.fetchall()
        return data


class connectPostgreSQL(Connector):
    def __init__(self, db_uri):
        try:
            db, host, user, pw = self._parseURI(db_uri)
            self.conn = psycopg2.connect(
                database=db,
                host=host,
                user=user,
                password=pw)
            self.cur = self.conn.cursor()
        except:
            raise ConnectError
            SystemExit

    def getTables(self):
        self.cur.execute("SELECT tablename FROM pg_tables WHERE tablename not LIKE \'pg_%\' AND tablename not LIKE \'sql_%\'")
        data = self.cur.fetchall()
        return data

    def _parseURI(self, uri):
        result = urlparse.urlparse(uri)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        return database, hostname, username, password


class connectMySQL:
    pass


class Visualizer:
    def __init__(self, db, uri, rows=DEFAULT_MAXDATA, name=DEFAULT_NAME):
        # create template environment
        self.env = Environment(loader=PackageLoader('visualizer', 'templates'))

        self.name = name
        self.uri = uri
        self.rows = rows

        if db not in DB_OPTIONS:
            raise NameError('Database option {0} not supported. Use one of these: {1}'.
                            format(db, str(DB_OPTIONS)))
        # Connect database
        if db == '-psql':
            self.connector = connectPostgreSQL(self.uri)
        elif db == '-sqlite':
            self.connector = connectSQLite(self.uri)
        elif db == '-mysql':
            self.connector == connectMySQL(self.uri)

        self.tableNames = self._parseTables()
        self.tableContent = self._parseTableData()

    def _parseTables(self):
        tableNames = []
        data = self.connector.getTables()
        for tabledata in data:
            tableNames.append(str(tabledata[0]).decode('utf8'))
        return tableNames

    def _parseTableData(self):
        content = []
        for table in self.tableNames:
            data = {}
            data['name'] = table
            data['header'] = []
            data['rows'] = []
            desc, rows = self.connector.getTableData(table)
            for header in desc:
                headerdata = {}
                headerdata['name'] = str(header).decode('utf8')
                headerdata['primary'] = False
                headerdata['nullablbe'] = False
                # TODO many more attributes
                data['header'].append(headerdata)
            rowcounter = 0
            for row in rows:
                if rowcounter >= self.rows:
                    break
                rowcounter += 1
                rowdata = []
                for element in row:
                    rowdata.append(str(element).decode('utf8'))
                data['rows'].append(rowdata)
            content.append(data)
        return content

    def _makeObject(self):
        obj = {}
        obj['name'] = self.name
        obj['generated'] = datetime.datetime.now().isoformat()
        obj['content'] = self.tableContent
        return obj

    def jsonGenerator(self):
        obj = self._makeObject()
        prettyobject = json.dumps(obj, indent=4, separators=(',', ': '))
        f = codecs.open(JSON_OUT, 'w', 'utf-8')
        f.write(prettyobject)
        f.close()

    def htmlGenerator(self):
        obj = self._makeObject()
        template = self.env.get_template('visualizer.html')
        rendered = template.render(data=obj)
        output = codecs.open(HTML_OUT, 'w', 'utf-8')
        for line in rendered:
            output.write(line)
        # output.write(rendered.decode('utf8'))
        output.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise StandardError('Arguments invalid')
    # if '-n' in sys.argv:
    #     name = sys.argv[]
    vis = Visualizer(sys.argv[1], sys.argv[2])
    vis.jsonGenerator()
    vis.htmlGenerator()
    print "done."
