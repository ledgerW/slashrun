# Phase 8 — Walkthroughs & Sharing (Guided Investigation)

## Purpose

Implement **Walkthroughs & Sharing** - a sophisticated system for creating guided investigative narratives inspired by Palantir's walkthrough capabilities. This phase enables users to capture key moments, insights, and decision points during simulation analysis, then compose them into shareable narratives with commentary and supporting evidence. Walkthroughs transform individual analysis sessions into collaborative knowledge assets.

This system elevates SlashRun from a simulation tool to an investigative platform where analysts can document their reasoning, share insights, and guide others through complex economic scenarios.

## Inputs

**From Phase 7:**
- Trigger designer integration for capturing policy decision rationale
- Timeline system for navigation and temporal context
- All visualization components (map, network, time-series) for pinning
- Evidence rail for supporting data and audit trails

**Backend Dependencies:**
- User authentication for walkthrough ownership and sharing
- Storage system for walkthrough data and media assets
- Export capabilities for generating sharable formats
- Optional: Collaboration features for multi-user walkthroughs

**External Dependencies:**
- PDF generation library (jsPDF or similar)
- Image capture and manipulation libraries
- Video/GIF generation for animated walkthroughs (optional)
- Rich text editor for narrative composition

## Deliverables

```
frontend/
├── css/
│   └── components/
│       ├── walkthroughs.css        # Main walkthrough interface
│       ├── pinboard.css           # Pin management and display
│       ├── narrative-editor.css   # Story composition interface
│       ├── walkthrough-player.css # Playback interface
│       └── sharing.css            # Export and sharing UI
├── js/
│   ├── components/
│   │   ├── walkthrough-manager.js   # Main walkthrough interface
│   │   ├── pinboard.js             # Pin capture and management
│   │   ├── narrative-editor.js     # Story composition
│   │   ├── walkthrough-player.js   # Guided playback
│   │   └── sharing-panel.js        # Export and sharing controls
│   ├── features/
│   │   └── walkthroughs/
│   │       ├── walkthrough-controller.js  # Walkthrough state management
│   │       ├── capture/
│   │       │   ├── pin-capture.js         # Pin creation from views
│   │       │   ├── screenshot.js          # Screenshot capture
│   │       │   ├── data-capture.js        # State/data snapshot
│   │       │   └── annotation.js          # Commentary and notes
│   │       ├── composition/
│   │       │   ├── story-builder.js       # Narrative flow construction
│   │       │   ├── template-system.js     # Walkthrough templates
│   │       │   ├── media-manager.js       # Image/chart management
│   │       │   └── outline-editor.js      # Structure and flow editing
│   │       ├── playback/
│   │       │   ├── player-engine.js       # Navigation and presentation
│   │       │   ├── auto-navigation.js     # Automatic view switching
│   │       │   ├── timing-control.js      # Pause/play/speed controls
│   │       │   └── interaction-handler.js # User interaction during playback
│   │       └── export/
│   │           ├── pdf-generator.js       # PDF walkthrough export
│   │           ├── html-export.js         # Standalone HTML export
│   │           ├── presentation.js        # Slide-based presentation
│   │           └── data-package.js        # Data and analysis export
└── docs/
    └── PHASE-8-README.md         # This file
```

## Implementation Checklist

### Walkthrough Foundation
- [ ] **Walkthrough creation**: New walkthrough with metadata (title, description, author)
- [ ] **Walkthrough library**: Browse, search, and organize walkthroughs
- [ ] **Auto-save system**: Continuous saving of walkthrough progress
- [ ] **Version control**: Track changes and enable walkthrough versioning
- [ ] **Templates**: Pre-built walkthrough structures for common analysis types
- [ ] **Collaboration**: Multi-user editing and comment system (if applicable)
- [ ] **Access control**: Public/private walkthroughs with sharing permissions

