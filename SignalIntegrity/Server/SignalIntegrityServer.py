"""
SignalIntegrityServer.py - local HTTP/JSON server for the SignalIntegrity web and Tauri GUIs
"""
# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import argparse
import json
import os
import sys

def main(argv=None):
    parser=argparse.ArgumentParser(prog='SignalIntegrityServer',
        description='Serve the SignalIntegrity web GUI on 127.0.0.1 (used by the Tauri desktop app).')
    parser.add_argument('--port',type=int,default=0,help='port to listen on (default: any free port)')
    parser.add_argument('--browser',action='store_true',help='open the GUI in the default web browser')
    parser.add_argument('--verbose',action='store_true',help='log requests and server errors')
    parser.add_argument('project',nargs='?',help='project (.si) to open at start-up')
    args=parser.parse_args(argv)

    from SignalIntegrity.Server.HttpServer import SignalIntegrityServer
    # the token is taken from the environment, never the command line, so other users can't read it
    server=SignalIntegrityServer(args.port,os.environ.get('SIGNALINTEGRITY_SERVER_TOKEN'),verbose=args.verbose)
    if args.project:
        try:
            server.api.Dispatch('open',{'filename':os.path.realpath(args.project)})
        except Exception as e:
            sys.stderr.write('could not open '+args.project+': '+str(e)+'\n')
    # first stdout line is read by the Tauri shell to find the server
    sys.stdout.write(json.dumps({'signalintegrity_server':{'port':server.port,'token':server.token,'url':server.Url()}})+'\n')
    sys.stdout.flush()
    if args.browser:
        import webbrowser
        webbrowser.open(server.Url())
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
