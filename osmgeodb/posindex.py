#
# osmgeodb - GIS database for OpenStreetMap data
#
# Copyright (C) 2011-2019 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import asyncio
import logging
import operator
import time
import zmq
import zmq.asyncio

from collections import Counter
from sortedcontainers import SortedKeyList

from .mpack import m_pack
from .socket import recv_messages

logger = logging.getLogger(__name__)

FMT_STATS = 'nodes[m]: {0:,.3f} {1:.3f}/s, time[s]:' \
    ' decompression: {2[decompression]:.1f}' \
    ' block parse: {2[parse blocks]:.1f}' \
    ' group parse: {2[parse groups]:.1f}'.format

async def receive_pos_index(socket: zmq.Socket, pos_index: SortedKeyList):
    """
    Receive OSM position index item from ZMQ socket and update the index.

    :param socket: ZMQ socket.
    :param pos_index: OSM position index.
    """
    async for item in recv_messages(socket):
        pos_index.add(item)

async def send_pos_index(socket: zmq.Socket, queue: asyncio.Queue):
    while not socket.closed:
        item = await queue.get()
        if item is None:
            break

        await socket.send(m_pack(item))

def create_index_entry(type, file_pos, group):
    return type, file_pos, group.id[0]

def create_pos_index() -> SortedKeyList:
    """
    Create OSM position index.

    The new index is empty.
    """
    return SortedKeyList([], key=operator.itemgetter(2))

# vim: sw=4:et:ai
