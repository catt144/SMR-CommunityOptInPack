# Receipt: sitting logs archived 2026-10-01

Copied byte-for-byte from `%APPDATA%\Surviving Mars Relaunched\logs\` (sources left in place; logs carry CRLF and are stored as-is). Sizes in bytes; sha256 of source and copy.

Not copied: 20260930-12.23.04 (already archived byte-identical at `docs/archive/elevator_rope_20260930/`, sha256 00a02233d2499f106c4a4d10cbaa1061429c8120207d85998a4bb22b90e72369); 20260929-12.03.53, 20260929-12.55.28, 20260928-22.57.28 (no such file in the logs folder).

- Mars.exe-20261001-00.06.49-6aba6e65.log
  - original: `%APPDATA%\Surviving Mars Relaunched\logs\Mars.exe-20261001-00.06.49-6aba6e65.log`
  - bytes: 61877
  - sha256 source: d8ac661e90c1436b027ae472b61ae29650cace76cb9fe3d91b343410e604f7c5
  - sha256 copy: d8ac661e90c1436b027ae472b61ae29650cace76cb9fe3d91b343410e604f7c5 (MATCH)
  - label: sitting B's B1
- Mars.exe-20261001-11.16.04-6aba6e65.log
  - original: `%APPDATA%\Surviving Mars Relaunched\logs\Mars.exe-20261001-11.16.04-6aba6e65.log`
  - bytes: 2513805
  - sha256 source: d6fc8484382283744e0191b88a7fc3ac340a9e5306f60d8a2dbd907cba41d19e
  - sha256 copy: d6fc8484382283744e0191b88a7fc3ac340a9e5306f60d8a2dbd907cba41d19e (MATCH)
  - label: batch D
- Mars.exe-20260930-21.43.16-6aba6e65.log
  - original: `%APPDATA%\Surviving Mars Relaunched\logs\Mars.exe-20260930-21.43.16-6aba6e65.log`
  - bytes: 35832
  - sha256 source: 1e20ad8dd413a9b74473d9816f0fcac3fd7ea52cf7987766936c33bd6175c57e
  - sha256 copy: 1e20ad8dd413a9b74473d9816f0fcac3fd7ea52cf7987766936c33bd6175c57e (MATCH)
  - label: sitting B, stopped
- Mars.exe-20260930-11.47.37-6aba6e65.log
  - original: `%APPDATA%\Surviving Mars Relaunched\logs\Mars.exe-20260930-11.47.37-6aba6e65.log`
  - bytes: 74632
  - sha256 source: ad7dc9ead84bdd6a3304b371d13fc8c2881b808864982e4febb9d390dff6d7af
  - sha256 copy: ad7dc9ead84bdd6a3304b371d13fc8c2881b808864982e4febb9d390dff6d7af (MATCH)
  - label: the depot's first placement
- Mars.exe-20260929-13.36.00-6aad2d75.log
  - original: `%APPDATA%\Surviving Mars Relaunched\logs\Mars.exe-20260929-13.36.00-6aad2d75.log`
  - bytes: 1592809
  - sha256 source: cbef673bc4f3c398f432346d40c76d291d3703b173330a0af0ff0c1a73a31272
  - sha256 copy: cbef673bc4f3c398f432346d40c76d291d3703b173330a0af0ff0c1a73a31272 (MATCH)
  - label: brief 10

Note (orchestrator, 2026-10-01): the hashes are of the on-disk CRLF bytes at archive time. `.gitattributes` (`* text=auto eol=lf`) stores these logs LF-normalised, as it does every archived log here, so a checkout's bytes and hashes differ from the figures above; the text is the same.
