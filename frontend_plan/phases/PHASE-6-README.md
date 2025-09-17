# Phase 6 — Scenario Builder (Ontology-aware Forms)

## Purpose

Implement the **Scenario Builder** - a comprehensive interface for creating and editing simulation scenarios with ontology-aware forms that map directly to the GlobalState structure. This phase enables users to create complex economic scenarios through guided forms, leveraging templates, and ensuring data consistency. The builder follows Palantir's ontology-driven design principles, where UI components are bound to domain entities (countries, rules, triggers).

This interface transforms the complex task of scenario creation into an intuitive, guided workflow that maintains data integrity while providing flexibility for advanced users.

## Inputs

**From Phase 5:**
- Time-series analysis for parameter validation and guidance
- Historical data ranges for realistic parameter bounds
- Statistical analysis tools for scenario validation
- Chart visualization for parameter impact preview

**Backend Dependencies:**
- Template endpoints: `GET /api/simulation/templates/mvs`, `GET /api/simulation/templates/fis`
- Scenario CRUD: `POST /api/simulation/scenarios`, `PUT /api/simulation/scenarios/{id}`
- Data validation: Parameter bounds, matrix consistency checks
- Country metadata: Available countries, regions, economic classifications

**External Dependencies:**
- Form validation libraries for complex validation rules
- JSON schema validation for structured data
- Autocomplete libraries for country/parameter selection

## Deliverables

```
frontend/
├── css/
│   └── components/
│       ├── scenario-builder.css  # Main builder interface
│       ├── wizard.css           # Step-by-step wizard styling
│       ├── form-components.css  # Custom form controls
│       ├── matrix-editor.css    # Matrix editing interface
│       └── validation.css       # Validation feedback styles
├── js/
│   ├── components/
│   │   ├── scenario-builder.js  # Main builder component
│   │   ├── wizard-stepper.js    # Step navigation component
│   │   ├── country-selector.js  # Country selection interface
│   │   ├── parameter-editor.js  # Economic parameter forms
│   │   └── matrix-editor.js     # Trade/relationship matrix editor
│   ├── features/
│   │   └── builder/
│   │       ├── builder-controller.js    # Builder state management
│   │       ├── steps/
│   │       │   ├── template-selection.js    # Template chooser
│   │       │   ├── countries-config.js      # Country configuration
│   │       │   ├── economics-config.js      # Economic parameters
│   │       │   ├── relationships-config.js  # Trade/alliance matrices
│   │       │   ├── rules-config.js          # Simulation rules
│   │       │   └── review-validate.js       # Final review step
│   │       ├── templates/
│   │       │   ├── mvs-template.js          # MVS scenario generator
│   │       │   ├── fis-template.js          # FIS scenario generator
│   │       │   └── custom-template.js       # Custom scenario base
│   │       └── validation/
│   │           ├── parameter-validation.js  # Economic parameter validation
│   │           ├── matrix-validation.js     # Matrix consistency checks
│   │           ├── rule-validation.js       # Simulation rule validation
│   │           └── scenario-validation.js   # Overall scenario validation
└── docs/
    └── PHASE-6-README.md         # This file
```

## Implementation Checklist

### Builder Interface Foundation
- [ ] **Wizard stepper**: Multi-step interface with progress indication
- [ ] **Step navigation**: Forward/back navigation with validation gates
- [ ] **Auto-save**: Automatic saving of progress to prevent data loss
- [ ] **Template system**: Load and customize MVS/FIS templates
- [ ] **Responsive design**: Builder works on different screen sizes
- [ ] **Keyboard navigation**: Full keyboard accessibility support
- [ ] **Help system**: Contextual help and documentation

### Template Integration
- [ ] **MVS template loader**: Load Minimum Viable Scenario template
- [ ] **FIS template loader**: Load Full Information Scenario template
- [ ] **Template customization**: Modify templates while preserving structure
- [ ] **Template comparison**: Compare different template options
- [ ] **Custom templates**: Create scenarios from scratch
- [ ] **Template validation**: Ensure template consistency before use
- [ ] **Template metadata**: Display template information and coverage

### Country Configuration
- [ ] **Country selection**: Multi-select interface for scenario countries
- [ ] **Regional grouping**: Organize countries by geographic regions
- [ ] **Economic classification**: Group by income level, development status
- [ ] **Country search**: Search and filter available countries
- [ ] **Bulk operations**: Apply settings to multiple countries
- [ ] **Country profiles**: Display key economic indicators per country
- [ ] **Validation**: Ensure minimum country requirements for scenarios

### Economic Parameter Editor
- [ ] **Macro parameters**: GDP, inflation, unemployment, policy rates
- [ ] **External sector**: Exchange rates, trade balances, capital flows
- [ ] **Financial sector**: Interest rates, spreads, financial conditions
- [ ] **Fiscal parameters**: Government spending, taxation, debt levels
- [ ] **Parameter validation**: Range checking, consistency validation
- [ ] **Historical context**: Show historical ranges for parameters
- [ ] **Unit conversion**: Handle different units and scales appropriately

