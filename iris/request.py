import asyncio
import urllib

class Request():
    def __init__(self, reader):
        self.reader = reader
        self.header = {}

    async def init(self):
        tmp = ""
        while True:
            data = await self.reader.readline()
            if data == b'\r\n':
                break
            if data == b'':
                break
            tmp = tmp + data.decode()
        print(tmp)
        message = tmp.split("\r\n")[0:-1]
        if len(message) == 0:
            raise Exception("empty")

        tmp = message[0].split(" ")
        self.method = tmp[0]
        self.url = urllib.parse.unquote(tmp[1])
        self.protocol = tmp[2]

        for header in message[1: -1]:
            pos = header.find(": ")
            key = header[:pos]
            value = header[pos + 1:]
            self.header[key] = value

