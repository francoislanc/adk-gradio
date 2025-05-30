<svelte:options accessors={true} />

<script lang="ts">
  import type { Gradio } from "@gradio/utils";
  import { Block } from "@gradio/atoms";
  import { BaseTabs as Tabs, type Tab } from "@gradio/tabs";
  import { BaseButton as Button } from "@gradio/button";
  import { BaseTabItem as TabItem } from "@gradio/tabitem";
  import { BaseJSON } from "@gradio/json";
  import type { LoadingStatus } from "@gradio/statustracker";
  import { tick } from "svelte";
  import type { ThemeMode } from "@gradio/core";
  import Column from "./Column.svelte";
  import EventView from "./EventView.svelte";
  import Close from "./icons/Close.svelte";
  import LeftArrow from "./icons/LeftArrow.svelte";
  import RightArrow from "./icons/RightArrow.svelte";
  import CustomRow from "./CustomRow.svelte";
  import {
    IconButton,
  } from "@gradio/atoms";

  export let gradio: Gradio<{
    change: never;
    submit: never;
    input: never;
    clear_status: LoadingStatus;
  }>;
  export let label = "Textbox";
  export let elem_id = "";
  export let elem_classes: string[] = [];
  export let visible = true;
  export let value = null;
  export let placeholder = "";
  export let show_label: boolean;
  export let scale: number | null = null;
  export let min_width: number | undefined = undefined;
  export let loading_status: LoadingStatus | undefined = undefined;
  export let value_is_output = false;
  export let interactive: boolean;
  export let rtl = false;
  export let root: string;
  export let theme_mode: ThemeMode = "light";
  export let height: number | string | undefined;
  export let min_height: number | string | undefined;
  export let max_height: number | string | undefined;

  let el: HTMLTextAreaElement | HTMLInputElement;
  const container = true;

  function handle_change(): void {
    gradio.dispatch("change");
    if (!value_is_output) {
      gradio.dispatch("input");
    }
  }

  function truncateText(text, length) {
    if (text.length <= length) {
      return text;
    }

    return text.substr(0, length) + "\u2026";
  }

  function title(part): string {
    let title = "";
    if (part.text) {
      title += "text:" + truncateText(part.text, 20);
    } else if (part.functionCall) {
      title += "functionCall: " + part.functionCall.name;
    } else if (part.functionResponse) {
      title += "functionResponse: " + part.functionResponse.name;
    } else if (part.executableCode) {
      title += "executableCode: " + part.executableCode.code.slice(0, 10);
    } else if (part.codeExecutionResult) {
      title += "codeExecutionResult: " + part.codeExecutionResult.outcome;
    }
    return title;
  }

  const traceLabelIconMap = new Map<string, string>([
    ["Invocation", "start"],
    ["agent_run", "directions_run"],
    ["tool", "build"],
    ["call_llm", "chat"],
  ]);

  // When the value changes, dispatch the change event via handle_change()
  // See the docs for an explanation: https://svelte.dev/docs/svelte-components#script-3-$-marks-a-statement-as-reactive
  $: value, handle_change();

  const TABS: Tab[] = [
    {
      label: "Events",
      id: "events",
      visible: true,
      interactive: true,
      elem_id: "events",
      scale: 1,
    },
    {
      label: "State",
      id: "state",
      visible: true,
      interactive: true,
      elem_id: "state",
      scale: 1,
    },
  ] as const;
  let selected_tab: (typeof TABS)[number]["id"] = "events";

  let selected_event = null;
  let selected_event_num = null;


  let filterNonUserEvent = (val) => {
    if (val != null) {
      const filteredEvents = val["events"].filter((e) => e["author"] != "user");
      return filteredEvents;
    } else {
      return null;
    }
  };

  function setEvent(e, i) {
    selected_event = e;
    selected_event_num = i;
  }

  function goNextEvent(events, currentEventNum) {
    if (currentEventNum < events.length) {
      selected_event_num = currentEventNum + 1;
      selected_event = events[selected_event_num];
      eventView.generateSVG(selected_event)
    }
  }
  function goPrevEvent(events, currentEventNum) {
    if (currentEventNum > 0) {
      selected_event_num = currentEventNum - 1;
      selected_event = events[selected_event_num];
      eventView.generateSVG(selected_event)
    }
  }
  let eventView
</script>

<Block
  {visible}
  test_id="json"
  {elem_id}
  {elem_classes}
  {container}
  {scale}
  {min_width}
  padding={true}
  allow_overflow={true}
  overflow_behavior="auto"
  {height}
  {min_height}
  {max_height}
>
  {@const session_value = value != null ? JSON.parse(value) : null}
  {@const nonUserEvents =
    value != null ? filterNonUserEvent(session_value) : null}

  {#if selected_event}
      <CustomRow
        elem_id="event-num"
      >
        <p>Event {selected_event_num + 1} / {nonUserEvents.length}</p>
        <IconButton
          Icon={LeftArrow}
          on:click={() => goPrevEvent(nonUserEvents, selected_event_num)}
        />
        <IconButton
          Icon={RightArrow}
          on:click={() => goNextEvent(nonUserEvents, selected_event_num)}
        />
        <IconButton
          Icon={Close}
          label="Close"
          on:click={() => (selected_event = null)}
        />
      </CustomRow>

      <EventView event={selected_event} bind:this={eventView} ></EventView>
  {:else}
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
        <Column>
          {#if nonUserEvents != null}
            {#each nonUserEvents as e, i}
              {#if selected_event && e["id"] == selected_event["id"]}
                <Button
                  size="md"
                  variant="primary"
                  on:click={() => (selected_event = null)}
                  >{i + 1}) {title(e["content"]["parts"][0])}</Button
                >
              {:else}
                <Button size="md" on:click={() => setEvent(e, i)}
                  >{i + 1}) {title(e["content"]["parts"][0])}</Button
                >
              {/if}
            {/each}
          {:else}
            <p>No conversation</p>
          {/if}
        </Column>
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
        {#if session_value != null}
          <BaseJSON
            theme_mode="dark"
            show_copy_button={false}
            value={session_value["state"]}
            label_height={100}
          />
        {:else}
          <p>No state</p>
        {/if}
      </TabItem>
    </Tabs>
  {/if}
</Block>

<style>
</style>