### Relationship Matrix Editor
- [ ] **Trade matrix**: Bilateral trade flow configuration
- [ ] **Alliance matrix**: Diplomatic and military alliance strengths
- [ ] **Sanctions matrix**: Economic sanctions between countries
- [ ] **Interbank matrix**: Financial exposure and connections
- [ ] **Visual matrix editor**: Spreadsheet-like interface for matrix editing
- [ ] **Matrix validation**: Symmetry checks, sum constraints
- [ ] **Import/export**: CSV import/export for bulk matrix editing

### Rules and Regimes Configuration
- [ ] **Monetary rules**: Central bank reaction functions and policies
- [ ] **Fiscal rules**: Government spending and taxation policies
- [ ] **Trade rules**: Trade policy and tariff structures
- [ ] **Financial rules**: Banking regulations and financial policies
- [ ] **Rule parameters**: Configurable parameters for each rule type
- [ ] **Rule conflicts**: Detection and resolution of conflicting rules
- [ ] **Rule validation**: Parameter bounds and logical consistency

### Scenario Validation
- [ ] **Parameter bounds**: Validate all parameters within reasonable ranges
- [ ] **Matrix consistency**: Check matrix properties (symmetry, positivity)
- [ ] **Economic consistency**: Validate economic relationships and constraints
- [ ] **Completeness check**: Ensure all required data is provided
- [ ] **Conflict detection**: Identify potential rule or parameter conflicts
- [ ] **Warning system**: Highlight potential issues with explanations
- [ ] **Validation reporting**: Comprehensive validation report generation

## API Integration Details

### Template Loading
```javascript
// Load scenario templates
async function loadTemplates() {
  const [mvsTemplate, fisTemplate] = await Promise.all([
    apiClient.get('/simulation/templates/mvs'),
    apiClient.get('/simulation/templates/fis')
  ]);
  
  return {
    mvs: {
      name: 'Minimum Viable Scenario',
      description: mvsTemplate.description,
      countries_count: mvsTemplate.countries_count,
      state: mvsTemplate.state
    },
    fis: {
      name: 'Full Information Scenario', 
      description: fisTemplate.description,
      countries_count: fisTemplate.countries_count,
      state: fisTemplate.state
    }
  };
}
```

### Scenario Creation
```javascript
// Create new scenario from builder data
async function createScenario(builderData) {
  const scenarioPayload = {
    name: builderData.name,
    description: builderData.description,
    initial_state: {
      t: 0,
      base_ccy: builderData.baseCurrency,
      countries: builderData.countries,
      trade_matrix: builderData.tradeMatrix,
      sanctions: builderData.sanctions,
      alliances: builderData.alliances,
      interbank: builderData.interbankMatrix,
      rules: builderData.rules,
      commodity_prices: builderData.commodityPrices
    },
    triggers: builderData.triggers || []
  };
  
  const response = await apiClient.post('/simulation/scenarios', scenarioPayload);
  return response;
}
```

### Validation Integration
```javascript
// Validate scenario data before creation
function validateScenario(scenarioData) {
  const errors = [];
  const warnings = [];
  
  // Country validation
  if (Object.keys(scenarioData.countries).length < 2) {
    errors.push('Scenario must include at least 2 countries');
  }
  
  // Economic parameter validation
  Object.entries(scenarioData.countries).forEach(([country, data]) => {
    if (data.macro.gdp <= 0) {
      errors.push(`${country}: GDP must be positive`);
    }
    if (data.macro.cpi_rate < -10 || data.macro.cpi_rate > 50) {
      warnings.push(`${country}: Inflation rate ${data.macro.cpi_rate}% is unusual`);
    }
  });
  
  // Matrix validation
  const tradeMatrix = scenarioData.trade_matrix;
  const countries = Object.keys(scenarioData.countries);
  
  countries.forEach(source => {
    countries.forEach(target => {
      if (source !== target) {
        const flow = tradeMatrix[`${source}->${target}`];
        if (flow && flow < 0) {
          errors.push(`Trade flow ${source}->${target} cannot be negative`);
        }
      }
    });
  });
  
  return { errors, warnings, isValid: errors.length === 0 };
}
```

## Component Specifications

### Scenario Builder Controller
```javascript
class ScenarioBuilderController {
  constructor(container, apiClient, stateManager)
  
  // Builder lifecycle
  initialize(templateType)
  save(draft = true)
  load(scenarioId)
  reset()
  
  // Step management
  goToStep(stepIndex)
  nextStep()
  previousStep()
  canAdvance(stepIndex)
  
  // Template operations
  loadTemplate(templateType)
  customizeTemplate(modifications)
  resetToTemplate()
  
  // Data management
  updateCountries(countries)
  updateParameters(parameters)
  updateMatrices(matrices)
  updateRules(rules)
  
  // Validation
  validateStep(stepIndex)
  validateScenario()
  getValidationReport()
  
  // Events
  onStepChange(callback)
  onValidationChange(callback)
  onSave(callback)
}
```

