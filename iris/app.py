from .request import Request
from .response import Response
import asyncio
import os

class Iris():
    def __init__(self):
        self.layers = {}

    async def use(self, method, path, handler):
        self.layers.append(handler)
        if path is None:
            path = '*'
        if not method in self.layers:
            self.layers[method] = {}
        if not path in self.layers[method]:
            self.layers[method][path] = []
        self.layers[method][path].append(handler)

    async def handler(self, reader, writer):
        request = Request(reader)
        await request.init()

        response = Response(writer)



    def listen(self, addr="127.0.0.1", port="2333"):
        loop = asyncio.get_event_loop()
        coro = asyncio.start_server(self.handler, addr, port, )
        server = loop.run_until_complete(coro)
        # Serve requests until Ctrl+C is pressed
        print('Serving on {}'.format(server.sockets[0].getsockname()))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        # Close the server
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

def get(req, res):
    print(req, res)
    # path = req.url
    # print(path)
    # if os.path.exists(path):
    #     if os.path.isdir(path):
    #         body = [b'HTTP/1.0 200 OK\r\n', b'Content-Type:text/html; charset=utf-8\r\n',
    #                 b'Connection: close\r\n',
    #                 b'\r\n',
    #                 bytes('<html><head><title>Index of ' +
    #                         str(path) + '</title></head>', 'utf-8')
    #                 ]

    #         body = body + [
    #             b'<body bgcolor="white">',
    #             bytes('<h1>Index of ' + str(path) + '</h1><hr>', 'utf-8'),
    #             b'<pre>'
    #         ]
    #         print(os.listdir(path))
    #         for x in os.listdir(path):
    #             body.append(bytes('<a href=' + str(posixpath.split(path)
    #                                                 [-1]) + '/' + str(x) + '>' + str(x) + '</a><br>', 'utf-8'))

    #         body = body + [
    #             b'</pre>'
    #             b'<hr>'
    #             b'</body></html>\r\n',
    #             b'\r\n'
    #         ]

    #         writer.writelines(body)
    #     else:
    #         size = os.path.getsize(path)
    #         file = open(path, 'rb')
    #         writer.writelines([
    #             b'HTTP/1.0 200 OK\r\n',
    #             b'Content-Type:text/html; charset=utf-8\r\n',
    #             b'Connection: close\r\n',
    #             bytes('Content-Length: ' + str(size) + '\r\n', 'utf-8'),
    #             bytes('Content-Type: ' + guess_type(path) + '\r\n', 'utf-8'),
    #             b'\r\n'
    #         ])
    #         writer.write(file.read())

    # else:
    #     writer.writelines([
    #         b'HTTP/1.0 404 Not found\r\n',
    #         b'Content-Type:text/html; charset=utf-8\r\n',
    #         b'Connection: close\r\n',
    #         b'\r\n',
    #         b'<html><body>404 Not found<body></html>\r\n',
    #         b'\r\n'
    #     ])

if __name__ == "__main__":
    iris = Iris()

    iris.use('GET', '*', )
    iris.use('HEAD', '*', )

    iris.listen()
