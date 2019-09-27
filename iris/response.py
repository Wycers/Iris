from .constants import code

class Response():
    def __init__(self, writer):
        self.__writer = writer

        self.headers = {}
        self.body = ""

        self.code = 404

    def __writeline(self, str):
        self.__writer.writelines([str.encode()])

    def __writelines(self, strs):
        self.__writer.writelines([s.encode() for s in strs])

    def __write_header(self):
        self.__writeline("HTTP/1.1 %d %s\r\n" % (self.code, code[self.code]))
        for k, v in self.headers.items():
            self.__writeline("%s: %s\r\n" % (k, v))
        self.__writeline("\r\n")

    def __write_body(self):
        self.__writeline("%s\r\n" % self.body)
        self.__writeline("\r\n")
        pass

    def set_status(self, code):
        self.code = code

    def set_header(self, key, value):
        self.headers[key] = value

    def set_body(self, body):
        self.body = body

    def html(self, body):
        self.set_status(200)
        self.set_header('Content-Type', 'text/html')
        self.body = body

    async def end(self):
        self.__write_header()
        self.__write_body()
        await self.__writer.drain()
        self.__writer.close()
