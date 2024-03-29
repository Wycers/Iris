from .constants import code
import mimetypes
import posixpath
import os


def guess_type(path):
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream',  # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain'
    })
    base, ext = posixpath.splitext(path)
    if ext in extensions_map:
        return extensions_map[ext]
    ext = ext.lower()
    if ext in extensions_map:
        return extensions_map[ext]
    else:
        return extensions_map['']


class Response():
    def __init__(self, method, writer):
        self.__writer = writer

        self.method = method
        # response header dictionary
        self.headers = {}
        # response body (in bytes)
        self.body = b''

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
        self.__writer.writelines([self.body])

    def set_status(self, code):
        self.code = code

    def set_header(self, key, value):
        self.headers[key] = value

    def set_body(self, body):
        self.body = body

    def html(self, body):
        self.set_status(200)
        self.set_header('Content-Type', 'text/html;charset=utf-8')
        self.set_body(body.encode("utf-8"))

    async def send_file(self, path, start=None, end=None):
        size = os.path.getsize(path)
        file = open(path, 'rb')
        if start is None and end is None:
            print("Send file %s with size %d" % (path, size))
            self.set_header('Content-Type', guess_type(path))
            self.set_header('Content-Length', str(size))
            self.set_body(file.read())
        else:
            if start is None:
                start = 0
            if end is None:
                end = size - 1
            self.set_status(206)
            self.set_header('Accept-Ranges', 'bytes')
            self.set_header('Content-Range', 'bytes %d-%d/%d' % (start, end, size)),
            if start > end:
                raise Exception("Invalid range specified")
            else:
                file.seek(start)
                self.set_body(file.read(end-start+1))
        file.close()

    async def end(self):
        self.__write_header()
        if self.method == 'HEAD':
            pass
        else:
            self.__write_body()
        await self.__writer.drain()
        self.__writer.close()
