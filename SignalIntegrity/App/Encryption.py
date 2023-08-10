"""
Encryption.py
"""
# Copyright (c) 2018 Teledyne LeCroy, Inc.
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

class Encryption(object):
    """
    https://cryptobook.nakov.com/symmetric-key-ciphers/aes-encrypt-decrypt-examples

    while this is not added to the setup.py (the encryption feature is probably needed
    by only a few, in order to use it, you need to pip install:

    pycryptodome
    scrypt

    """
    password = None
    ending = '$'
    Save=None
    def __init__(self,pwd=None,ending=None):
        if pwd != None:
            Encryption.password = pwd
        if ending != None:
            if ending == '' or Encryption.ending in ['',None]:
                ending = '$'
            Encryption.ending = ending

    def __encrypt_AES_GCM(self,msg, password=None):
        from Crypto.Cipher import AES
        import scrypt
        if password == None: password=self.password.encode()
        kdfSalt = os.urandom(16)
        secretKey = scrypt.hash(password, kdfSalt, N=16384, r=8, p=1, buflen=32)
        aesCipher = AES.new(secretKey, AES.MODE_GCM)
        ciphertext, authTag = aesCipher.encrypt_and_digest(msg)
        return (kdfSalt, ciphertext, aesCipher.nonce, authTag)

    def __decrypt_AES_GCM(self,encryptedMsg, password=None):
        from Crypto.Cipher import AES
        import scrypt
        if password == None: password=self.password.encode()
        (kdfSalt, ciphertext, nonce, authTag) = encryptedMsg
        secretKey = scrypt.hash(password, kdfSalt, N=16384, r=8, p=1, buflen=32)
        aesCipher = AES.new(secretKey, AES.MODE_GCM, nonce)
        plaintext = aesCipher.decrypt_and_verify(ciphertext, authTag)
        return plaintext

    def Decrypt(self,text):
        import binascii
        kdfSalt=binascii.unhexlify(text[0:32])
        aesIV=binascii.unhexlify(text[32:64])
        authTag=binascii.unhexlify(text[64:96])
        ciphertext=binascii.unhexlify(text[96:])
        encryptedMsg=(kdfSalt, ciphertext, aesIV, authTag)
        plaintext=self.__decrypt_AES_GCM(encryptedMsg)
        return plaintext

    def Encrypt(self,text):
        import binascii
        (kdfSalt, ciphertext, aesIV, authTag)=self.__encrypt_AES_GCM(text, self.password)
        Encryption.Save=(kdfSalt, ciphertext, aesIV, authTag)
        kdfSaltText=binascii.hexlify(kdfSalt)
        ciphertextText=binascii.hexlify(ciphertext)
        aesIVText=binascii.hexlify(aesIV)
        authtagText=binascii.hexlify(authTag)
        return kdfSaltText+aesIVText+authtagText+ciphertextText

    def WriteEncryptedLines(self,filename,lines):
        textToWrite=''.join(lines)
        if self.password != None and os.path.splitext(filename)[0].endswith(self.ending):
            try:
                textToWrite=self.Encrypt(textToWrite.encode()).decode()
            except ModuleNotFoundError: # pragma: no cover
                raise IOError('file cannot be encrypted')
        with open(filename,'w') as f:
            f.write(textToWrite)
        return self

    def ReadEncryptedLines(self,filename,split=True):
        with open(filename,'r') as f:
            text=f.readlines()
        if len(text)==1:
            if self.password != None:
                try:
                    text=self.Decrypt(text[0].encode()).decode()
                    if split:
                        text=text.splitlines(True)
                except:
                    raise IOError('decryption failed')
            else:
                raise IOError('file is encrypted')
        return text

if __name__ == '__main__': # pragma: no cover
    pwd=Encryption(pwd='test',ending='$')
    lines=['This is a test\n','of the emergency broadcast system\n']
    pwd.WriteEncryptedLines('test$.txt',lines)
    print(pwd.ReadEncryptedLines('test$.txt'))