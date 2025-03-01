from src.lib.configuration import Configurable, Configuration
from src.message import Consumer, MessageHub
from src.messages import MessageId, Message, all_message_ids, TerminateRequest, StartRequest, message_fields_from_id, \
    message_name_from_id
from src.service import Service


class CSVLogger(Consumer, Configurable, Service):
    def __init__(self, hub: MessageHub):
        Consumer.__init__(self, hub)
        Service.__init__(self)
        Configurable.__init__(self, "CSVLogger")

        self.log_file: str = ""
        self.requested_ids: list[MessageId] = []
        self.message_dict: dict[str, str | None] = {}

    def initialise(self, conf: Configuration = None):
        self.log_file = self.get_conf_str("log_file")
        self.requested_ids = list(self.get_conf_list("message_ids"))
        self.message_dict = self.generate_from_ids(self.requested_ids)

    def send(self, message: Message):
        if isinstance(message, StartRequest):
            self.start()
        if isinstance(message, TerminateRequest):
            self.stop()
        if message.uid in self.requested_ids:
            self.handle_message(message)

    def handle_message(self, message: Message) -> None:
        name = message_name_from_id(message.uid)
        message_values = message.get_fields()
        for field in message_values.keys():
            field_name = f"{name}_{field}"
            if self.message_dict[field_name] is not None:
                self.emit_csv()
            self.message_dict[field_name] = message_values[field]

    def emit_csv(self):
        pass

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
        pass

    def stop(self):
        pass