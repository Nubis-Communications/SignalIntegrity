# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['cli.py'],
             pathex=['C:\\Users\\pete_\\Documents\\SignalIntegrity'],
             binaries=[],
             datas=[('SignalIntegrity/App/icons/png/*', 'SignalIntegrity/App/icons/png'), ('SignalIntegrity/App/icons/png/16x16/*', 'SignalIntegrity/App/icons/png/16x16'), ('SignalIntegrity/App/icons/png/16x16/actions/*', 'SignalIntegrity/App/icons/png/16x16/actions')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='cli',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
