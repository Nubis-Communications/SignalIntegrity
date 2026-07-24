# Encryption {#sec:Encryption}

Sometimes, it becomes necessary to transact SignalIntegrity projects hiding the internal features. This is best accomplished by encrypting the project files, usually all project files in a hierarchy. Encryption is achieved by specifying an ending for the file, along with a password. These are specified in the [Preferences](15-Main-Schematic-Dialog.md#Control-Help:Preferences), specifically the preferences [Encryption.Password](29-Preferences.md#sub:Encryption.Password) and [Encryption.Ending](29-Preferences.md#sub:Encryption.Ending).

Since file encryption is not a common need, the necessary packages are not automatically installed. These must be installed by hand (i.e. pip installed):

- pycryptodome

- scrypt

Any files subsequently saved whose name ends in the ending specified (see [Encryption.Ending](29-Preferences.md#sub:Encryption.Ending)) are AES encrypted using the password supplied (see [Encryption.Password](29-Preferences.md#sub:Encryption.Password)) in the [Standard Preferences](29-Preferences.md#sub:Standard-Preferences).

Any files subsequently read that are encrypted, are decrypted using the password supplied in the preferences.

For more information, see: <https://cryptobook.nakov.com/symmetric-key-ciphers/aes-encrypt-decrypt-examples>
