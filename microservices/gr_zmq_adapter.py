#!/usr/bin/env python

# Copyright (c) 2019 Jeppe Ledet-Pedersen
# This software is released under the MIT license.
# See the LICENSE file for further details.

import os
import sys
import time
import json
import argparse

from gnuradio import gr
from gnuradio import blocks
from gnuradio import zeromq
import numpy as np

from redis import Redis

class fft_broadcast_sink(gr.sync_block):
    def __init__(self, fft_size, **kw):
        super().__init__(name="redis_sink",
                            in_sig=[(np.float32, fft_size)],
                            out_sig=[])

        redis_host = kw.get('redis_host', 'localhost')
        redis_port = kw.get('redis_port', 6379)
        self.redis_stream = kw.get('redis_stream', 'spectral')
        
        self.r = Redis(redis_host, redis_port, retry_on_timeout=True)

    def work(self, input_items, output_items):

        # input_items is a vector of "samples". Each sample is a vector of length fft_size
        ninput_items = len(input_items[0])

        for msg in input_items[0]:
            p = np.around(msg).astype(int)
#            p = np.fft.fftshift(p)
            # For reasonable performance, the Redis stream is a JSON-encoded list (a string). Otherwise,
            # serialization can be costly
            data = {"samples": json.dumps(p.tolist()) }

            # maxlen=100 says to only keep the last 100 messages. This prevents old data from streaming
            self.r.xadd(self.redis_stream, data, maxlen=100)

        self.consume(0, ninput_items)

        return 0


class top_block(gr.top_block):
    '''top_block(args,
                 pass_tags=False,
                 zmq_sub_filter='',
                 zmq_timeout_ms=100,
                 zmq_hwm=-1)
    '''
    def __init__(self, args, **kw):
        super().__init__("Top Block")

        # Create the sub_source block
        self.zmq_sub_source = zeromq.sub_source(
            args.data_size,
            args.fft_size,
            args.endpoint,
            kw.get('zmq_timeout_ms', 100),
            kw.get('pass_tags', False),
            kw.get('zmq_hwm', -1),
            kw.get('zmq_sub_filter', ''),
            )

        self.fft_broadcast = fft_broadcast_sink(args.fft_size,
                                                    redis_host=args.redis_host,
                                                    redis_port=args.redis_port,
                                                    redis_stream=args.redis_stream)

        self.connect((self.zmq_sub_source, 0), (self.fft_broadcast, 0))

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-s', '--sample-rate', type=float, default=200e6)
    parser.add_argument('-f', '--frequency', type=float, default=1600e6)
    parser.add_argument('--data-size', type=int, default=gr.sizeof_float,
                            help='size of one data point, in bytes')
#    parser.add_argument('-g', '--gain', type=float, default=40)
    parser.add_argument('-n', '--fft-size', type=int, default=4096)
    parser.add_argument('-r', '--frame-rate', type=int, default=25)
    parser.add_argument('--endpoint', default="tcp://127.0.0.1:5001")

    parser.add_argument('--redis-host', default=os.environ.get("REDIS_HOSTNAME", "localhost"))
    parser.add_argument('--redis-port', type=int, default=os.environ.get("REDIS_PORT", 6379))
    parser.add_argument('--redis-stream', default='spectral')

    args = parser.parse_args()

    tb = top_block(args)
    tb.start()

    while True:
        time.sleep(1)

    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
