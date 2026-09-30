@echo off
python start2.py --arch seq --size 5 --clients 4 --port 5050 --out %CSV%
python start2.py --arch seq --size 50 --clients 4 --port 5050 --out %CSV%
python start2.py --arch seq --size 500 --clients 4 --port 5050 --out %CSV%

python start2.py --arch seq --size 5 --clients 20 --port 5050 --out %CSV%
python start2.py --arch seq --size 50 --clients 20 --port 5050 --out %CSV%
python start2.py --arch seq --size 500 --clients 20 --port 5050 --out %CSV%

python start2.py --arch seq --size 5 --clients 80 --port 5050 --out %CSV%
python start2.py --arch seq --size 50 --clients 80 --port 5050 --out %CSV%
python start2.py --arch seq --size 500 --clients 80 --port 5050 --out %CSV%

python start2.py --arch thread --size 5 --clients 4 --port 5050 --out %CSV%
python start2.py --arch thread --size 50 --clients 4 --port 5050 --out %CSV%
python start2.py --arch thread --size 500 --clients 4 --port 5050 --out %CSV%

python start2.py --arch thread --size 5 --clients 20 --port 5050 --out %CSV%
python start2.py --arch thread --size 50 --clients 20 --port 5050 --out %CSV%
python start2.py --arch thread --size 500 --clients 20 --port 5050 --out %CSV%
 
python start2.py --arch thread --size 5 --clients 80 --port 5050 --out %CSV%
python start2.py --arch thread --size 50 --clients 80 --port 5050 --out %CSV%
python start2.py --arch thread --size 500 --clients 80 --port 5050 --out %CSV%

python start2.py --arch pool --size 5 --clients 4 --port 5050 --out %CSV%
python start2.py --arch pool --size 50 --clients 4 --port 5050 --out %CSV%
python start2.py --arch pool --size 500 --clients 4 --port 5050 --out %CSV%

python start2.py --arch pool --size 5 --clients 20 --port 5050 --out %CSV%
python start2.py --arch pool --size 50 --clients 20 --port 5050 --out %CSV%
python start2.py --arch pool --size 500 --clients 20 --port 5050 --out %CSV%

python start2.py --arch pool --size 5 --clients 80 --port 5050 --out %CSV%
python start2.py --arch pool --size 50 --clients 80 --port 5050 --out %CSV%
python start2.py --arch pool --size 500 --clients 80 --port 5050 --out %CSV%