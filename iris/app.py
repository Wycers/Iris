from .request import Request
from .response import Response
from pathlib import Path
import asyncio
import os
import urllib

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

        response = Response(request.method, writer)

        print(request.method)
        print(request.url)

        if not request.method in self.layers:
            response.set_status(405)
            response.html('<html><body><h1>405 Method Not Allowed</h1></body></html>')
        elif '*' in self.layers[request.method]:
            for handler in self.layers[request.method]['*']:
                await handler(request, response)
        elif not request.url in self.layers[request.method]:
            # 404 while handler not found
            response.set_status(404)
            response.html('<html><body><h1>404 Not found</h1></body></html>')
        else:
            for handler in self.layers[request.method][request.url]:
                await handler(request, response)
        await response.end()

    async def static_fn(self, req, res):
        path = Path("." + req.url)

        if path.exists():
            if path.is_dir():
                res.set_header('Set-Cookie', req.url + '/; path=/;')
                cookie = req.get_header('cookie')
                if cookie is not None:
                    if str(path) == '.' and cookie != '/':
                        res.set_status(302)
                        res.set_header('Location', cookie)
                        return
                res.set_status(200)
                body = ""

                body += '<a href=\"/%s\">.</a><br>' % str(path)
                if str(path) == '.':
                    pass
                else:
                    body += '<a href=\"/%s\">..</a><br>' % str(path.parents[0])

                for x in path.iterdir():
                    print(x.resolve())
                    body += '<a href=\"%s/%s\">%s</a><br>' % (req.url, urllib.parse.quote(x.name), x.name)
                res.html('''
                <html>
                    <head><title>%s</title></head>
                    <body>
                        <h1>Index of %s</h1>
                        <pre>%s</pre>
                    </body>
                </html>''' % (req.url, req.url, body))
            elif os.path.isfile(path):
                res.set_status(200)
                Range = req.get_header('range')
                start, end = None, None
                if Range is not None:
                    s, t = Range.strip('bytes=').split('-')
                    try:
                        start = int(s)
                    except ValueError:
                        start = None
                    try:
                        end = int(t)
                    except ValueError:
                        end = None
                await res.send_file(path, start, end)
        else:
            res.set_status(404)
            res.html('<html><body><h1>404 Not found</h1></body></html>')

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
