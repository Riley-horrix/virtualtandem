from typing import TextIO

from src.lib.configuration import Configurable, Configuration
from src.message import Consumer, MessageHub
from src.messages import MessageId, Message, all_message_ids, TerminateRequest, StartRequest, message_fields_from_id, \
    message_name_from_id, InitialiseRequest
from src.service import Service


class CSVLogger(Consumer, Configurable, Service):
    def __init__(self, hub: MessageHub):
        Consumer.__init__(self, hub)
        Service.__init__(self)
        Configurable.__init__(self, "CSVLogger")

        self.log_file: str = ""
        self.requested_ids: list[MessageId] = []
        self.message_dict: dict[str, str | None] = {}

        self.csv_file: TextIO | None = None
        self.started = False

    def initialise(self, conf: Configuration = None):
        print("[CSVLogger]: Initialising")
        Configurable.initialise(self, conf)
        self.log_file = self.get_conf_str("log_file")
        self.requested_ids = list(self.get_conf_list("message_ids"))
        self.message_dict = self.generate_from_ids(self.requested_ids)

    def send(self, message: Message):
        if isinstance(message, StartRequest):
            self.start()
        if isinstance(message, TerminateRequest):
            self.stop()
        if isinstance(message, InitialiseRequest):
            self.initialise()
        if self.started and message.uid.value in self.requested_ids:
            self.handle_message(message)

    def handle_message(self, message: Message) -> None:
        name = message_name_from_id(message.uid.value)
        message_values = message.get_fields()
        for field in message_values.keys():
            field_name = f"{name}_{field}"
            if self.message_dict[field_name] is not None:
                self.emit_csv()
            self.message_dict[field_name] = message_values[field]

    def emit_csv(self):
        csv_line = ','.join([elem if elem else "" for elem in self.message_dict.values()]) + '\n'
        for key in self.message_dict.keys():
            self.message_dict[key] = None
        self.csv_file.write(csv_line)
        self.csv_file.flush()

    @staticmethod
    def generate_from_ids(message_ids) -> dict[str, int | float | None]:
        value_dict: dict[str, int | float | None] = {}
        for message_id in message_ids:
            name = message_name_from_id(message_id)
            str_fields = message_fields_from_id(message_id)
            for field in str_fields:
                field_name = f"{name}_{field}"
                value_dict[field_name] = None
        return value_dict

    def get_consumed(self) -> list[MessageId]:
        # Consume every message on the bus
        return all_message_ids

    def start(self):
        print("[CSVLogger]: Started")
        self.csv_file = open(self.log_file, "w")
        if not self.csv_file:
            raise Exception("[CSVLogger]: Failed to open csv logging file.")

        # Write the csv header
        csv_header = ','.join(self.message_dict.keys()) + '\n'

        self.csv_file.write(csv_header)
        self.csv_file.flush()
        self.started = True

    def stop(self):
        self.started = False
        self.csv_file.flush()
        self.csv_file.close()
