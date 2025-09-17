# Phase 7 — Trigger Designer (Advanced Event System)

## Purpose

Implement the **Trigger Designer** - a sophisticated interface for creating, testing, and managing simulation triggers with visual condition building and action composition. This phase enables users to create complex policy scenarios, external shocks, and conditional events that respond dynamically to simulation state changes. The designer follows investigative workflow patterns from Palantir, allowing users to build hypothesis-driven triggers with comprehensive testing capabilities.

This interface transforms trigger creation from code-based configuration to visual programming, making complex conditional logic accessible to policy analysts and economists.

## Inputs

**From Phase 6:**
- Scenario builder integration for trigger attachment to scenarios
- Country and parameter metadata for condition/action validation
- Template system for common trigger patterns
- Validation framework for complex logic validation

**Backend Dependencies:**
- Trigger examples: `GET /api/simulation/triggers/examples`
- Scenario integration: Triggers attached to scenarios during creation/editing
- GlobalState schema: Complete field structure for condition/action building
- Trigger evaluation engine: Backend validation of trigger logic

**External Dependencies:**
- Expression parser for trigger condition syntax
- Visual programming libraries for condition/action builders
- Code editor components for advanced users

## Deliverables

```
frontend/
├── css/
│   └── components/
│       ├── trigger-designer.css    # Main designer interface
│       ├── condition-builder.css   # Visual condition builder
│       ├── action-composer.css     # Action composition interface
│       ├── trigger-timeline.css    # Timeline preview and testing
│       └── trigger-library.css     # Trigger templates and examples
├── js/
│   ├── components/
│   │   ├── trigger-designer.js     # Main designer component
│   │   ├── condition-builder.js    # Visual condition builder
│   │   ├── action-composer.js      # Action composition interface
│   │   ├── trigger-timeline.js     # Timeline preview component
│   │   └── trigger-library.js      # Template and example browser
│   ├── features/
│   │   └── triggers/
│   │       ├── trigger-controller.js    # Trigger state management
│   │       ├── builder/
│   │       │   ├── condition-parser.js      # Condition expression parsing
│   │       │   ├── action-builder.js        # Action composition logic
│   │       │   ├── visual-editor.js         # Visual programming interface
│   │       │   └── code-editor.js           # Code-based trigger editing
│   │       ├── testing/
│   │       │   ├── dry-run-engine.js        # Trigger testing engine
│   │       │   ├── timeline-preview.js      # Preview when triggers fire
│   │       │   ├── scenario-tester.js       # Test against scenarios
│   │       │   └── conflict-detector.js     # Detect trigger conflicts
│   │       ├── templates/
│   │       │   ├── policy-triggers.js       # Policy change templates
│   │       │   ├── shock-triggers.js        # External shock templates
│   │       │   ├── threshold-triggers.js    # Threshold-based templates
│   │       │   └── custom-triggers.js       # Custom trigger patterns
│   │       └── validation/
│   │           ├── condition-validator.js   # Condition logic validation
│   │           ├── action-validator.js      # Action consistency validation
│   │           └── trigger-validator.js     # Overall trigger validation
└── docs/
    └── PHASE-7-README.md         # This file
```

## Implementation Checklist

### Designer Interface Foundation
- [ ] **Main designer layout**: Tabbed interface for conditions, actions, testing
- [ ] **Trigger metadata**: Name, description, documentation fields
- [ ] **Template integration**: Load and customize trigger templates
- [ ] **Save/load system**: Persistent trigger definitions with versioning
- [ ] **Help system**: Contextual help for trigger syntax and patterns
- [ ] **Keyboard shortcuts**: Power user shortcuts for common operations
- [ ] **Responsive design**: Works on different screen sizes

### Visual Condition Builder
- [ ] **Drag-and-drop interface**: Visual programming for trigger conditions
- [ ] **Logical operators**: AND, OR, NOT with visual grouping
- [ ] **Comparison operators**: Greater than, less than, equals, contains, etc.
- [ ] **Field selector**: Dropdown/autocomplete for GlobalState field paths
- [ ] **Value input**: Smart input widgets for different data types
- [ ] **Temporal conditions**: Time-based conditions (after timestep X, etc.)
- [ ] **Condition validation**: Real-time validation of condition logic

### Action Composer
- [ ] **Action types**: Policy changes, parameter overrides, events, notifications
- [ ] **Value modification**: Set, increment, multiply field values
- [ ] **Conditional actions**: Actions that depend on state conditions
- [ ] **Batch actions**: Apply multiple actions simultaneously
- [ ] **Action sequencing**: Order actions with dependencies
- [ ] **Action validation**: Validate action effects and consistency
- [ ] **Action preview**: Show expected state changes before saving

