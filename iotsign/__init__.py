import logging

from . import database, config, protocol

def initialize_logging(level):
    logging.basicConfig(
        format='%(asctime)-23s [%(levelname)s] %(name)s :: %(message)s',
        level=level,
    )

def main():
    args = config.get_args()
    print(args)
    initialize_logging(args.log_level)
    database.initialize(str(args.database.resolve()))
    database.Message.create(message="hello").save()

