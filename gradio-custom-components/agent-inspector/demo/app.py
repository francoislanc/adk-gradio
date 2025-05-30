import json
from pathlib import Path
import gradio as gr
from gradio_agent_inspector import AgentInspector
import os


def simulate_conversation():
    dir_path = Path(os.path.dirname(os.path.realpath(__file__)))

    initial_state = {
        "state": {},
        "events": [],
    }

    states = []
    for i in range(3):
        session_value_p = dir_path / "session-sample" / f"value-{i}.json"
        with session_value_p.open("r", encoding="utf-8") as f:
            session_value = json.load(f)

            # attach event trace and graph info to the event
            for e in session_value["events"]:
                event_trace_p = dir_path / "event-trace" / f"trace-{e['id']}.json"
                if event_trace_p.exists():
                    with event_trace_p.open("r", encoding="utf-8") as trace_f:
                        event_trace = json.load(trace_f)
                        if "gcp.vertex.agent.llm_request" in event_trace:
                            event_trace["gcp.vertex.agent.llm_request"] = json.loads(
                                event_trace["gcp.vertex.agent.llm_request"]
                            )
                        if "gcp.vertex.agent.llm_response" in event_trace:
                            event_trace["gcp.vertex.agent.llm_response"] = json.loads(
                                event_trace["gcp.vertex.agent.llm_response"]
                            )
                        e["trace"] = event_trace
                event_graph_p = dir_path / "event-trace" / f"graph-{e['id']}.json"
                if event_graph_p.exists():
                    with event_graph_p.open("r", encoding="utf-8") as graph_f:
                        event_graph = json.load(graph_f)
                        e["graph"] = event_graph
            states.append(session_value)

    return initial_state, states


def update_conversation_state(state_index, states):
    if (state_index + 1) >= len(states):
        return states[state_index], state_index
    else:
        new_index = state_index + 1
        return states[new_index], new_index


initial_state, conversation_states = simulate_conversation()

with gr.Blocks() as demo:
    gr.Markdown("# Agent Inspector")

    state_counter = gr.State(-1)

    agent_inspector = AgentInspector(json.dumps(initial_state))

    with gr.Row():
        next_btn = gr.Button(
            f"▶️ Next ({0} / {len(conversation_states)})", variant="primary"
        )
        reset_btn = gr.Button("🔄 Reset", variant="secondary")

    def next_state(current_counter):
        new_state, new_counter = update_conversation_state(
            current_counter, conversation_states
        )

        json_state = json.dumps(new_state)
        next_button_label = f"▶️ Next ({new_counter+1} / {len(conversation_states)})"

        return json_state, new_counter, next_button_label

    def reset_conversation():
        json_state = json.dumps(initial_state)
        next_button_label = f"▶️ Next ({0} / {len(conversation_states)})"

        return json_state, -1, next_button_label

    next_btn.click(
        next_state,
        inputs=[state_counter],
        outputs=[agent_inspector, state_counter, next_btn],
    )

    reset_btn.click(
        reset_conversation, outputs=[agent_inspector, state_counter, next_btn]
    )

    # examples = gr.Examples(
    #     examples=[
    #         s for s in conversation_states
    #     ],
    #     inputs=[initial_state],
    # )

if __name__ == "__main__":
    demo.launch()
