# Time travel using the server API

LangGraph provides the [**time travel**](/oss/python/langgraph/use-time-travel) functionality to resume execution from a prior checkpoint, either replaying the same state or modifying it to explore alternatives. In all cases, resuming past execution produces a new fork in the history.

To time travel using the LangSmith Deployment API (via the LangGraph SDK):

1. **Run the graph** with initial inputs using [LangGraph SDK](/langsmith/langgraph-python-sdk)'s [client.runs.wait](https://reference.langchain.com/python/langsmith/deployment/sdk/#langgraph_sdk.client.RunsClient.wait) or [client.runs.stream](https://reference.langchain.com/python/langsmith/deployment/sdk/#langgraph_sdk.client.RunsClient.stream) APIs.
2. **Identify a checkpoint in an existing thread**: Use [client.threads.get\_history](https://reference.langchain.com/python/langsmith/deployment/sdk/#langgraph_sdk.client.ThreadsClient.get_history) method to retrieve the execution history for a specific `thread_id` and locate the desired `checkpoint_id`.
   Alternatively, set a [breakpoint](/oss/python/langgraph/interrupts) before the node(s) where you want execution to pause. You can then find the most recent checkpoint recorded up to that breakpoint.
3. **(Optional) modify the graph state**: Use the [client.threads.update\_state](https://reference.langchain.com/python/langsmith/deployment/sdk/#langgraph_sdk.client.ThreadsClient.update_state) method to modify the graph’s state at the checkpoint and resume execution from alternative state.
4. **Resume execution from the checkpoint**: Use the [client.runs.wait](https://reference.langchain.com/python/langsmith/deployment/sdk/#langgraph_sdk.client.RunsClient.wait) or [client.runs.stream](https://reference.langchain.com/python/langsmith/deployment/sdk/#langgraph_sdk.client.RunsClient.stream) APIs with an input of `None` and the appropriate `thread_id` and `checkpoint_id`.

## Use time travel in a workflow

<Accordion title="Example graph">
  ```python  theme={null}
  from typing_extensions import TypedDict, NotRequired
  from langgraph.graph import StateGraph, START, END
  from langchain.chat_models import init_chat_model
  from langgraph.checkpoint.memory import InMemorySaver

  class State(TypedDict):
      topic: NotRequired[str]
      joke: NotRequired[str]

  model = init_chat_model(
      "claude-sonnet-4-5-20250929",
      temperature=0,
  )

  def generate_topic(state: State):
      """LLM call to generate a topic for the joke"""
      msg = model.invoke("Give me a funny topic for a joke")
      return {"topic": msg.content}

  def write_joke(state: State):
      """LLM call to write a joke based on the topic"""
      msg = model.invoke(f"Write a short joke about {state['topic']}")
      return {"joke": msg.content}

  # Build workflow
  builder = StateGraph(State)

  # Add nodes
  builder.add_node("generate_topic", generate_topic)
  builder.add_node("write_joke", write_joke)

  # Add edges to connect nodes
  builder.add_edge(START, "generate_topic")
  builder.add_edge("generate_topic", "write_joke")

  # Compile
  graph = builder.compile()
  ```
</Accordion>

### 1. Run the graph

<Tabs>
 

  <Tab title="JavaScript">
    ```js  theme={null}
    import { Client } from "@langchain/langgraph-sdk";
    const client = new Client({ apiUrl: <DEPLOYMENT_URL> });

    // Using the graph deployed with the name "agent"
    const assistantID = "agent";

    // create a thread
    const thread = await client.threads.create();
    const threadID = thread["thread_id"];

    // Run the graph
    const result = await client.runs.wait(
      threadID,
      assistantID,
      { input: {}}
    );
    ```
  </Tab>

  
</Tabs>

### 2. Identify a checkpoint

<Tabs>
 

  <Tab title="JavaScript">
    ```js  theme={null}
    // The states are returned in reverse chronological order.
    const states = await client.threads.getHistory(threadID);
    const selectedState = states[1];
    console.log(selectedState);
    ```
  </Tab>


</Tabs>

<a id="optional" />

### 3. Update the state

[`update_state`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.update_state) will create a new checkpoint. The new checkpoint will be associated with the same thread, but a new checkpoint ID.

<Tabs>
 

  <Tab title="JavaScript">
    ```js  theme={null}
    const newConfig = await client.threads.updateState(
      threadID,
      {
        values: { "topic": "chickens" },
        checkpointId: selectedState["checkpoint_id"]
      }
    );
    console.log(newConfig);
    ```
  </Tab>

 
</Tabs>

### 4. Resume execution from the checkpoint

<Tabs>
 

  <Tab title="JavaScript">
    ```javascript {highlight={5,6}} theme={null}
    await client.runs.wait(
      threadID,
      assistantID,
      {
        input: null,
        checkpointId: newConfig["checkpoint_id"]
      }
    );
    ```
  </Tab>

 
</Tabs>

## Learn more

* [**LangGraph time travel guide**](/oss/python/langgraph/use-time-travel): learn more about using time travel in LangGraph.