### Pin Capture System
- [ ] **Universal pinning**: Pin from any visualization (map, network, time-series, evidence)
- [ ] **Pin types**: Screenshots, data snapshots, insights, decisions, questions
- [ ] **Automatic context**: Capture view state, timeline position, selected filters
- [ ] **Manual annotation**: Add commentary, titles, and explanations to pins
- [ ] **Media capture**: Screenshots with highlighting and annotation overlays
- [ ] **Data preservation**: Snapshot relevant data for future reference
- [ ] **Pin organization**: Categories, tags, and search within walkthroughs

### Narrative Composition
- [ ] **Story editor**: Rich text editor for walkthrough narrative
- [ ] **Pin integration**: Embed pins within narrative flow
- [ ] **Section structure**: Organize walkthroughs into logical sections/chapters  
- [ ] **Visual flow**: Storyboard view showing pin sequence and connections
- [ ] **Narrative templates**: Common investigation patterns (hypothesis→evidence→conclusion)
- [ ] **Cross-references**: Link between related pins and sections
- [ ] **Preview mode**: Preview walkthrough before sharing or export

### Guided Playback
- [ ] **Player interface**: Controls for playing through walkthrough
- [ ] **Auto-navigation**: Automatically switch views and navigate timeline
- [ ] **Interactive playback**: Allow viewer interaction during playback
- [ ] **Pacing controls**: Adjustable playback speed and pause points
- [ ] **Progress tracking**: Show progress through walkthrough
- [ ] **Bookmark system**: Jump to specific sections or pins
- [ ] **Viewer mode**: Clean interface for walkthrough consumption

### Export and Sharing
- [ ] **PDF export**: Professional PDF reports with charts and commentary
- [ ] **HTML export**: Standalone web pages with interactive elements
- [ ] **Presentation mode**: Slide-based presentation format
- [ ] **Data packages**: Export underlying data and analysis
- [ ] **Link sharing**: Shareable links with access controls
- [ ] **Embedding**: Embed walkthroughs in external sites (iframe)
- [ ] **Print-friendly**: Optimized layouts for printing

## API Integration Details

### Walkthrough Data Management
```javascript
// Walkthrough data structure
const walkthroughSchema = {
  id: 'walkthrough_uuid',
  title: 'Economic Crisis Analysis',
  description: 'Analysis of policy responses to inflation spike',
  author: { id: 'user_uuid', name: 'Jane Analyst' },
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T12:00:00Z',
  scenario_id: 'scenario_uuid',
  
  structure: {
    sections: [
      {
        id: 'section_1',
        title: 'Initial Conditions',
        narrative: 'The scenario begins with...',
        pins: ['pin_1', 'pin_2']
      }
    ]
  },
  
  pins: [
    {
      id: 'pin_1',
      type: 'insight',
      title: 'Inflation Threshold Breach',
      description: 'CPI exceeded 4% target at t=12',
      timestep: 12,
      view_state: {
        view: 'time-series',
        selected_countries: ['USA', 'EUR'],
        chart_config: { indicator: 'cpi_rate' }
      },
      media: {
        screenshot: 'screenshot_url',
        data_snapshot: { /* relevant data */ }
      },
      created_at: '2024-01-01T10:30:00Z'
    }
  ],
  
  settings: {
    public: false,
    allow_comments: true,
    export_formats: ['pdf', 'html']
  }
};
```