### Trigger Testing System
- [ ] **Dry-run engine**: Test triggers against historical scenarios
- [ ] **Timeline preview**: Visual timeline showing when triggers would fire
- [ ] **Multi-scenario testing**: Test triggers across different scenarios
- [ ] **Conflict detection**: Identify triggers that may conflict
- [ ] **Performance testing**: Measure trigger evaluation performance
- [ ] **Debug mode**: Step-by-step trigger evaluation debugging
- [ ] **Test reports**: Comprehensive testing result reports

### Template and Examples System
- [ ] **Trigger library**: Browse and load common trigger patterns
- [ ] **Policy templates**: Pre-built triggers for common policy changes
- [ ] **Shock templates**: External shock triggers (oil crisis, trade war, etc.)
- [ ] **Threshold templates**: Triggers based on economic thresholds
- [ ] **Custom templates**: Save and share custom trigger patterns
- [ ] **Template search**: Find relevant templates by keywords or category
- [ ] **Template validation**: Ensure templates work with current schema

### Advanced Features
- [ ] **Code editor**: Advanced users can write triggers in code
- [ ] **Expression syntax**: Rich expression language for complex conditions
- [ ] **Variable system**: Define and use variables within triggers
- [ ] **Trigger dependencies**: Triggers that depend on other triggers
- [ ] **Probabilistic triggers**: Triggers with probability of firing
- [ ] **Continuous triggers**: Triggers that fire every timestep when conditions met
- [ ] **One-time triggers**: Triggers that fire once and then disable

## API Integration Details

### Trigger Examples Loading
```javascript
// Load trigger examples and templates
async function loadTriggerExamples() {
  const examples = await apiClient.get('/simulation/triggers/examples');
  
  return {
    policy_changes: examples.filter(t => t.category === 'policy'),
    external_shocks: examples.filter(t => t.category === 'shock'),
    thresholds: examples.filter(t => t.category === 'threshold'),
    custom: examples.filter(t => t.category === 'custom')
  };
}
```

### Trigger Creation and Testing
```javascript
// Create trigger with conditions and actions
function createTrigger(triggerDefinition) {
  return {
    name: triggerDefinition.name,
    description: triggerDefinition.description,
    condition: {
      when: buildConditionExpression(triggerDefinition.conditions),
      once: triggerDefinition.oneTime || false
    },
    action: {
      type: triggerDefinition.actionType,
      parameters: triggerDefinition.actionParameters
    },
    expires_after_turns: triggerDefinition.expiresAfter || null
  };
}

// Test trigger against scenario data
async function testTrigger(trigger, scenarioId) {
  const history = await apiClient.get(`/simulation/scenarios/${scenarioId}/history`);
  const fireEvents = [];
  
  history.forEach(step => {
    const shouldFire = evaluateCondition(trigger.condition.when, step.state);
    if (shouldFire) {
      fireEvents.push({
        timestep: step.timestep,
        state: step.state,
        reason: explainCondition(trigger.condition.when, step.state)
      });
    }
  });
  
  return {
    wouldFire: fireEvents.length > 0,
    fireTimesteps: fireEvents.map(e => e.timestep),
    fireReasons: fireEvents.map(e => e.reason)
  };
}
```

### Condition Expression Building
```javascript
// Build condition expression from visual builder
function buildConditionExpression(conditions) {
  function buildNode(node) {
    switch (node.type) {
      case 'comparison':
        return `${node.field} ${node.operator} ${node.value}`;
      case 'logical':
        const left = buildNode(node.left);
        const right = buildNode(node.right);
        return `(${left}) ${node.operator.toUpperCase()} (${right})`;
      case 'temporal':
        return `t ${node.operator} ${node.timestep}`;
      default:
        return node.expression;
    }
  }
  
  return buildNode(conditions.root);
}
```

## Component Specifications

### Trigger Designer Controller
```javascript
class TriggerDesignerController {
  constructor(container, apiClient, stateManager)
  
  // Trigger lifecycle
  createTrigger(template)
  loadTrigger(triggerId)
  saveTrigger(trigger)
  deleteTrigger(triggerId)
  
  // Testing
  testTrigger(trigger, scenarioId)
  previewTimeline(trigger, scenarioId)
  detectConflicts(triggers)
  
  // Templates
  loadTemplates()
  saveAsTemplate(trigger, metadata)
  
  // Validation
  validateTrigger(trigger)
  validateCondition(condition)
  validateAction(action)
  
  // Events
  onTriggerChange(callback)
  onTestComplete(callback)
  onValidationChange(callback)
}
```

### Visual Condition Builder
```javascript
class VisualConditionBuilder {
  constructor(container, schema)
  
  // Visual building
  addCondition(parentId, conditionType)
  removeCondition(conditionId)
  updateCondition(conditionId, properties)
  
  // Logical operations
  addLogicalGroup(operator)
  changeLogicalOperator(groupId, operator)
  
  // Field selection
  setFieldPath(conditionId, fieldPath)
  getFieldSuggestions(query)
  validateFieldPath(fieldPath)
  
  // Expression export
  getExpression()
  setExpression(expressionString)
  
  // Events
  onConditionChange(callback)
  onValidation(callback)
}
```

