# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for schwab_market_data_pyspark.
#
# PySpark ships its own jars/ and python resource files that PyInstaller's
# static import analysis won't discover on its own — collect_data_files()
# and collect_submodules() pull those in explicitly. Without this, the EXE
# builds but fails at runtime with "Java gateway process exited" or missing
# resource errors.
#
# The resulting EXE still requires a separately installed JDK 17 (Temurin
# recommended) and, on Windows, winutils.exe/hadoop.dll on HADOOP_HOME —
# PyInstaller packages the Python side only, never the JVM.

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

pyspark_datas = collect_data_files('pyspark')
py4j_datas = collect_data_files('py4j')
pyspark_hidden = collect_submodules('pyspark')
py4j_hidden = collect_submodules('py4j')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=pyspark_datas + py4j_datas + [
        ('schwab_market_data_pyspark.ini.template', '.'),
        ('sql', 'sql'),
    ],
    hiddenimports=pyspark_hidden + py4j_hidden + [
        'core',
        'core.config',
        'core.logging_setup',
        'spark_session',
        'spark_session.session_factory',
        'db',
        'db.history_reader',
        'db.analytics_writer',
        'db._jdbc',
        'analytics',
        'analytics.window_specs',
        'analytics.moving_stats',
        'analytics.bollinger',
        'analytics.zscore',
        'cli',
        'cli.args',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='schwab_market_data_pyspark',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