### Pin Capture Implementation
```javascript
// Universal pin capture from any view
class PinCapture {
  constructor(walkthroughId, viewManager, stateManager) {
    this.walkthroughId = walkthroughId;
    this.viewManager = viewManager;
    this.stateManager = stateManager;
  }
  
  async captureCurrentView(pinType, metadata) {
    const viewState = this.viewManager.getCurrentViewState();
    const screenshot = await this.captureScreenshot(viewState.container);
    const dataSnapshot = this.captureRelevantData(viewState);
    
    const pin = {
      id: generatePinId(),
      type: pinType,
      title: metadata.title,
      description: metadata.description,
      timestep: this.stateManager.getCurrentTimestep(),
      view_state: viewState,
      media: {
        screenshot: screenshot,
        data_snapshot: dataSnapshot
      },
      created_at: new Date().toISOString()
    };
    
    await this.savePinToWalkthrough(pin);
    return pin;
  }
  
  async captureScreenshot(container) {
    // Use html2canvas or similar to capture view
    const canvas = await html2canvas(container);
    return canvas.toDataURL('image/png');
  }
  
  captureRelevantData(viewState) {
    // Capture data relevant to current view
    switch(viewState.view) {
      case 'map':
        return {
          selected_countries: viewState.selected_countries,
          active_layers: viewState.active_layers,
          map_bounds: viewState.map_bounds
        };
      case 'network':
        return {
          selected_nodes: viewState.selected_nodes,
          layout: viewState.layout,
          filters: viewState.filters
        };
      // ... other view types
    }
  }
}
```

## Component Specifications

### Walkthrough Controller
```javascript
class WalkthroughController {
  constructor(container, apiClient, stateManager)
  
  // Walkthrough lifecycle
  createWalkthrough(metadata)
  loadWalkthrough(walkthroughId)
  saveWalkthrough()
  deleteWalkthrough(walkthroughId)
  
  // Pin management
  capturePin(type, metadata)
  updatePin(pinId, updates)
  removePin(pinId)
  reorderPins(newOrder)
  
  // Narrative composition
  updateNarrative(sectionId, content)
  addSection(title, position)
  removeSection(sectionId)
  
  // Playback
  startPlayback()
  pausePlayback()
  navigateToPin(pinId)
  setPlaybackSpeed(speed)
  
  // Export
  exportToPDF(options)
  exportToHTML(options)
  generateShareableLink()
  
  // Events
  onPinAdded(callback)
  onPlaybackStateChange(callback)
  onExportComplete(callback)
}
```

### Walkthrough Player
```javascript
class WalkthroughPlayer {
  constructor(container, walkthrough, viewManager)
  
  // Playback control
  play()
  pause()
  stop()
  goToPin(pinId)
  nextPin()
  previousPin()
  
  // Navigation
  navigateToViewState(viewState)
  animateTransition(fromState, toState)
  
  // Presentation
  enterPresentationMode()
  exitPresentationMode()
  toggleFullscreen()
  
  // Interaction
  allowViewerInteraction(enabled)
  captureViewerFeedback()
  
  // Progress
  getProgress()
  setProgress(progress)
}
```

### Export Engine
```javascript
class ExportEngine {
  constructor(walkthrough, viewManager)
  
  // PDF Export
  async generatePDF(options = {}) {
    const doc = new jsPDF();
    
    // Title page
    doc.addPage();
    doc.text(walkthrough.title, 20, 30);
    doc.text(walkthrough.description, 20, 50);
    
    // Process each section
    for (const section of walkthrough.structure.sections) {
      doc.addPage();
      doc.text(section.title, 20, 30);
      doc.text(section.narrative, 20, 50);
      
      // Add pins for this section
      for (const pinId of section.pins) {
        const pin = walkthrough.pins.find(p => p.id === pinId);
        await this.addPinToPDF(doc, pin);
      }
    }
    
    return doc;
  }
  
  // HTML Export
  async generateHTML(options = {}) {
    const template = await this.loadHTMLTemplate();
    const renderedContent = this.renderWalkthroughToHTML(walkthrough);
    return template.replace('{{CONTENT}}', renderedContent);
  }
  
  // Data Package Export
  async generateDataPackage() {
    const packageData = {
      walkthrough: walkthrough,
      data_snapshots: this.collectDataSnapshots(),
      media_assets: this.collectMediaAssets(),
      export_metadata: {
        generated_at: new Date().toISOString(),
        version: '1.0'
      }
    };
    
    return JSON.stringify(packageData, null, 2);
  }
}
```

## Validation Tests

