from .constants import code

class response():
    def __init__(self, writer):
        self.__writer = writer

        self.header = {}
        self.body = ""

        self.code = 404

    def __writeline(self, str):
        self.__writer.writeline(bytes(str))

    def __writelines(self, strs):
        self.__writer.writelines([bytes(s) for s in strs])

    def __write_header(self):
        self.__writeline("HTTP/1.1 %d %s\r\n" % (self.code, code[self.code]))
        for k, v in self.headers.items():
            self.__writeline("%s: %s\r\n" % (k, v))
        self.__writeline("\r\n")

    def __write_body(self):
        pass

    def set_status(self, code):
        self.code = code

    def set_header(self, key, value):
        self.header[key] = value


    def html(self, body):
        self.set_status(200)
        self.set_header('Content-Type', 'text/html')
        self.body = body

    async def send(self):
        self.writer.__write_header()
        self.writer.__write_body()
        await self.writer.drain()
        self.writer.close()
