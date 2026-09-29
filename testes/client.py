import socket, sys, time

host = sys.argv[1]
size = int(sys.argv[2])
port = int(sys.argv[3]) if len(sys.argv) > 3 else 5000

s = socket.create_connection((host, port))
start = time.perf_counter()

received = 0
while received < size:
    data = s.recv(1024 * 1024)
    if not data:
        break
    received += len(data)

elapsed = time.perf_counter() - start
s.close()
print(elapsed)