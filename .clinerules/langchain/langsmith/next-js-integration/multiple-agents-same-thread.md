# How to run multiple agents on the same thread

In LangSmith Deployment, a thread is not explicitly associated with a particular agent.
This means that you can run multiple agents on the same thread, which allows a different agent to continue from an initial agent's progress.

In this example, we will create two agents and then call them both on the same thread.
You'll see that the second agent will respond using information from the [checkpoint](/oss/python/langgraph/graph-api#checkpointer-state) generated in the thread by the first agent as context.

## Setup

<Tabs>
 

  <Tab title="Javascript">
    ```js  theme={null}
    import { Client } from "@langchain/langgraph-sdk";

    const client = new Client({ apiUrl: <DEPLOYMENT_URL> });

    const openAIAssistant = await client.assistants.create(
      { graphId: "agent", config: {"configurable": {"model_name": "openai"}}}
    );

    const assistants = await client.assistants.search();
    const defaultAssistant = assistants.find(a => !a.config);
    ```
  </Tab>

 
</Tabs>

We can see that these agents are different:

<Tabs>
 

  <Tab title="Javascript">
    ```js  theme={null}
    console.log(openAIAssistant);
    ```
  </Tab>

 
</Tabs>

Output:

```
{
"assistant_id": "db87f39d-b2b1-4da8-ac65-cf81beb3c766",
"graph_id": "agent",
"created_at": "2024-08-30T21:18:51.850581+00:00",
"updated_at": "2024-08-30T21:18:51.850581+00:00",
"config": {
"configurable": {
"model_name": "openai"
}
},
"metadata": {}
}
```

<Tabs>
 

  <Tab title="Javascript">
    ```js  theme={null}
    console.log(defaultAssistant);
    ```
  </Tab>

  
</Tabs>

Output:

```
{
"assistant_id": "fe096781-5601-53d2-b2f6-0d3403f7e9ca",
"graph_id": "agent",
"created_at": "2024-08-08T22:45:24.562906+00:00",
"updated_at": "2024-08-08T22:45:24.562906+00:00",
"config": {},
"metadata": {
"created_by": "system"
}
}
```

## Run assistants on thread

### Run OpenAI assistant

We can now run the OpenAI assistant on the thread first.

<Tabs>
  

  <Tab title="Javascript">
    ```js  theme={null}
    const thread = await client.threads.create();
    let input =  {"messages": [{"role": "user", "content": "who made you?"}]}

    const streamResponse = client.runs.stream(
      thread["thread_id"],
      openAIAssistant["assistant_id"],
      {
        input,
        streamMode: "updates"
      }
    );
    for await (const event of streamResponse) {
      console.log(`Receiving event of type: ${event.event}`);
      console.log(event.data);
      console.log("\n\n");
    }
    ```
  </Tab>

 
</Tabs>

Output:

```
Receiving event of type: metadata
{'run_id': '1ef671c5-fb83-6e70-b698-44dba2d9213e'}

Receiving event of type: updates
{'agent': {'messages': [{'content': 'I was created by OpenAI, a research organization focused on developing and advancing artificial intelligence technology.', 'additional_kwargs': {}, 'response_metadata': {'finish_reason': 'stop', 'model_name': 'gpt-4o-2024-05-13', 'system_fingerprint': 'fp_157b3831f5'}, 'type': 'ai', 'name': None, 'id': 'run-f5735b86-b80d-4c71-8dc3-4782b5a9c7c8', 'example': False, 'tool_calls': [], 'invalid_tool_calls': [], 'usage_metadata': None}]}}
```

### Run default assistant

Now, we can run it on the default assistant and see that this second assistant is aware of the initial question, and can answer the question, "and you?":

<Tabs>
 

  <Tab title="Javascript">
    ```js  theme={null}
    let input =  {"messages": [{"role": "user", "content": "and you?"}]}

    const streamResponse = client.runs.stream(
      thread["thread_id"],
      defaultAssistant["assistant_id"],
      {
        input,
        streamMode: "updates"
      }
    );
    for await (const event of streamResponse) {
      console.log(`Receiving event of type: ${event.event}`);
      console.log(event.data);
      console.log("\n\n");
    }
    ```
  </Tab>

 
</Tabs>

Output:

```
Receiving event of type: metadata
{'run_id': '1ef6722d-80b3-6fbb-9324-253796b1cd13'}

Receiving event of type: updates
{'agent': {'messages': [{'content': [{'text': 'I am an artificial intelligence created by Anthropic, not by OpenAI. I should not have stated that OpenAI created me, as that is incorrect. Anthropic is the company that developed and trained me using advanced language models and AI technology. I will be more careful about providing accurate information regarding my origins in the future.', 'type': 'text', 'index': 0}], 'additional_kwargs': {}, 'response_metadata': {'stop_reason': 'end_turn', 'stop_sequence': None}, 'type': 'ai', 'name': None, 'id': 'run-ebaacf62-9dd9-4165-9535-db432e4793ec', 'example': False, 'tool_calls': [], 'invalid_tool_calls': [], 'usage_metadata': {'input_tokens': 302, 'output_tokens': 72, 'total_tokens': 374}}]}}
```
