import logging
import time
import argparse
import json
import emoji

from steem import Steem

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig()


class TxListener:

    def __init__(self, steemd_instance, config):
        self.s = steemd_instance
        self.config = config
        self.account = config.get("account")
        self.userlist_file = config.get("userlist_file")
        self.message = config.get("message")

    def get_last_block_height(self):
        try:
            props = self.s.get_dynamic_global_properties()
            return props['head_block_number']
        except Exception as e:
            return self.get_last_block_height()

    def already_thanked(self, username):
        with open(self.userlist_file, 'r') as f:
            for line in f.readlines():
                if username in line:
                    return True
        return False

    def add_to_list(self, username):
        with open(self.userlist_file, 'a+') as f:
            f.write("%s\n" % username)

    def handle_operation(self, op_type, op_value):
        if op_type != "account_witness_vote":
            return

        if op_value.get("witness") != self.account or not op_value.get("approve"):
            return

        if self.already_thanked(op_value["account"]):
            return

        self.send_memo(op_value["account"], self.config.get("memo"))

    def send_memo(self, to, message):
        try:
            self.s.commit.transfer(
                to,
                0.001,
                "SBD",
                memo=emoji.emojize(message),
                account=self.account
            )
            logger.info("Sent a hug to %s", to)
            self.add_to_list(to)
        except Exception as error:
            logger.error(error)

    def parse_block(self, block_id):
        logger.info("Parsing %s", block_id)

        # get all operations in the related block id
        operation_data = self.s.get_ops_in_block(
            block_id, virtual_only=False)

        for operation in operation_data:
            self.handle_operation(*operation['op'][0:2])

    def listen_blocks(self, starting_point=None):
        if not starting_point:
            starting_point = self.get_last_block_height()
        while True:
            while (self.get_last_block_height() - starting_point) > 0:
                starting_point += 1
                self.parse_block(starting_point)

            logger.info("Sleeping for 3 seconds...")
            time.sleep(3)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Config file in JSON format")
    args = parser.parse_args()
    config = json.loads(open(args.config).read())

    steemd_instance = Steem(
        nodes=config.get("nodes"),
        keys=config.get("keys"),
    )

    tx_listener = TxListener(
        steemd_instance=steemd_instance,
        config=config
    )

    tx_listener.listen_blocks()


if __name__ == '__main__':
    main()
