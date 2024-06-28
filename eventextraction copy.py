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





def extract_events():
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    client = OpenAI()
    assistant = client.beta.assistants.create(
        name="Event Extraction Assistant",
        instructions="Please take the supplied html file and return a string in the structure of a python python dictionary, but not a literal code block, of events run by this organization. Return the events as a python dictionary with the events as the keys, and the values being dictionaries of the event details, such as date, description, and an 'outdated' event which should automatically be set to 'tbd'.",
        model="gpt-4o",
        tools=[{"type": "file_search"}],
    )

    vector_store = client.beta.vector_stores.create(name="Events HTML File")


    file_paths = ["SMH_page.html"]
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
        file=open("SMH_page.html", "rb"), purpose="assistants"
    )

    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "Please take the supplied html file and return a string in the structure of a python dictionary, but not a literal code block, of events run by this organization. Return the events as a python dictionary with the events as the keys, and the values being dictionaries of the event details, such as date, description, and an 'outdated' event which should automatically be set to 'tbd'. DO NOT RESPOND WITH ANY TEXT APART FROM THE PYTHON DICTIONARY",
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
    return_dict = json.loads(return_str)
    
                                

    
    #print("python dict using json loads:", return_dict)
 

    return return_str
if __name__ == "__main__":
    print("testing main")
    # Test the function directly in this module
    events = extract_events()
    print(events)