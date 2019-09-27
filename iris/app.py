from .request import Request
from .response import Response
import asyncio
import os
import posixpath

class Iris():
    def __init__(self):
        self.layers = {}

    def use(self, method, path, handler):
        print(method, path)
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

        print(request.method)
        print(request.url)

        if not request.method in self.layers:
            response.set_status(405)
            response.set_header('Content-Type', 'text/html; charset=utf-8')
            response.set_header('Connection', 'close')
            response.set_body('<html><body><h1>405 Method Not Allowed</h1></body></html>')
        if '*' in self.layers[request.method]:
            for handler in self.layers[request.method]['*']:
                await handler(request, response)
        elif not request.url in self.layers[request.method]:
            # 404 while handler not found
            response.set_status(404)
            response.set_header('Content-Type', 'text/html; charset=utf-8')
            response.set_header('Connection', 'close')
            response.set_body('<html><body><h1>404 Not found</h1></body></html>')
        else:
            for handler in self.layers[request.method][request.url]:
                await handler(request, response)
        await response.end()

    async def static_fn(self, req, res):
        path = "." + req.url

        if not os.path.exists(path):
            res.set_status(404)
            res.set_header('Content-Type', 'text/html; charset=utf-8')
            res.set_header('Connection', 'close')
            res.set_body('<html><body><h1>404 Not found</h1></body></html>')
        if os.path.isdir(path):
            res.set_status(200)
            res.set_header('Content-Type', 'text/html; charset=utf-8')
            res.set_header('Connection', 'close')

            print(os.listdir(path))
            body = ""
            for x in os.listdir(path):
                body += '<a href=%s/%s>%s</a><br>' % (posixpath.split(path)[-1], x, x)
            res.set_body('''
            <html>
                <head><title>%s</title></head>
                <body>
                    <h1>Index of %s</h1>
                    <pre>%s</pre>
                </body>
            </html>''' % (str(path), str(path), body))
        else:
            res.send_file(path)

    def static(self, path):
        self.use('GET', '*', self.static_fn)
        self.use('HEAD', '*', self.static_fn)

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


if __name__ == "__main__":
    iris = Iris()

    iris.use('GET', '*', static)
    iris.use('HEAD', '*', static)

    iris.listen()
