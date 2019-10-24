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
        message = tmp.split("\r\n")[0:-1]
        if len(message) == 0:
            raise Exception("empty")

        tmp = message[0].split(" ")
        self.method = tmp[0]
        self.url = urllib.parse.unquote(tmp[1])
        if self.url.endswith('/'):
            self.url = self.url[:-1]
        self.protocol = tmp[2]

        for header in message[1: ]:
            pos = header.find(":")
            key = header[:pos].strip().lower()
            value = header[pos + 1:].strip()
            self.header[key] = value

    def get_header(self, key):
        if key.lower() in self.header:
            return self.header[key]
        return None

