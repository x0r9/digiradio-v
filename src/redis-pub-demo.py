"""
Demo to start publishing data onto redis
"""

import argparse
import redis
import random
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser("redis-pub-demo - save KISS data into a redis cache")
    parser.add_argument("-ip", type=str, default="127.0.0.1", help="ip of kiss modem")
    parser.add_argument("-port", type=int, default=6379, help="port of kiss modem")
    args = parser.parse_args()

    r = redis.Redis(host=args.ip, port=args.port, db=0)

    pub_id = random.randint(1000,9999)
    pub_topic = "pubsub-test"
    counter = 0
    while True:
        counter += 1

        message = f"Client {pub_topic} - count: {counter:5d}"
        print(f"publish to {pub_topic} msg: {message}")
        r.publish(str(pub_topic), str(message))
        time.sleep(1)