### Matrix Editor Component
```javascript
class MatrixEditor {
  constructor(container, config)
  
  // Matrix operations
  setMatrix(matrixData)
  getMatrix()
  updateCell(row, col, value)
  
  // Validation
  validateMatrix()
  highlightErrors()
  showWarnings()
  
  // Import/Export
  importFromCSV(csvData)
  exportToCSV()
  
  // UI
  render()
  resize()
  enableEditing()
  disableEditing()
  
  // Events
  onCellChange(callback)
  onValidation(callback)
}
```

### Parameter Editor
```javascript
class ParameterEditor {
  constructor(container, parameterSchema)
  
  // Parameter management
  setParameters(parameters)
  getParameters()
  updateParameter(path, value)
  
  // Validation
  validateParameter(path, value)
  getParameterBounds(path)
  showHistoricalRange(path)
  
  // UI
  render()
  showHelp(parameterPath)
  highlightInvalid()
  
  // Events
  onChange(callback)
  onValidation(callback)
}
```

## Validation Tests

### Builder Interface
- [ ] **Step navigation**: All wizard steps navigate correctly forward/back
- [ ] **Auto-save**: Changes are saved automatically without data loss
- [ ] **Template loading**: MVS and FIS templates load without errors
- [ ] **Responsive design**: Builder works on tablet and desktop screens
- [ ] **Keyboard navigation**: All interactive elements accessible via keyboard
- [ ] **Help system**: Help content displays correctly for all sections

### Data Input and Validation
- [ ] **Parameter validation**: Invalid values are caught and highlighted
- [ ] **Matrix validation**: Matrix consistency checks work correctly
- [ ] **Country selection**: Country selection and filtering work properly
- [ ] **Bulk operations**: Multi-country operations apply correctly
- [ ] **Import/export**: CSV import/export preserves data accuracy

### Template System
- [ ] **Template consistency**: Templates load with valid, complete data
- [ ] **Customization**: Template modifications don't break data structure
- [ ] **Comparison**: Template comparison shows meaningful differences
- [ ] **Reset functionality**: Reset to template restores original state

### Scenario Creation
- [ ] **API integration**: Scenarios created successfully via API
- [ ] **Data integrity**: Created scenarios match builder input exactly
- [ ] **Validation reporting**: Validation reports are comprehensive and accurate
- [ ] **Error handling**: API errors are handled gracefully with user feedback

## Architecture Decisions

### Form Architecture
**Decision**: Custom form components with JSON schema validation  
**Rationale**: Flexibility for complex economic data, consistent validation  
**Implementation**: Reusable form components with schema-driven validation

### Data Management
**Decision**: Centralized builder state with immutable updates  
**Rationale**: Predictable state changes, easy undo/redo, debugging  
**Implementation**: Redux-like pattern with action/reducer architecture

### Validation Strategy
**Decision**: Multi-level validation (field, step, scenario)  
**Rationale**: Early error detection, guided user experience  
**Implementation**: Validation pipeline with severity levels

### Template System
**Decision**: Template as data structure with overlay modifications  
**Rationale**: Preserve template integrity while allowing customization  
**Implementation**: Deep merge with validation of modifications

## Performance Considerations

### Form Rendering
- **Virtual scrolling**: Handle large country lists efficiently
- **Lazy loading**: Load parameter schemas on demand
- **Debounced validation**: Avoid excessive validation during typing
- **Memoization**: Cache expensive validation computations

### Matrix Editing
- **Virtual table**: Handle large matrices (100x100+) efficiently
- **Batch updates**: Group multiple cell changes for performance
- **Background validation**: Validate matrices asynchronously
- **Memory management**: Clean up large data structures appropriately

### Data Persistence
- **Incremental saves**: Only save changed data sections
- **Compression**: Compress large matrices for storage
- **Background sync**: Save progress without blocking UI

## Handoff Memo → Phase 7

**What's Complete:**
- Comprehensive scenario builder with wizard interface
- Template system integration (MVS/FIS) with customization
- Country selection and economic parameter configuration
- Matrix editors for trade, sanctions, alliances, interbank relationships
- Multi-level validation system with comprehensive error reporting
- Auto-save functionality and data persistence

**What's Next:**
Phase 7 will implement the **Trigger Designer** - advanced interface for creating and testing triggers with condition builder and action composer. This includes:
- Visual trigger condition builder with logical operators
- Action composer for policy changes and state modifications  
- Dry-run preview system showing when triggers would fire
- Integration with scenario builder for trigger attachment
- Trigger testing and debugging tools

**Key Integration Points for Phase 7:**
- Scenario builder will include basic trigger attachment
- Trigger designer will reference scenario country/parameter structure
- Timeline integration for trigger testing and preview
- Evidence rail integration for trigger impact analysis

**Shared Data Requirements:**
- GlobalState schema for trigger condition/action validation
- Country and parameter metadata for trigger builder
- Historical scenarios for trigger testing and validation
- Trigger examples and templates for common use cases

**Architecture Notes:**
- Trigger designer will be a specialized interface component
- Consider visual programming approach for complex trigger logic
- Plan for trigger versioning and scenario impact analysis
- Integration with existing validation and state management systems

**Trigger Design Needs for Phase 7:**
- Condition expression parser and validator
- Action effect preview and validation
- Trigger conflict detection between multiple triggers
- Performance optimization for trigger evaluation during simulation
