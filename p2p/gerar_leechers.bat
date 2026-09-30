for /L %%i in (1,1,4) do (
    mkdir leech_%%i 2>nul
    start "leech %%i" /B aria2c ^
  --enable-dht=false ^
  --bt-enable-lpd=true ^
  --listen-port=6901 ^
  --dir=leech_1 ^
  --torrent-file=file_5MB.torrent ^
  --seed-time=600 ^
  --console-log-level=info
)