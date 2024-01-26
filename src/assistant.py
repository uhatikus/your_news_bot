from openai import OpenAI
import time

import os
from dotenv import load_dotenv

load_dotenv()


OPENAI_API_KEY_FOR_NEWS = os.getenv("OPENAI_API_KEY_FOR_NEWS")
OPENAI_ASSISTANT_ID_FOR_NEWS = os.getenv("OPENAI_ASSISTANT_ID_FOR_NEWS")


class Assistant:
    def __init__(self):
        with open("instructions.txt") as f:
            lines = f.readlines()
            instructions = "".join(lines).replace("\n", " ")
        model = "gpt-3.5-turbo"
        self.client = OpenAI(api_key=OPENAI_API_KEY_FOR_NEWS)

        self.assistant_id = OPENAI_ASSISTANT_ID_FOR_NEWS
        # print(self.client.beta.assistants.list())
        self.assistant = self.client.beta.assistants.update(
            self.assistant_id, instructions=instructions, model=model
        )

        self.RUN = {
            "TERMINAL_STATES": ["expired", "completed", "failed", "cancelled"],
            "PENDING_STATES": ["queued", "in_progress", "cancelling"],
            "ACTION_STATES": ["requires_action"],
        }

        self.API_TIMEOUT = 10  # 10 seconds

    def __wait_on_run(self, thread_id: str, run):
        print(
            f"[run] before id: {run.id} status: {run.status}, error: {run.last_error}"
        )
        itr = 0
        while run.status in self.RUN["PENDING_STATES"]:
            print(
                f"[run] waiting for id: {run.id} status: {run.status}, error: {run.last_error}"
            )
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run.id, timeout=self.API_TIMEOUT
            )
            time.sleep(2)  # 2 seconds
        print(f"[run] after id: {run.id} status: {run.status}, error: {run.last_error}")

        return run

    def create_thread(self):
        return self.client.beta.threads.create(timeout=self.API_TIMEOUT)

    def delete_thread(self, thread_id: str):
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id, timeout=self.API_TIMEOUT
        )

        file_ids = []
        for message in messages:
            file_ids.extend([file.id for file in message.file_ids])
        file_ids = set(file_ids)
        for file_id in file_ids:
            self.delete_file(file_id)

        return self.client.beta.threads.delete(
            thread_id=thread_id, timeout=self.API_TIMEOUT
        )

    def send_message(self, thread_id: str, message: str):
        runs = self.client.beta.threads.runs.list(thread_id, timeout=self.API_TIMEOUT)
        if len(runs.data) > 0:
            run = runs.data[0]
            if run.status not in self.RUN["TERMINAL_STATES"]:
                print(f"[send_message] Existing run: {run.id}, status: {run.status}")
                try:
                    self.client.beta.threads.runs.cancel(
                        thread_id=thread_id, run_id=run.id, timeout=self.API_TIMEOUT
                    )
                except Exception as e:
                    print(f"Error cancelling the run: {e}")
                self.__wait_on_run(thread_id, run)
                print(
                    f"[send_message] After wait | Existing run: {run.id}, status: {run.status}"
                )

        thread_message = self.client.beta.threads.messages.create(
            thread_id, role="user", content=message, timeout=self.API_TIMEOUT
        )
        print("sent a message")

        return thread_message

    def get_assistant_response(self, thread_id: str):
        print("creating a run")
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant.id,
            timeout=self.API_TIMEOUT,
        )

        while (run := self.__wait_on_run(thread_id, run)).status not in self.RUN[
            "TERMINAL_STATES"
        ]:
            print(f"run.status: {run.status}")

        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id, timeout=self.API_TIMEOUT
        )

        print(messages.data[0])

        return messages.data[0]
