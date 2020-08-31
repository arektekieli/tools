import socket
import struct

BUFFER_LEN = 2**16

MAGIC_BYTES = "\xaa\x55"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.0.22', 5005))

# Get new records amount
query = "\x55\xaa\x01\xb4\x06\x00\x00\x00\x00\x00\xff\xff\x00\x00\x05\x00"
s.sendall(query)
data = s.recv(BUFFER_LEN)
print("Received", data.encode("hex"))

# Check if starts with magic bytes
if data.startswith(MAGIC_BYTES) == False:
    exit("No magic bytes magic bytes at begining")

# Amount starts at offset 4. I assume it is little endian uint_32
amount = struct.unpack("<I", data[4:8])[0]

if amount == 0:
    exit("There are no records.")

raw_amount = struct.pack("<I", amount)
raw_length = struct.pack("<H", amount * 0xC)

# Get records
query = "\x55\xaa\x01\xa1\x00\x00\x00\x00{}{}\x01\x00".format(raw_amount, raw_length)
s.sendall(query)
records_data = s.recv(BUFFER_LEN)
print("Received", records_data.encode("hex"))

# Check if starts with magic bytes
if data.startswith(MAGIC_BYTES) == False:
    exit("No magic bytes magic bytes at begining")

# Check expected len.
expected = (0xC * amount) + 0xC + 4
if len(records_data) != expected:
    exit("Data length if different than expected length.")

# Send information to device that we received records so it will remove them from new records
query = "\x55\xaa\x01\xa2\x02\x00\x00\x00\x00\x00\xff\xff\x00\x00\x0c\x00"
s.sendall(query)
data = s.recv(BUFFER_LEN)
print("Received", data.encode("hex"))

# Check if starts with magic bytes
if data.startswith(MAGIC_BYTES) == False:
    exit("No magic bytes magic bytes at begining")

s.close()

records = []

# Parse records
for i in range(amount):
    d = records_data[0xC + (i * 0xC) : 0x18 + (i * 0xC)]
    _id = struct.unpack("<I", d[0:4])[0]
    seconds = struct.unpack("<B", d[7:8])[0]
    unknown = d[4:].encode("hex")
    records.append({"id": _id, "data": unknown, "seconds": seconds})

print(records)

#[
#	{'seconds': 15, 'data': '0101010fe1813f6d', 'id': 123456788}, 
#	{'seconds': 19, 'data': '01011413e1813f6d', 'id': 3}
#]



