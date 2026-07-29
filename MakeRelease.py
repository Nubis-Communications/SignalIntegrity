"""
MakeRelease.py
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

import os
import sys
import shutil
import zipfile
import ssl
import tempfile


def _make_ca_bundle():
    """Build a CA bundle that includes the certificates from the operating
    system trust store in addition to certifi's bundle.

    On corporate networks the outbound TLS connection is often intercepted by
    a proxy (e.g. Zscaler) that presents a certificate signed by a private
    root CA.  That root CA is installed in the OS trust store but NOT in the
    ``certifi`` bundle that ``requests``/``twine`` use, so uploads fail with
    ``CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate``.

    Returns the path to a merged PEM bundle, or ``None`` if it could not be
    created (in which case the default certifi bundle is used).
    """
    if not hasattr(ssl, 'enum_certificates'):
        # enum_certificates is only available on Windows.
        return None
    try:
        import certifi
        data = open(certifi.where(), 'rb').read()
    except Exception:
        data = b''
    extra = b''
    for store in ('ROOT', 'CA'):
        try:
            for cert_bytes, encoding, _trust in ssl.enum_certificates(store):
                if encoding == 'x509_asn':
                    extra += ssl.DER_cert_to_PEM_cert(cert_bytes).encode()
        except Exception:
            pass
    if not extra:
        return None
    bundle_path = os.path.join(tempfile.gettempdir(),
                               'signalintegrity_ca_bundle.pem')
    with open(bundle_path, 'wb') as f:
        f.write(data + b'\n' + extra)
    return bundle_path


# Make requests/twine (and pip) trust the OS certificate store so uploads work
# from behind a TLS-intercepting corporate proxy.
_caBundle = _make_ca_bundle()
if _caBundle:
    os.environ['REQUESTS_CA_BUNDLE'] = _caBundle
    os.environ['SSL_CERT_FILE'] = _caBundle

root=os.path.dirname(os.path.realpath(__file__))
fileList=[os.path.join(path, name).replace('\\','/') for path, subdirs, files in os.walk(root) for name in files]
filteredFileList=[]
for fullFileName in fileList:
    filenameWithExtension=os.path.basename(fullFileName).replace('\\','/')
    filename,fileextension = os.path.splitext(filenameWithExtension)
    relpath=os.path.relpath(fullFileName, root).replace('\\','/')
    if relpath == filenameWithExtension: # this is a file in the root directory
        if fileextension != '.py': # not a python file
            if filenameWithExtension not in ['LICENSE.txt','README.md']:
                continue
    if filename[0]=='.': # hidden directory
        continue
    if relpath.startswith('.'):
        continue
    if fileextension == '.pyc':
        continue
    if '_pycache_' in fullFileName:
        continue
    if fileextension == '.p':
        continue
    if relpath.startswith('SignalIntegrity.egg-info/'):
        continue
    if relpath.startswith('build/'):
        continue
    if relpath.startswith('dist/'):
        continue
    if filenameWithExtension in ['LinkDoc.sh',
                                 'LinkHelp.sh',
                                 'UnlinkDoc.sh',
                                 'UnlinkHelp.sh']:
        continue
    if relpath.startswith('Doc/'):
        if filenameWithExtension != 'README.md':
            continue
    if relpath.startswith('Test/'):
        continue
    if relpath.startswith('SignalIntegrity/App/Help'):
        continue
    if relpath.startswith('SignalIntegrity/App/Examples/PowerIntegrity'):
        continue
    filteredFileList.append(fullFileName)
from SignalIntegrity.__about__ import __version__
destFileList=[os.path.abspath(os.path.join('../SignalIntegrity-'+__version__+'/',
                                           os.path.relpath(fullFileName,root)))
                                           for fullFileName in filteredFileList]
try:
    shutil.rmtree(os.path.abspath('../SignalIntegrity-'+__version__))
except (NotADirectoryError,FileNotFoundError):
    pass
try:
    os.remove(os.path.abspath('../SignalIntegrity-'+__version__+'.zip'))
except FileNotFoundError:
    pass
for input,output in zip(filteredFileList,destFileList):
    if not os.path.isdir(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output),exist_ok=True)
    shutil.copyfile(input,output)
zipf = zipfile.ZipFile(os.path.abspath(os.path.join(root,'../SignalIntegrity-'+__version__+'.zip')), 'w', zipfile.ZIP_DEFLATED)
for input,output in zip(filteredFileList,destFileList):
    zipf.write(output,os.path.join('SignalIntegrity-'+__version__,os.path.relpath(input, root)))
zipf.close()
os.chdir(os.path.abspath(os.path.join(root,'../SignalIntegrity-'+__version__)))
# use the same interpreter that is running this script (on Windows 'python3'
# often resolves to the Microsoft Store alias stub, which is not a real interpreter)
result = os.system('"'+sys.executable+'" setup.py bdist_wheel')
if result != 0:
    sys.exit('wheel build failed (exit code '+str(result)+') - aborting before upload')

#### comment in the upload block below to upload
import glob
import getpass
import subprocess

# Collect the built artifacts explicitly. cmd.exe (used by os.system on Windows)
# does NOT expand the 'dist/*' wildcard, so we expand it here in Python.
distFiles = glob.glob(os.path.join('dist', '*'))
if not distFiles:
    sys.exit('nothing to upload - no files found in dist/')

# Modern PyPI rejects wheels whose filename / .dist-info directory are not
# normalized (lower-cased) - e.g. it wants 'signalintegrity-...whl', not
# 'SignalIntegrity-...whl'.  Older setuptools (< 69) produced the un-normalized
# name, so fail fast with a helpful message instead of a confusing 400 error.
for _f in distFiles:
    if _f.endswith('.whl') and os.path.basename(_f).startswith('SignalIntegrity'):
        sys.exit("built wheel '"+os.path.basename(_f)+"' is not normalized; "
                 "PyPI requires a lower-cased 'signalintegrity-...whl'. "
                 "Upgrade the build tooling with:\n    \""+sys.executable+
                 "\" -m pip install -U \"setuptools>=69\" wheel\n"
                 "then delete the dist/ folder and re-run this script.")

# PyPI only accepts token authentication. The username is always "__token__"
# and the password is your API token (the string that starts with "pypi-").
# Provide it via the TWINE_PASSWORD environment variable, otherwise you will be
# prompted for it here (input is hidden).
token = os.environ.get('TWINE_PASSWORD')
if not token:
    print('Enter your PyPI API token (starts with "pypi-"). '
          'It will not be echoed.')
    token = getpass.getpass('API token: ')

uploadEnv = dict(os.environ)
uploadEnv['TWINE_USERNAME'] = '__token__'
#uploadEnv['TWINE_PASSWORD'] = # put key here, begins with pypi- (or set the TWINE_PASSWORD environment variable before running this script)

# Non-interactive so it fails fast with a clear error instead of hanging.
uploadEnv['TWINE_NON_INTERACTIVE'] = '1'

# comment this in if you actually want to upload
#
# result = subprocess.call(
#     [sys.executable, '-m', 'twine', 'upload','--verbose'] + distFiles,
#     env=uploadEnv)
# if result != 0:
#     sys.exit('twine upload failed (exit code '+str(result)+')')

#### below is for testing, but I don't think this really works anymore -- I'm not sure
# result = subprocess.call(
#     [sys.executable, '-m', 'twine', 'upload',
#      '--repository-url', 'https://test.pypi.org/legacy/'] + distFiles,
#     env=uploadEnv)
pass




