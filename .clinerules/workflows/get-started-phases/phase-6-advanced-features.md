# Phase 6: Advanced Features [MANDATORY]

**Purpose:** Implement advanced features based on application needs

**Prerequisites:**
- Phase 5: User management complete

**References:**
- `.clinerules/ui/reactflow-patterns.md`
- `.clinerules/supabase/realtime_guide.md`

---

## ReactFlow Integration Decision [CRITICAL]

**Determine if ReactFlow is needed based on Phase 0 requirements.**

### ReactFlow is MANDATORY if application includes:

✅ **Workflow Designers**
- Building automation workflows
- Creating multi-step processes
- Designing approval chains

✅ **Mind Maps / Concept Mapping**
- Visual brainstorming tools
- Knowledge organization

✅ **System Architecture Diagrams**
- Infrastructure visualization
- Service dependency maps

✅ **Data Flow Visualizations**
- ETL pipeline designers
- Data transformation workflows

✅ **Decision Trees**
- Rule-based logic builders
- Conditional path visualization

✅ **Node-Based Editors**
- Visual programming interfaces
- Graph-based data structures

### ReactFlow NOT needed for:
❌ Simple CRUD applications
❌ List/table-based interfaces
❌ Form-based data entry
❌ Standard dashboards

---

## ReactFlow Implementation [IF APPLICABLE]

**If ReactFlow is needed, it is MANDATORY to implement.**

### Install ReactFlow

```bash
npm install @xyflow/react
```

### Basic Flow Component

**Reference:** `.clinerules/ui/reactflow-patterns.md` for complete patterns

**`components/flow-editor.tsx`:**
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

export default function FlowEditor({
  initialNodes,
  initialEdges,
}: {
  initialNodes: Node[];
  initialEdges: Edge[];
}) {
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

### Save/Load with Supabase

**`lib/flow-storage.ts`:**
```typescript
import { createClient } from '@/lib/supabase/client';
import type { Node, Edge } from '@xyflow/react';

export async function saveFlow(
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

  return { error };
}

export async function loadFlow(flowId: string) {
  const supabase = createClient();
  
  const { data, error } = await supabase
    .from('flows')
    .select('nodes, edges')
    .eq('id', flowId)
    .single();

  if (error || !data) return null;

  return {
    nodes: JSON.parse(data.nodes) as Node[],
    edges: JSON.parse(data.edges) as Edge[],
  };
}
```

**See `.clinerules/ui/reactflow-patterns.md` for:**
- Custom node types
- Drag-and-drop functionality
- Autosave implementation
- Advanced patterns

---

## Real-time Features [IF APPLICABLE]

**If application needs real-time features, implement using Supabase Realtime.**

**Reference:** `.clinerules/supabase/realtime_guide.md`

### Basic Realtime Subscription

```typescript
'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@/lib/supabase/client';

export default function RealtimeComponent() {
  const [data, setData] = useState([]);
  const supabase = createClient();

  useEffect(() => {
    // Initial fetch
    fetchData();

    // Subscribe to changes
    const channel = supabase
      .channel('table-changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'your_table'
        },
        (payload) => {
          // Handle real-time updates
          fetchData();
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  async function fetchData() {
    const { data } = await supabase
      .from('your_table')
      .select('*');
    setData(data || []);
  }

  return <div>{/* Render data */}</div>;
}
```

---

## File Uploads [IF APPLICABLE]

**If application handles file uploads:**

### Install Upload Components

```bash
npx shadcn@latest add https://supabase.com/ui/blocks/dropzone
```

### Basic File Upload

```typescript
'use client';

import { useState } from 'react';
import { createClient } from '@/lib/supabase/client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';

export function FileUpload() {
  const [uploading, setUploading] = useState(false);
  const supabase = createClient();

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const fileExt = file.name.split('.').pop();
      const fileName = `${Math.random()}.${fileExt}`;
      
      const { error } = await supabase.storage
        .from('uploads')
        .upload(fileName, file);

      if (error) throw error;
      
      toast.success('File uploaded successfully');
    } catch (error) {
      toast.error('Upload failed');
      console.error(error);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div>
      <Input
        type="file"
        onChange={handleUpload}
        disabled={uploading}
      />
    </div>
  );
}
```

---

## Analytics/Charts [IF APPLICABLE]

**If application needs data visualization:**

```bash
npx shadcn@latest add chart
```

**See:** [ui.shadcn.com/charts](https://ui.shadcn.com/charts) for examples

---

## Phase 6 Completion Checklist

**ReactFlow (if applicable):**
- [ ] ReactFlow installed
- [ ] Basic flow editor implemented
- [ ] Custom node types created (if needed)
- [ ] Save/load functionality working
- [ ] Flow persists to database

**Real-time (if applicable):**
- [ ] Realtime subscriptions set up
- [ ] Updates reflect immediately
- [ ] Cleanup on unmount

**File Uploads (if applicable):**
- [ ] Storage bucket created
- [ ] Upload functionality working
- [ ] Files accessible

**Analytics (if applicable):**
- [ ] Charts components installed
- [ ] Data visualization working

---

## Next Phase

**Proceed to:** [Phase 7: Polish & Documentation](./phase-7-polish-and-docs.md)
