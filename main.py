import logging
import json
from quixstreams import Application
from pprint import pformat
from requests_sse import EventSource

def handle_stats(stats_msg):
    stats = json.loads(stats_msg)
    logging.info("STATS: %s", pformat(stats))

def main():
    logging.info("START")

    app = Application(
        broker_address="localhost:19092",
        loglevel="DEBUG",
        producer_extra_config={
            "statistics.interval.ms": 3*1000,
            "stats_cb": handle_stats,
            "debug": "msg",
            "linger.ms": 500,
            "batch.size": 1024 * 1024,
            "compression.type": "gzip",
        },
    )

    with (
        app.get_producer() as producer,
        EventSource("http://github-firehose.libraries.io/events",timeout=30) as event_source
    ):
        for event in event_source:
            value = json.loads(event.data)
            key  = value['id']
            logging.debug("Got: %s", pformat(value))

            producer.produce(
                topic="github_events",
                key=key,
                value=json.dumps(value),
            )
            producer.flush()

if __name__ == "__main__":
    try:
        logging.basicConfig(level="INFO")
        main()
    except Exception as e:
        raise Exception(f"Error: {e}")
