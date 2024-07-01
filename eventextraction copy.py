from openai import OpenAI, AssistantEventHandler
from dotenv import load_dotenv
import os
from pathlib import Path
from typing_extensions import override
import io
import sys
import json
import ast
import re

#what things on the our lady of the road and center for the homeless qualify as "events"? (so i can test on those sites)

"""instructions: Please take the supplied html file and return a string in the 
structure of a python dictionary of events that show up on the page. This dictionary 
should contain ALL events, past, present, and future. Return the events as a python 
dictionary with the events as the keys, and the value of each event being another dictionary 
of event details, including the date of the event, description, and an 'outdated' key, which 
should automatically be set to 'tbd'. Return the date in 'month year' format, for example, 'November 2023'. If there is no date,
make the date 'tbd', if there is only a month and no year, automatically make the year the current year in time.
REturn the dictionary as a string, NOT a code block, and DO NOT RESPOND WITH ANY TEXT OTHER THAN THE DICTIONARY."""


def extract_events():
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    client = OpenAI()
    assistant = client.beta.assistants.create(
        name="Event Extraction Assistant",
        instructions="""Take the supplied pdf file(s) and use computer vision to observe them and organize all events that are present in the files; past present and future. Return the events as a STRING with the structure of a python dictionary; do NOT return a code block. The keys should be the event title, and the value associated with each title should be another dictionary of event details, with the date, description, and an 'outdated' tag which should be set to 'tbd'. Always make the date be in 'month year' format, such as 'November 2024', and do not have the day in the date. If there is no information on the date, mark it as 'tbd', and if there is a month but no year, put the current year as the year. Do not return ANY information other than this dictionary.""",
        model="gpt-4o",
        tools=[{"type": "file_search"}],
    )

    vector_store = client.beta.vector_stores.create(name="Events PDF File(s)")


    file_paths = ["SMH_page.pdf"]
    file_streams = [open(path, "rb") for path in file_paths]


    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    print(file_batch.status)
    print(file_batch.file_counts)



    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )


    message_file = client.files.create(
        file=open("SMH_page.pdf", "rb"), purpose="assistants"
    )

    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": """Take the supplied pdf file(s) and use computer vision to observe them and organize all events that are present in the files; past present and future. Return the events as a STRING with the structure of a python dictionary; do NOT return a code block. The keys should be the event title, and the value associated with each title should be another dictionary of event details, with the date, description, and an 'outdated' tag which should be set to 'tbd'. Always make the date be in 'month year' format, such as 'November 2024', and do not have the day in the date. If there is no information on the date, mark it as 'tbd', and if there is a month but no year, put the current year as the year. Do not return ANY information other than this dictionary.""",
                "attachments": [
                    {"file_id": message_file.id, "tools": [{"type": "file_search"}]}
                ]
            }
        ]
    )

    print(thread.tool_resources.file_search)

    class EventHandler(AssistantEventHandler):
        @override
        def on_text_craeted(self, text) -> None:
            print(f"\nassistant > ", end="", flush=True)

        """@override
        def on_tool_call_created(self, tool_call):
            print(f"\nassistant > {tool_call.type}\n", flush=True)
        """
        @override
        def on_message_done(self, message) -> None:

            message_content = message.content[0].text
            annotations = message_content.annotations
            citations = []
            for index, annotation in enumerate(annotations):
                message_content.value = message_content.value.replace(
                    annotation.text, f"[{index}]"
                )
                if file_citation := getattr(annotation, "file_citation", None):
                    cited_file = client.files.retrieve(file_citation.file_id)
                    citations.append(f"[{index}] {cited_file.filename}")

            print(message_content.value)
            print("\n".join(citations))



    return_str = io.StringIO()
    sys.stdout = return_str


    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Please do not address the user",
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()

    sys.stdout = sys.__stdout__
    return_str = return_str.getvalue()
    print(return_str)
    #print(return_str)
    print("done!")

    
    #match = re.search(r'\{.*\}', return_str)
    #dict_str = match.group(0)
    return_dict = ast.literal_eval(return_str)
    
                                

    
    #print("python dict using json loads:", return_dict)
 

    return return_dict
if __name__ == "__main__":
    print("testing main")
    # Test the function directly in this module
    events = extract_events()
    print(events)
    print("\n\n")
    for element in events:
        print(element)