### Pin Capture
- [ ] **Universal capture**: Pins can be captured from all visualization types
- [ ] **Screenshot quality**: Screenshots are clear and properly sized
- [ ] **Data preservation**: Pin data snapshots contain relevant context
- [ ] **Annotation system**: Comments and titles save correctly with pins
- [ ] **View state capture**: Pin navigation restores exact view state

### Narrative Composition
- [ ] **Rich text editor**: Editor supports formatting, links, and embedded media
- [ ] **Pin embedding**: Pins embed correctly within narrative flow
- [ ] **Section organization**: Sections can be added, reordered, and removed
- [ ] **Auto-save**: Changes save automatically without data loss
- [ ] **Preview accuracy**: Preview matches final walkthrough presentation

### Playback System
- [ ] **Navigation accuracy**: Playback navigates to correct views and timesteps
- [ ] **Transition smoothness**: View transitions are smooth and logical
- [ ] **Control responsiveness**: Play/pause/navigation controls work reliably
- [ ] **Progress tracking**: Progress indicator accurately reflects playback position
- [ ] **Interactive mode**: Viewer interactions work correctly during playback

### Export Functions
- [ ] **PDF quality**: PDF exports are well-formatted with clear images
- [ ] **HTML export**: HTML exports work offline and maintain interactivity
- [ ] **Data completeness**: Data packages include all necessary information
- [ ] **Sharing links**: Shareable links work correctly with access controls

## Architecture Decisions

### Pin Data Structure
**Decision**: Hierarchical pins with rich metadata and media attachments  
**Rationale**: Support complex narratives while preserving analytical context  
**Implementation**: JSON-based pins with binary media references

### Playback Engine
**Decision**: State-driven playback with view manager integration  
**Rationale**: Smooth integration with existing visualization components  
**Implementation**: Player controller orchestrates view state changes

### Export Strategy
**Decision**: Multiple export formats with configurable options  
**Rationale**: Support different use cases from presentations to archival  
**Implementation**: Pluggable export engines with common base interface

### Sharing and Collaboration
**Decision**: Link-based sharing with granular permissions  
**Rationale**: Simple sharing while maintaining security and access control  
**Implementation**: Token-based access with user authentication integration

## Performance Considerations

### Media Management
- **Image optimization**: Compress screenshots and media for storage/sharing
- **Lazy loading**: Load walkthrough media only when needed
- **Caching**: Cache frequently accessed walkthroughs and media
- **Progressive loading**: Load walkthrough sections progressively

### Export Performance
- **Background processing**: Generate large exports in background
- **Progress reporting**: Show progress for long-running export operations
- **Chunked processing**: Process large walkthroughs in chunks
- **Format optimization**: Optimize each export format for its use case

### Playback Performance
- **Preloading**: Preload next few pins/sections during playback
- **Smooth transitions**: Optimize view state changes for smooth animation
- **Memory management**: Clean up resources from previous pins

## Handoff Memo → Phase 9

**What's Complete:**
- Comprehensive pin capture system for all visualization types
- Rich narrative composition with embedded pins and media
- Guided playback system with automatic navigation
- Multiple export formats (PDF, HTML, data packages)
- Sharing and access control system
- Professional presentation and documentation capabilities

**What's Next:**
Phase 9 will implement **Performance & Polish** - the final optimization and quality assurance phase. This includes:
- Web Workers for heavy computational tasks
- Accessibility compliance and testing
- Mobile responsiveness and touch interactions
- Performance monitoring and optimization
- Error boundary and recovery systems
- Production deployment preparation

**Key Integration Points for Phase 9:**
- All visualization components need performance profiling
- Export systems need optimization for large walkthroughs
- Playback system needs smooth animation optimization
- Sharing system needs security hardening

**Final Architecture Requirements:**
- Bundle optimization and code splitting
- Performance monitoring integration
- Error logging and diagnostics
- Browser compatibility testing
- Load testing and capacity planning

**Polish Requirements for Phase 9:**
- Consistent interaction patterns across all components
- Professional visual design and micro-interactions
- Comprehensive keyboard accessibility
- Mobile and tablet optimization
- Production-ready error handling and recovery
