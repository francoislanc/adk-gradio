
# `gradio_agent_inspector`
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  

Agent Inspector for ADK

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

## `AgentInspector`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><code>value</code></td>
<td align="left" style="width: 25%;">

```python
str | Callable | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">default text to provide in textbox. If a function is provided, the function will be called each time the app loads to set the initial value of this component.</td>
</tr>

<tr>
<td align="left"><code>placeholder</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">placeholder hint to provide behind textbox.</td>
</tr>

<tr>
<td align="left"><code>label</code></td>
<td align="left" style="width: 25%;">

```python
str | I18nData | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.</td>
</tr>

<tr>
<td align="left"><code>every</code></td>
<td align="left" style="width: 25%;">

```python
Timer | float | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.</td>
</tr>

<tr>
<td align="left"><code>inputs</code></td>
<td align="left" style="width: 25%;">

```python
Component | Sequence[Component] | set[Component] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.</td>
</tr>

<tr>
<td align="left"><code>show_label</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">if True, will display label.</td>
</tr>

<tr>
<td align="left"><code>scale</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.</td>
</tr>

<tr>
<td align="left"><code>min_width</code></td>
<td align="left" style="width: 25%;">

```python
int
```

</td>
<td align="left"><code>160</code></td>
<td align="left">minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.</td>
</tr>

<tr>
<td align="left"><code>interactive</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">if True, will be rendered as an editable textbox; if False, editing will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will be hidden.</td>
</tr>

<tr>
<td align="left"><code>rtl</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True and `type` is "text", sets the direction of the text to right-to-left (cursor appears on the left of the text). Default is False, which renders cursor on the right.</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>render</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.</td>
</tr>

<tr>
<td align="left"><code>key</code></td>
<td align="left" style="width: 25%;">

```python
int | str | tuple[int | str, ...] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.</td>
</tr>

<tr>
<td align="left"><code>preserved_by_key</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>"value"</code></td>
<td align="left">A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.</td>
</tr>
</tbody></table>


### Events

| name | description |
|:-----|:------------|
| `change` | Triggered when the value of the AgentInspector changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input. |
| `input` | This listener is triggered when the user changes the value of the AgentInspector. |
| `submit` | This listener is triggered when the user presses the Enter key while the AgentInspector is focused. |



### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As output:** Is passed, passes text value as a {str} into the function.
- **As input:** Should return, expects a {str} returned from function and sets textarea value to it.

 ```python
 def predict(
     value: str | None
 ) -> str | None:
     return value
 ```
 
