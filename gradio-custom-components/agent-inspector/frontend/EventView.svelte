<script lang="ts">
  import type { Gradio } from "@gradio/utils";
  import { BlockTitle } from "@gradio/atoms";
  import { Block } from "@gradio/atoms";
  import { BaseTabs as Tabs, type Tab } from "@gradio/tabs";
  import { BaseButton as Button } from "@gradio/button";
  import { BaseTabItem as TabItem } from "@gradio/tabitem";
  import { BaseJSON } from "@gradio/json";
  import { StatusTracker } from "@gradio/statustracker";
  import type { LoadingStatus } from "@gradio/statustracker";
  import { tick } from "svelte";
  import type { ThemeMode } from "@gradio/core";

  import { instance } from "@viz-js/viz";
  import { onMount } from "svelte";

  export let event: object;

  function truncateText(text, length) {
    if (text.length <= length) {
      return text;
    }

    return text.substr(0, length) + "\u2026";
  }

  const traceLabelIconMap = new Map<string, string>([
    ["Invocation", "start"],
    ["agent_run", "directions_run"],
    ["tool", "build"],
    ["call_llm", "chat"],
  ]);

  function getSpanIcon(label: string) {
    for (const [key, value] of traceLabelIconMap.entries()) {
      if (label.startsWith(key)) {
        return value;
      }
    }
    return "start";
  }

  let event_graph: string | null = null;
  export function generateSVG(event) {
    if (event?.graph?.dotSrc) {
      instance().then((viz) => {
        event_graph = viz.renderSVGElement(event?.graph?.dotSrc).outerHTML;
      });
    } else {
      event_graph = null
    }
  }

  const TABS: Tab[] = [
    {
      label: "Event",
      id: "event",
      visible: true,
      interactive: true,
      elem_id: "event",
      scale: 1,
    },
    {
      label: "Request",
      id: "request",
      visible: true,
      interactive: true,
      elem_id: "request",
      scale: 1,
    },
    {
      label: "Response",
      id: "response",
      visible: true,
      interactive: true,
      elem_id: "response",
      scale: 1,
    },
  ] as const;
  let selected_tab: (typeof TABS)[number]["id"] = "event";

  function removeTraceAndGraphKey(e) {
    return e;
    let { graph, trace, ...cleanE } = e;
    return cleanE;
  }

  onMount(async () => {
    generateSVG(event);
  });
</script>

<Tabs
  initial_tabs={TABS}
  selected={selected_tab}
  elem_classes={["editor-tabs"]}
>
  <TabItem
    id={TABS[0].id}
    label={TABS[0].label}
    visible={TABS[0].visible}
    interactive={TABS[0].interactive}
    elem_classes={["editor-tabitem"]}
    order={1}
    scale={1}
  >
    {#if event_graph}
      {@html event_graph}
    {/if}
    <BaseJSON
      theme_mode="dark"
      show_copy_button={false}
      value={removeTraceAndGraphKey(event)}
      label_height={10}
      show_indices={false}
      open={true}
    />
  </TabItem>
  <TabItem
    id={TABS[1].id}
    label={TABS[1].label}
    visible={TABS[1].visible}
    interactive={TABS[1].interactive}
    elem_classes={["editor-tabitem"]}
    order={1}
    scale={1}
  >
    {#if event && "trace" in event && "gcp.vertex.agent.llm_request" in event["trace"]}
      <BaseJSON
        theme_mode="dark"
        show_copy_button={false}
        value={event["trace"]["gcp.vertex.agent.llm_request"]}
        label_height={10}
        show_indices={false}
        open={true}
      />
    {/if}
  </TabItem>

  <TabItem
    id={TABS[2].id}
    label={TABS[2].label}
    visible={TABS[2].visible}
    interactive={TABS[2].interactive}
    elem_classes={["editor-tabitem"]}
    order={2}
    scale={1}
  >
    {#if event && "trace" in event && "gcp.vertex.agent.llm_response" in event["trace"]}
      <BaseJSON
        theme_mode="dark"
        show_copy_button={false}
        value={event["trace"]["gcp.vertex.agent.llm_response"]}
        label_height={10}
        show_indices={false}
        open={true}
      />
    {/if}
  </TabItem>
</Tabs>
