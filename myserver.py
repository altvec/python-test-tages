#!/usr/bin/env python
# -*- coding: utf-8 -*-

import aiohttp
import argparse

from aiohttp import web
from urllib.parse import urljoin


class Server:
    def __init__(self, target):
        self.target = target

    async def proxy(self, request):
        url = urljoin(self.target, request.match_info['path'])
        data = await request.read()
        query_params = request.rel_url.query

        peername = request.transport.get_extra_info('peername')
        if peername is not None:
            host, port = peername

        print(f'{host}:{port} :: {request.method} {url}')

        async with aiohttp.ClientSession() as session:
            async with session.request(
                request.method,
                url,
                data=data,
                params=query_params,
                headers=request.headers,
            ) as resp:
                response = resp
                raw = await response.read()

        return web.Response(
            body=raw,
            status=response.status,
            headers=dict(response.headers),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple HTTP proxy')
    parser.add_argument('--host', help='target host', required=True)
    args = parser.parse_args()

    app = web.Application()
    server = Server(args.host)
    app.add_routes([web.route('*', '/{path:.*?}', server.proxy)])

    web.run_app(app)
