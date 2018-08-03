#!/usr/bin/python2
from __future__ import print_function
from argparse import RawTextHelpFormatter
import argparse
import errno
import os
import socket

def isOpen(ip, port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.settimeout(1)
   try:
      s.connect((ip, int(port)))
      s.shutdown(1)
      return 1
   except Exception as e:
      if e.errno == errno.ECONNREFUSED:
          return -1
      return 0

def scan(l):
    connected = []
    failed = []
    closed = []

    for hostPort in l:
        host, port = hostPort.split(':')
        if '-' in port:
            start, stop = port.split('-')
            start = int(start)
            stop = int(stop)
            stop += 1
            for p in xrange(start, stop):
                if isOpen(host, p) == 1:
                    connected.append("{}:{}".format(host, p))
                elif isOpen(host, p) == -1:
                    closed.append("{}:{}".format(host, p))
                else:
                    failed.append("{}:{}".format(host, p))
        else:
            if isOpen(host, port) == 1:
                connected.append("{}:{}".format(host, port))
            elif isOpen(host, port) == -1:
                closed.append("{}:{}".format(host, port))
            else:
                failed.append("{}:{}".format(host, port))
    return connected, failed, closed

def readFile(f):
    l = []
    with open(f) as fp:
        for line in fp:
            line = line.strip()
            if ':' in line:
                host, port = line.split(':')
            elif ',' in line:
                host, port = line.split(',')
            elif ' ' in line:
                host, port = line.split(' ')
            l.append("{}:{}".format(host.strip(), port.strip()))
    return l

def getFileNames(f):
    if '/' in f:
        basedir = os.path.dirname(f)
    else:
        basedir = '.'
    basename = os.path.basename(f)
    fileWithoutExtension, extension = os.path.splitext(basename)

    successFile = "{}/{}_SUCCESS{}".format(basedir, fileWithoutExtension, extension)
    failFile = "{}/{}_FAIL{}".format(basedir, fileWithoutExtension, extension)
    closeFile = "{}/{}_CLOSED{}".format(basedir, fileWithoutExtension, extension)
    return successFile, failFile, closeFile

def cleanup(successFile, failFile, closeFile):
    if os.path.isfile(successFile):
        os.remove(successFile)
    if os.path.isfile(failFile):
        os.remove(failFile)
    if os.path.isfile(closeFile):
        os.remove(closeFile)

def writeResults(f, connected, failed, closed):
    successFile, failFile, closeFile = getFileNames(f)
    cleanup(successFile, failFile, closeFile)

    if len(connected) > 0:
        with open(successFile, 'a') as fs:
            for c in connected:
                print(c, file=fs)

    if len(failed) > 0:
        with open(failFile, 'a') as ff:
            for fail in failed:
                print(fail, file=ff)

    if len(closed) > 0:
        with open(closeFile, 'a') as fc:
            for close in closed:
                print(close, file=fc)

def printResults(connected, failed, closed):
    for c in connected:
        print("Connected:        {}".format(c))
    for close in closed:
        print("Not Listening:    {}".format(close))
    for fail in failed:
        print("Failed:           {}".format(fail))

def runList(l):
    connected, failed, closed = scan(l)
    printResults(connected, failed, closed)

def runFile(f):
    connected, failed, closed = scan(readFile(f))
    printResults(connected, failed, closed)
    writeResults(f, connected, failed, closed)

def main():
    desc_str = 'Checks connectivity to endpoints'
    file_str = '''
file where each line is host port or host portRange.
delimited by a space, comma, or colon.
portRange delimited by a dash, no spaces.
e.g.
"host port",
"host:port",
"host,port",
"host, port"
e.g.
"host 3000-3005"
"host:3000-3005"
"host,3000-3005"
"host, 3000-3005"

'''
    host_str = '''
host port or host portRange.
delimited by a space or comma.
portRange delimited by a dash, no spaces.
e.g.
"host port",
"host:port"'
e.g.
"host 3000-3005"
"host:3000-3005"

'''
    hosts_str = '''
list of host:port or host:portRange
delimited by a space
e.g.
"host1:port1 host2:port2 ..."
"host1:port1 host2:3000-3005 ..."

'''

    parser = argparse.ArgumentParser(add_help=False,
                                     description=desc_str,
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('-f', '--file', help=file_str)
    parser.add_argument('-h', '--host', help=host_str, nargs='+')
    parser.add_argument('-H', '--hosts', help=hosts_str, nargs='+')
    args = parser.parse_args()

    if args.file:
        runFile(args.file)
    elif args.host:
        if len(args.host) == 1:
             runList(args.host)
        elif len(args.host) == 2:
             runList( [ "{}:{}".format(args.host[0], args.host[1]) ] )
        else:
            parser.print_help()
    elif args.hosts:
        runList(args.hosts)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
