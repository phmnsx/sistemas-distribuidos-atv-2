mkdir seed
copy file_50MB.bin seed\

aria2c ^
  --enable-dht=false ^
  --bt-enable-lpd=true ^
  --listen-port=6881 ^
  --dir=seed ^
  --torrent-file=file_5MB.torrent ^
  --seed-time=600 ^
  --check-integrity=true ^
  --bt-seed-unverified=true ^
  --console-log-level=info