### Dry-Run Testing Engine
```javascript
class DryRunTestingEngine {
  constructor(apiClient)
  
  // Test execution
  async runTest(trigger, scenarioId, options)
  async runBatchTest(triggers, scenarioIds)
  
  // Results analysis
  analyzeResults(testResults)
  generateReport(testResults)
  
  // Timeline generation
  generateTimeline(trigger, scenarioHistory)
  identifyFireEvents(trigger, scenarioHistory)
  
  // Performance measurement
  measureEvaluationTime(trigger, iterations)
  profileTriggerPerformance(triggers)
}
```

## Validation Tests

### Designer Interface
- [ ] **Template loading**: All trigger templates load without errors
- [ ] **Visual builder**: Condition builder creates valid expressions
- [ ] **Action composer**: Actions compose correctly with proper validation
- [ ] **Save/load**: Triggers save and load preserving all properties
- [ ] **Help system**: Help content displays correctly for all features

### Condition Building
- [ ] **Visual to expression**: Visual conditions convert to correct expressions
- [ ] **Expression validation**: Invalid conditions are caught and highlighted
- [ ] **Field path validation**: Field paths are validated against schema
- [ ] **Logical operations**: AND, OR, NOT operations work correctly
- [ ] **Temporal conditions**: Time-based conditions evaluate properly

### Action System
- [ ] **Action validation**: Actions are validated for consistency and safety
- [ ] **Action preview**: Action effects are previewed accurately
- [ ] **Batch actions**: Multiple actions execute in correct order
- [ ] **Action conflicts**: Conflicting actions are detected and warned

### Testing System
- [ ] **Dry-run accuracy**: Dry-run results match actual trigger behavior
- [ ] **Timeline preview**: Timeline shows correct fire events
- [ ] **Conflict detection**: Trigger conflicts are identified accurately
- [ ] **Performance testing**: Performance tests complete within reasonable time
- [ ] **Test reports**: Generated reports are comprehensive and accurate

## Architecture Decisions

### Expression Language
**Decision**: Custom expression language with visual builder  
**Rationale**: Balance simplicity for visual users with power for advanced users  
**Implementation**: Parser with both visual and code interfaces

### Testing Strategy
**Decision**: Client-side dry-run with server-side validation  
**Rationale**: Fast feedback while maintaining accuracy  
**Implementation**: Trigger evaluation engine in JavaScript

### Template System
**Decision**: JSON-based templates with metadata  
**Rationale**: Easy to create, share, and validate templates  
**Implementation**: Template loader with validation and customization

### Visual Programming Approach
**Decision**: Node-based visual programming with expression output  
**Rationale**: Accessible to non-programmers while maintaining precision  
**Implementation**: Drag-and-drop interface with expression compilation

## Performance Considerations

### Expression Evaluation
- **Compiled expressions**: Pre-compile expressions for faster evaluation
- **Caching**: Cache expensive field lookups and calculations
- **Lazy evaluation**: Only evaluate conditions when necessary
- **Optimization**: Optimize complex logical expressions

### Visual Builder
- **Virtual rendering**: Handle large condition trees efficiently
- **Debounced updates**: Avoid excessive re-rendering during editing
- **Memory management**: Clean up visual elements properly

### Testing Performance
- **Parallel testing**: Run multiple tests concurrently
- **Progress reporting**: Show progress for long-running tests
- **Result caching**: Cache test results for identical scenarios

## Handoff Memo → Phase 8

**What's Complete:**
- Visual trigger condition builder with drag-and-drop interface
- Action composer for policy changes and state modifications
- Comprehensive testing system with dry-run capabilities
- Template library with common trigger patterns
- Expression language with both visual and code interfaces
- Trigger conflict detection and performance analysis

**What's Next:**
Phase 8 will implement **Walkthroughs & Sharing** - pin-based narrative creation and guided investigation flows. This includes:
- Pinboard system for capturing key moments and insights
- Narrative composition with commentary and analysis
- Export functionality for sharing walkthroughs
- Guided walkthrough playback with automatic navigation
- Integration with all visualization components

**Key Integration Points for Phase 8:**
- Triggers can be pinned to walkthroughs to explain policy decisions
- Timeline integration for walkthrough navigation
- Map, network, and time-series views support pinning
- Evidence rail provides supporting data for walkthrough narratives

**Shared Data Requirements:**
- Pin data structure for capturing state snapshots and metadata
- Walkthrough composition and playback system
- Export formats for sharing (PDF, HTML, video)
- Annotation system for adding commentary to pins

**Architecture Notes:**
- Walkthrough system will be a meta-layer over existing visualizations
- Consider version control for collaborative walkthrough editing
- Plan for walkthrough templates and common narrative patterns
- Integration with authentication for sharing and permissions

**Walkthrough Design Needs for Phase 8:**
- Pin capture system for all visualization types
- Narrative flow and sequencing tools
- Export and sharing infrastructure
- Playback controls with automatic navigation between pins
