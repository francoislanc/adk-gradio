
import gradio as gr
from app import demo as app
import os

_docs = {'AgentInspector': {'description': 'Creates a very simple textbox for user to enter string input or display string output.', 'members': {'__init__': {'value': {'type': 'str | Callable | None', 'default': 'None', 'description': 'default text to provide in textbox. If a function is provided, the function will be called each time the app loads to set the initial value of this component.'}, 'placeholder': {'type': 'str | None', 'default': 'None', 'description': 'placeholder hint to provide behind textbox.'}, 'label': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.'}, 'every': {'type': 'Timer | float | None', 'default': 'None', 'description': 'Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.'}, 'inputs': {'type': 'Component | Sequence[Component] | set[Component] | None', 'default': 'None', 'description': 'Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.'}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will display label.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.'}, 'interactive': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will be rendered as an editable textbox; if False, editing will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, component will be hidden.'}, 'rtl': {'type': 'bool', 'default': 'False', 'description': 'If True and `type` is "text", sets the direction of the text to right-to-left (cursor appears on the left of the text). Default is False, which renders cursor on the right.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'key': {'type': 'int | str | tuple[int | str, ...] | None', 'default': 'None', 'description': "in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render."}, 'preserved_by_key': {'type': 'list[str] | str | None', 'default': '"value"', 'description': "A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor."}}, 'postprocess': {'value': {'type': 'str | None', 'description': 'Expects a {str} returned from function and sets textarea value to it.'}}, 'preprocess': {'return': {'type': 'str | None', 'description': 'Passes text value as a {str} into the function.'}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the AgentInspector changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'input': {'type': None, 'default': None, 'description': 'This listener is triggered when the user changes the value of the AgentInspector.'}, 'submit': {'type': None, 'default': None, 'description': 'This listener is triggered when the user presses the Enter key while the AgentInspector is focused.'}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'AgentInspector': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_agent_inspector`

<div style="display: flex; gap: 7px;">
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  
</div>

Agent Inspector for ADK
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_agent_inspector
```

## Usage

```python
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
    for i in range(2):
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

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `AgentInspector`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["AgentInspector"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["AgentInspector"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, passes text value as a {str} into the function.
- **As output:** Should return, expects a {str} returned from function and sets textarea value to it.

 ```python
def predict(
    value: str | None
) -> str | None:
    return value
```
""", elem_classes=["md-custom", "AgentInspector-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          AgentInspector: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
