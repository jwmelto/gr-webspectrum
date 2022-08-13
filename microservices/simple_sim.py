#!/usr/bin/env python

# Copyright (c) 2019 Jeppe Ledet-Pedersen
# This software is released under the MIT license.
# See the LICENSE file for further details.

import sys
import os
import time
import json
import argparse

from redis import Redis

class BaseAdapter:

    def __init__(self):
        #TODO redis params?
        self.redis_host = 'localhost'
        self.redis_port = 6379
        self.redis_stream = 'spectral'

    def send_samples(self, samples, stream=self.redis_stream, data={}):
        '''send_samples(samples, stream=default, data={})

        sends a message to Redis
          samples - a list of amplitude samples
          stream  - the name of the stream. This defaults to the configured stream,
                    but multiple streams can be fed by passing this parameter
          data    - the base implementation sends a simple dict,
                    { 'samples' : json.dumps(samples) }
                    other meta-data can be passed by pre-populating the dict with other values
        '''

sampleCount = 0
def generate_samples(fft_size):
    global sampleCount
    sampleCount += 4
    samples = [ ((x + sampleCount) % 100) - 200 for x in range(1, fft_size) ]
    return samples

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-s', '--sample-rate', type=float, default=200e6)
    parser.add_argument('-f', '--frequency', type=float, default=1600e6)
    parser.add_argument('-n', '--fft-size', type=int, default=4096)

    parser.add_argument('--redis-host', default=os.environ.get("REDIS_HOSTNAME", "localhost"))
    parser.add_argument('--redis-port', type=int, default=os.environ.get("REDIS_PORT", 6379))
    parser.add_argument('--redis-stream', default='spectral')

    args = parser.parse_args()

    r = Redis(args.redis_host, args.redis_port, retry_on_timeout=True)

    while True:
        time.sleep(0.1)                   #run 10Hz update rate
        data = {"samples": json.dumps(generate_samples(args.fft_size)) }

        # maxlen=100 says to only keep the last 100 messages. This prevents old data from streaming
        r.xadd(args.redis_stream, data, maxlen=100)


if __name__ == '__main__':
    main()
