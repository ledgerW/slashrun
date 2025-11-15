# React Flow Patterns & Examples

React Flow is a library for building node-based editors, workflow designers, diagrams, and interactive visualizations. This guide covers common patterns and implementation examples.

**Official Documentation:** [reactflow.dev](https://reactflow.dev)

---

## Installation

```bash
npm install @xyflow/react
```

**Import stylesheet in every component using React Flow:**
```typescript
import '@xyflow/react/dist/style.css';
```

---

## Core Concepts

### 1. Nodes
Nodes represent individual elements in your flow. Each node has:
- `id`: Unique identifier
- `position`: { x, y } coordinates
- `data`: Custom data payload
- `type`: Node type (optional, defaults to 'default')

### 2. Edges
Edges connect nodes. Each edge has:
- `id`: Unique identifier
- `source`: Source node id
- `target`: Target node id
- `type`: Edge type (optional)

### 3. Handles
Connection points on nodes where edges attach. Can be:
- Source handles (where edges start)
- Target handles (where edges end)

---

## Basic Implementation

### Minimal Flow Component

```typescript
'use client';

import { useState, useCallback } from 'react';
import {
  ReactFlow,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  type Node,
  type Edge,
  type NodeChange,
  type EdgeChange,
  type Connection,
  Background,
  Controls,
  MiniMap,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const initialNodes: Node[] = [
  {
    id: '1',
    type: 'input',
    data: { label: 'Start' },
    position: { x: 250, y: 0 },
  },
  {
    id: '2',
    data: { label: 'Process' },
    position: { x: 250, y: 100 },
  },
  {
    id: '3',
    type: 'output',
    data: { label: 'End' },
    position: { x: 250, y: 200 },
  },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2' },
  { id: 'e2-3', source: '2', target: '3' },
];

export default function BasicFlow() {
  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );

  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    []
  );

  return (
    <div style={{ width: '100%', height: '600px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}
```

---

## Custom Nodes

### Creating Custom Node Types

```typescript
// components/nodes/CustomNode.tsx
import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';

interface CustomNodeData {
  label: string;
  description?: string;
}

export default memo(({ data }: NodeProps<CustomNodeData>) => {
  return (
    <div className="px-4 py-2 shadow-md rounded-md bg-white border-2 border-stone-400">
      <Handle type="target" position={Position.Top} />
      
      <div>
        <div className="font-bold">{data.label}</div>
        {data.description && (
          <div className="text-gray-500 text-sm">{data.description}</div>
        )}
      </div>

      <Handle type="source" position={Position.Bottom} />
    </div>
  );
});

CustomNode.displayName = 'CustomNode';
```

### Using Custom Nodes

```typescript
import CustomNode from '@/components/nodes/CustomNode';

const nodeTypes = {
  custom: CustomNode,
};

export default function FlowWithCustomNodes() {
  const nodes: Node[] = [
    {
      id: '1',
      type: 'custom',
      data: { label: 'Custom Node', description: 'This is a custom node' },
      position: { x: 250, y: 100 },
    },
  ];

  return (
    <ReactFlow
      nodes={nodes}
      nodeTypes={nodeTypes}
      // ... other props
    />
  );
}
```

---

## Interactive Patterns

### Drag and Drop New Nodes

```typescript
'use client';

import { useState, useCallback, useRef } from 'react';
import { ReactFlow, type Node, type XYPosition } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

export default function DragDropFlow() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');
      
      if (typeof type === 'undefined' || !type || !reactFlowInstance) {
        return;
      }

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const newNode: Node = {
        id: `${Date.now()}`,
        type,
        position,
        data: { label: `${type} node` },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance]
  );

  return (
    <div className="flex h-screen">
      {/* Sidebar with draggable items */}
      <aside className="w-64 bg-gray-100 p-4">
        <h3 className="font-bold mb-4">Drag Nodes</h3>
        <div
          className="p-4 mb-2 bg-white border rounded cursor-move"
          draggable
          onDragStart={(e) => e.dataTransfer.setData('application/reactflow', 'default')}
        >
          Default Node
        </div>
        <div
          className="p-4 bg-white border rounded cursor-move"
          draggable
          onDragStart={(e) => e.dataTransfer.setData('application/reactflow', 'input')}
        >
          Input Node
        </div>
      </aside>

      {/* Flow canvas */}
      <div ref={reactFlowWrapper} className="flex-1">
        <ReactFlow
          nodes={nodes}
          onInit={setReactFlowInstance}
          onDrop={onDrop}
          onDragOver={onDragOver}
          fitView
        />
      </div>
    </div>
  );
}
```

### Node Selection and Context Menu

```typescript
import { useCallback, useState } from 'react';
import { ReactFlow, type Node } from '@xyflow/react';

export default function SelectableFlow() {
  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, []);

  const deleteNode = useCallback(() => {
    if (selectedNode) {
      setNodes((nds) => nds.filter((n) => n.id !== selectedNode.id));
      setSelectedNode(null);
    }
  }, [selectedNode]);

  return (
    <div className="relative h-screen">
      <ReactFlow
        nodes={nodes}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
      />
      
      {selectedNode && (
        <div className="absolute top-4 right-4 bg-white p-4 shadow-lg rounded">
          <h3 className="font-bold mb-2">Selected Node</h3>
          <p className="text-sm mb-2">{selectedNode.data.label}</p>
          <button
            onClick={deleteNode}
            className="px-3 py-1 bg-red-500 text-white rounded"
          >
            Delete
          </button>
        </div>
      )}
    </div>
  );
}
```

---

## Supabase Integration

### Save Flow to Database

```typescript
import { createClient } from '@/lib/supabase/client';

async function saveFlow(
  flowId: string,
  nodes: Node[],
  edges: Edge[]
) {
  const supabase = createClient();
  
  const { error } = await supabase
    .from('flows')
    .upsert({
      id: flowId,
      nodes: JSON.stringify(nodes),
      edges: JSON.stringify(edges),
      updated_at: new Date().toISOString(),
    });

  if (error) {
    console.error('Error saving flow:', error);
    return false;
  }
  
  return true;
}
```

### Load Flow from Database

```typescript
async function loadFlow(flowId: string) {
  const supabase = createClient();
  
  const { data, error } = await supabase
    .from('flows')
    .select('nodes, edges')
    .eq('id', flowId)
    .single();

  if (error) {
    console.error('Error loading flow:', error);
    return null;
  }

  return {
    nodes: JSON.parse(data.nodes) as Node[],
    edges: JSON.parse(data.edges) as Edge[],
  };
}
```

### Complete Flow with Autosave

```typescript
'use client';

import { useState, useCallback, useEffect } from 'react';
import { ReactFlow, type Node, type Edge } from '@xyflow/react';
import { createClient } from '@/lib/supabase/client';
import { useDebounce } from '@/hooks/use-debounce';

export default function AutosaveFlow({ flowId }: { flowId: string }) {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [saving, setSaving] = useState(false);

  // Debounce changes to avoid too frequent saves
  const debouncedNodes = useDebounce(nodes, 1000);
  const debouncedEdges = useDebounce(edges, 1000);

  // Load initial data
  useEffect(() => {
    async function load() {
      const supabase = createClient();
      const { data } = await supabase
        .from('flows')
        .select('nodes, edges')
        .eq('id', flowId)
        .single();

      if (data) {
        setNodes(JSON.parse(data.nodes));
        setEdges(JSON.parse(data.edges));
      }
    }
    load();
  }, [flowId]);

  // Autosave on changes
  useEffect(() => {
    async function save() {
      setSaving(true);
      const supabase = createClient();
      await supabase
        .from('flows')
        .upsert({
          id: flowId,
          nodes: JSON.stringify(debouncedNodes),
          edges: JSON.stringify(debouncedEdges),
          updated_at: new Date().toISOString(),
        });
      setSaving(false);
    }

    if (debouncedNodes.length > 0 || debouncedEdges.length > 0) {
      save();
    }
  }, [debouncedNodes, debouncedEdges, flowId]);

  return (
    <div className="relative h-screen">
      {saving && (
        <div className="absolute top-4 right-4 bg-blue-500 text-white px-3 py-1 rounded z-10">
          Saving...
        </div>
      )}
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={(changes) =>
          setNodes((nds) => applyNodeChanges(changes, nds))
        }
        onEdgesChange={(changes) =>
          setEdges((eds) => applyEdgeChanges(changes, eds))
        }
      />
    </div>
  );
}
```

---

## Styling and Theming

### Custom Edge Styles

```typescript
const edgeTypes = {
  custom: {
    type: 'smoothstep',
    animated: true,
    style: { stroke: '#3b82f6', strokeWidth: 2 },
  },
};

<ReactFlow edgeTypes={edgeTypes} />
```

### Node Styling with Tailwind

```typescript
export default function StyledNode({ data }: NodeProps) {
  return (
    <div className="px-6 py-3 shadow-lg rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white border-2 border-white">
      <Handle type="target" position={Position.Top} className="w-3 h-3" />
      <div className="font-bold text-lg">{data.label}</div>
      <Handle type="source" position={Position.Bottom} className="w-3 h-3" />
    </div>
  );
}
```

---

## Common Use Cases

### Workflow Designer
- Node-based workflow automation
- Conditional branching
- Process visualization

### Mind Maps
- Hierarchical idea organization
- Collapsible nodes
- Free-form layout

### System Architecture Diagrams
- Service connections
- Data flow visualization
- Infrastructure mapping

### Decision Trees
- Branch-based logic
- Conditional paths
- Outcome visualization

---

## Performance Tips

1. **Use `memo` for custom nodes** to prevent unnecessary re-renders
2. **Implement virtualization** for large flows (>1000 nodes)
3. **Debounce autosave** operations
4. **Use `fitView` sparingly** - only on initial load
5. **Optimize node data** - keep data payloads small

---

## Resources

- **Official Documentation:** [reactflow.dev/learn](https://reactflow.dev/learn)
- **Examples Gallery:** [reactflow.dev/examples](https://reactflow.dev/examples)
- **API Reference:** [reactflow.dev/api-reference](https://reactflow.dev/api-reference)
- **Discord Community:** [discord.gg/Bqt6xrs](https://discord.gg/Bqt6xrs)
- **GitHub:** [github.com/xyflow/xyflow](https://github.com/xyflow/xyflow)

---

## Example: Complete Application Structure

```
app/
├── flows/
│   ├── [id]/
│   │   └── page.tsx          # Flow editor page
│   └── page.tsx              # Flow list page
components/
├── flow/
│   ├── FlowEditor.tsx        # Main flow component
│   ├── FlowToolbar.tsx       # Controls and tools
│   └── FlowSidebar.tsx       # Node palette
└── nodes/
    ├── InputNode.tsx         # Custom input node
    ├── ProcessNode.tsx       # Custom process node
    └── OutputNode.tsx        # Custom output node
