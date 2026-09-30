@echo off
setlocal

python -u p2p.py 1 file_5MB.torrent  5  3 %CSV%
python -u p2p.py 20 file_5MB.torrent  5  3 %CSV%
python -u p2p.py 80 file_5MB.torrent  5  3 %CSV%

REM 50 MB
python -u p2p.py 1 file_50MB.torrent  50  3 %CSV%
python -u p2p.py 20 file_50MB.torrent  50  3 %CSV%
python -u p2p.py 80 file_50MB.torrent  50  3 %CSV%

REM 500 MB
python -u p2p.py 1 file_500MB.torrent 500 3 %CSV%
python -u p2p.py 20 file_500MB.torrent 500 3 %CSV%
python -u p2p.py 80 file_500MB.torrent 500 3 %CSV%

endlocal