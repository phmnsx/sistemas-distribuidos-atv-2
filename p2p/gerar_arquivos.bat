fsutil file createnew file_5MB.bin 5242880

python -m py3createtorrent --force -t http://127.0.0.1:6969/announce -o file_5MB.torrent   file_5MB.bin

fsutil file createnew file_50MB.bin 52428800

python -m py3createtorrent --force -t http://127.0.0.1:6969/announce -o file_50MB.torrent  file_50MB.bin

fsutil file createnew file_500MB.bin 524288000

python -m py3createtorrent --force -t http://127.0.0.1:6969/announce -o file_500MB.torrent file_500MB.bin