#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#


import aiohttp
import asyncio
import async_timeout
from aiohttp import ClientResponseError

from gremlin_python.driver.transport import AbstractBaseTransport

__author__ = 'Lyndon Bauto (lyndonb@bitquilltech.com)'


class AiohttpTransport(AbstractBaseTransport):
    nest_asyncio_applied = False

    # Default heartbeat of 5.0 seconds.
    def __init__(self, call_from_event_loop=None, read_timeout=None, write_timeout=None, **kwargs):
        if call_from_event_loop is not None and call_from_event_loop and not AiohttpTransport.nest_asyncio_applied:
            """ 
                The AiohttpTransport implementation uses the asyncio event loop. Because of this, it cannot be called within an
                event loop without nest_asyncio. If the code is ever refactored so that it can be called within an event loop
                this import and call can be removed. Without this, applications which use the event loop to call gremlin-python
                (such as Jupyter) will not work.
            """
            import nest_asyncio
            nest_asyncio.apply()
            AiohttpTransport.nest_asyncio_applied = True

        # Start event loop and initialize websocket and client to None
        self._loop = asyncio.new_event_loop()
        self._websocket = None
        self._client_session = None

        # Set all inner variables to parameters passed in.
        self._aiohttp_kwargs = kwargs
        self._write_timeout = write_timeout
        self._read_timeout = read_timeout
        if "max_content_length" in self._aiohttp_kwargs:
            self._aiohttp_kwargs["max_msg_size"] = self._aiohttp_kwargs.pop("max_content_length")
        if "ssl_options" in self._aiohttp_kwargs:
            self._aiohttp_kwargs["ssl"] = self._aiohttp_kwargs.pop("ssl_options")

    def connect(self, url, headers=None):
        # Inner function to perform async connect.
        async def async_connect():
            # Start client session and use it to create a websocket with all the connection options provided.
            self._client_session = aiohttp.ClientSession(loop=self._loop)
            try:
                self._websocket = await self._client_session.ws_connect(url, **self._aiohttp_kwargs, headers=headers)
            except ClientResponseError as err:
                # If 403, just send forbidden because in some cases this prints out a huge verbose message
                # that includes credentials.
                if err.status == 403:
                    raise Exception('Failed to connect to server: HTTP Error code 403 - Forbidden.')
                else:
                    raise

        # Execute the async connect synchronously.
        self._loop.run_until_complete(async_connect())

    def write(self, message):
        # Inner function to perform async write.
        async def async_write():
            async with async_timeout.timeout(self._write_timeout):
                await self._websocket.send_bytes(message)

        # Execute the async write synchronously.
        self._loop.run_until_complete(async_write())

    def read(self):
        # Inner function to perform async read.
        async def async_read():
            async with async_timeout.timeout(self._read_timeout):
                return await self._websocket.receive()

        # Execute the async read synchronously.
        msg = self._loop.run_until_complete(async_read())

        # Need to handle multiple potential message types.
        if msg.type == aiohttp.WSMsgType.close:
            # Server is closing connection, shutdown and throw exception.
            self.close()
            raise RuntimeError("Connection was closed by server.")
        elif msg.type == aiohttp.WSMsgType.closed:
            # Should not be possible since our loop and socket would be closed.
            raise RuntimeError("Connection was already closed.")
        elif msg.type == aiohttp.WSMsgType.error:
            # Error on connection, try to convert message to a string in error.
            raise RuntimeError("Received error on read: '" + str(msg.data) + "'")
        elif msg.type == aiohttp.WSMsgType.text:
            # Convert message to bytes.
            data = msg.data.strip().encode('utf-8')
        else:
            # General handle, return byte data.
            data = msg.data
        return data

    def close(self):
        # Inner function to perform async close.
        async def async_close():
            if not self._websocket.closed:
                await self._websocket.close()
            if not self._client_session.closed:
                await self._client_session.close()

        # If the loop is not closed (connection hasn't already been closed)
        if not self._loop.is_closed():
            # Execute the async close synchronously.
            self._loop.run_until_complete(async_close())

            # Close the event loop.
            self._loop.close()

    @property
    def closed(self):
        # Connection is closed if either the websocket or the client session is closed.
        return self._websocket.closed or self._client_session.closed
