import json
from pathlib import Path
from typing import Iterator, List, Tuple
import uuid
import gradio as gr
from gradio_agent_inspector import AgentInspector
import os
from google.adk.cli.fast_api import get_fast_api_app
import uvicorn
import argparse

from adk_gradio_example.adk_simple_client import adk_client
import google.adk.cli.utils.envs as adk_envs
from google.adk.cli.utils.envs import _walk_to_root_until_found

from dotenv import load_dotenv
import logging

logger = logging.getLogger(__file__)


# overwrite load_dotenv_for_agent function to use the system environment variables if defined
# override=False => override=True
def new_load_dotenv_for_agent(
    agent_name: str, agent_parent_folder: str, filename: str = ".env"
):
    """Loads the .env file for the agent module."""
    # Gets the folder of agent_module as starting_folder
    starting_folder = os.path.abspath(os.path.join(agent_parent_folder, agent_name))
    dotenv_file_path = _walk_to_root_until_found(starting_folder, filename)
    if dotenv_file_path:
        load_dotenv(dotenv_file_path, override=False, verbose=True)
        logger.info(
            "Loaded %s file for %s at %s",
            filename,
            agent_name,
            dotenv_file_path,
        )
    else:
        logger.info("No %s file found for %s", filename, agent_name)


adk_envs.load_dotenv_for_agent = new_load_dotenv_for_agent


def update_events_adk_inspector(request: gr.Request):
    session_id = request.session_hash if request else str(uuid.uuid4())
    res = adk_client(session_id).get_events()
    return json.dumps(res, indent=2)


def update_trace_and_graph_adk_inspector(request: gr.Request):
    session_id = request.session_hash if request else str(uuid.uuid4())
    res = adk_client(session_id).get_events()
    if "events" in res:
        for e in res["events"]:
            try:
                trace = adk_client(session_id).get_trace(e["id"])
                if trace:
                    e["trace"] = trace

                graph = adk_client(session_id).get_graph(e["id"])
                if graph:
                    e["graph"] = graph
            except Exception as e:
                print(e)
    return json.dumps(res, indent=2)


def chat_with_adk_agent(
    user_message: str, history: List[Tuple[str, str]], request: gr.Request
) -> Iterator[List]:
    """Handle chat interaction with the ADK agent"""
    if not user_message.strip():
        yield history

    session_id = request.session_hash if request else str(uuid.uuid4())
    if not adk_client(session_id).session_id:
        history.append(
            gr.ChatMessage(
                role="assistant",
                content=f"Please setup the agent connection first using the Setup tab.",
            )
        )
        yield history

    # Get response from ADK agent
    try:
        response = adk_client(session_id).send_message(user_message)

        # Update history
        for r in response:
            parts_0 = r.get("content").get("parts")[0]
            if "text" in parts_0:
                assistant_chat_response = gr.ChatMessage(
                    role="assistant", content=parts_0["text"], metadata={}
                )
                history.append(assistant_chat_response)
            elif "functionCall" in parts_0:
                assistant_chat_response = gr.ChatMessage(
                    role="assistant",
                    content=parts_0["functionCall"]["name"],
                    metadata={"title": "Function calls"},
                )
                history.append(assistant_chat_response)
    except Exception as e:
        print(e)
    finally:
        yield history


def append_user_message(msg: str, history: list) -> tuple[str, list]:
    """Adds user message to chat history"""
    history.append(gr.ChatMessage(role="user", content=msg))
    return "", history


def update_api_keys(google_api_key: str, request: gr.Request):
    if len(google_api_key) > 0:
        session_id = request.session_hash if request else str(uuid.uuid4())
        adk_client(session_id).set_custom_api_key(google_api_key)


with gr.Blocks(title="Gradio Agent Inspector + ADK") as demo:
    gr.Markdown(
        """# 🕵️ Chat and Inspect ADK Agent in Gradio
                
[Agent Inspector](https://huggingface.co/spaces/Agents-MCP-Hackathon/gradio_agent_inspector) is a Gradio component designed to make this process easier and more transparent.  
Inspired by tools like the [ADK web](https://github.com/google/adk-web) debug panel, Agent Inspector brings similar functionality to the Gradio ecosystem.  
Whether you're building, testing, or fine-tuning your agent, Agent Inspector helps you understand what's happening under the hood.

Github repo :
[![adk-gradio](https://img.shields.io/badge/Github-ADK--gradio-blue)](https://github.com/francoislanc/adk-gradio)          

                 
                
                
                """
    )

    with gr.Tab("💬 Chat and debug"):
        with gr.Row(scale=1):
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    type="messages",
                    value=[],
                )
                msg_input = gr.Textbox(
                    placeholder="Enter your message here...",
                    show_label=False,
                    container=False,
                )
            with gr.Column(scale=2):
                agent_inspector = AgentInspector()

            msg_store = gr.State("")
            msg_input.submit(
                lambda msg: (msg, msg, ""),  # Store message and clear input
                inputs=[msg_input],
                outputs=[msg_store, msg_input, msg_input],
            ).then(
                append_user_message,
                inputs=[msg_store, chatbot],
                outputs=[msg_input, chatbot],
            ).then(
                chat_with_adk_agent,  # Generate and stream response
                inputs=[msg_store, chatbot],
                outputs=chatbot,
            ).then(
                update_events_adk_inspector,
                inputs=[],
                outputs=agent_inspector,
            ).then(
                update_trace_and_graph_adk_inspector,
                inputs=[],
                outputs=agent_inspector,
            )
    with gr.Tab("🔧 Configuration & Setup"):
        gr.Markdown("## 🔑 API Keys Configuration")

        with gr.Row():
            api_key_input = gr.Textbox(
                label="Google AI Studio API Key",
                placeholder="Enter your key...",
                type="password",
            )
        with gr.Row():
            save_keys_btn = gr.Button("💾 Save API Keys", variant="secondary")
        save_keys_btn.click(update_api_keys, inputs=[api_key_input], outputs=[])


def main():
    parser = argparse.ArgumentParser("simple_example")
    parser.add_argument(
        "--external-adk-api-server", default=True, action=argparse.BooleanOptionalAction
    )
    parser.add_argument("--adk-api-server-port", default=8000, type=int)
    args = parser.parse_args()

    print(f"{args.external_adk_api_server=} {args.adk_api_server_port=}")
    if args.external_adk_api_server:
        demo.launch()
    else:
        dir_path = (
            Path(os.path.dirname(os.path.realpath(__file__)))
            / "adk_gradio_example"
            / "adk_agents"
        )
        app = get_fast_api_app(agents_dir=str(dir_path), web=False)
        app = gr.mount_gradio_app(app, demo, path="/gradio")
        uvicorn.run(app, host="0.0.0.0", port=args.adk_api_server_port, reload=False)


if __name__ == "__main__":
    main()
