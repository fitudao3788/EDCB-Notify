import datetime
import os.path
import re
import threading
import time
from collections import deque

import dotenv
import httpx
from loguru import logger


class EDCBRecInfoWatcher:
    def __init__(self, target_file: str, webhook_url: str = ""):
        self.stop_pending = False
        self.thread = None

        self.target_file = os.path.abspath(target_file)
        self.webhook_url = webhook_url
        self.next_id = self.get_next_id()

        logger.info("Initial next id: {}".format(self.next_id))

    def send_webhook(self, program_title: str, program_started_at: datetime.datetime, program_ended_at: datetime.datetime, channel_name: str, record_drop: str, record_status: str) -> None:
        weeks = ["(月)", "(火)", "(水)", "(木)", "(金)", "(土)", "(日)"]
        week_str = weeks[int(program_started_at.weekday())]

        with httpx.Client() as client:
            payload = {
                "embeds": [{
                    "title": program_title,
                    "description": program_started_at.strftime(f"%Y/%m/%d{week_str} %H:%M〜") + program_ended_at.strftime("%H:%M"),
                    "color": 0x3498db,
                    "fields": [
                        {"name": "チャンネル", "value": channel_name, "inline": True},
                        {"name": "録画状態", "value": record_status, "inline": True},
                        {"name": "ドロップ", "value": record_drop, "inline": True},
                    ],
                    "footer": {"text": "EDCBNotify"},
                }],
            }
            client.post(self.webhook_url, json=payload)

    def get_next_id(self) -> int:
        if not os.path.isfile(self.target_file):
            return 0

        with open(self.target_file, encoding="utf-8") as f:
            chunk = deque(f, maxlen=5)

        for line in chunk:
            next_id_matches = re.search(r';;NextID=(\d+)', line)
            if next_id_matches:
                return int(next_id_matches.group(1))
        return 0

    def check_new_record(self) -> None:
        new_next_id = self.get_next_id()

        if new_next_id <= self.next_id:
            return

        logger.info(f"New next ID: {new_next_id}")

        with open(self.target_file, encoding="utf-8") as f:
            record_lines = f.readlines()

        for record_line in record_lines:
            record_data = record_line.rstrip("\n").split("\t")

            if len(record_data) <= 1:
                continue
            if self.next_id > int(record_data[-1]):
                continue

            program_title = record_data[1]
            raw_program_date = record_data[2]
            raw_program_started_at = record_data[3]
            raw_program_duration = record_data[4]
            channel_name = record_data[5]
            record_drop = record_data[10]
            record_status = record_data[15]

            program_started_at = datetime.datetime.strptime(raw_program_date + " " + raw_program_started_at, "%Y/%m/%d %H:%M:%S")
            program_duration_arr = raw_program_duration.split(":")
            program_duration = datetime.timedelta(hours=int(program_duration_arr[0]), minutes=int(program_duration_arr[1]), seconds=int(program_duration_arr[2]))
            program_ended_at = program_started_at + program_duration

            self.send_webhook(program_title, program_started_at, program_ended_at, channel_name, record_drop, record_status)

        self.next_id = new_next_id

    def _start_internal(self):
        while True:
            if self.stop_pending:
                break

            self.check_new_record()
            time.sleep(5)

    def start(self) -> None:
        self.thread = threading.Thread(target=self._start_internal)
        self.thread.start()

    def stop(self) -> None:
        self.stop_pending = True
        self.thread.join()


def main():
    dotenv.load_dotenv()

    target_file = os.environ.get("EDCB_RECINFO_FILE")
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

    if target_file is None or webhook_url is None:
        logger.warning("Please specify environment variables EDCB_RECINFO_FILE and DISCORD_WEBHOOK_URL.")
        return

    logger.info("Starting watcher...")

    watcher = EDCBRecInfoWatcher(target_file=target_file, webhook_url=webhook_url)
    watcher.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()


if __name__ == "__main__":
    main()
