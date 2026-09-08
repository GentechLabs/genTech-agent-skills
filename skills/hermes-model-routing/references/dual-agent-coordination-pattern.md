# Dual-Agent Coordination Pattern

## 🎯 Overview
Advanced model routing for dual-agent workflows between Gentech (VPS) and Forge (Desktop). Optimizes for cost, quality, and availability.

## 🤖 Agent Roles

### Gentech (VPS) - 24/7 Operations
**Responsibilities:**
- Cron job execution and monitoring
- Simple automation and repetitive tasks
- Health checks and status reporting
- Night-time heavy analysis (1-5 AM ET off-peak)

**Model Strategy:**
- **Simple Tasks**: Z.AI GLM-4.5 Flash (existing layer)
- **Complex Tasks**: Z.AI GLM-5.2 (heavy analysis/audits)
- **Peak Hours**: Avoid 1-5 AM ET (Z.AI 3x cost)

### Forge (Desktop) - Home Operations
**Responsibilities:**  
- Complex coding and development tasks
- Quality review and debugging
- Strategic planning and creative work
- Real-time collaboration during home hours

**Model Strategy:**
- **Primary**: DeepSeek Flash (5M free tokens) - general tasks
- **Heavy**: GLM 5.2 - coding/complex analysis
- **Context**: 128K+ window required for Hermes compatibility

## 📅 Weekly Scheduling System

### Input Format
Jordan provides weekly schedule:
```
Weekly Schedule - [Week Start Date]
-----------------------------------------
Monday: Work 9-5, Home ~5:30, Forge available 5:30-10
Tuesday: Work 9-5, Home ~5:30, Forge available 5:30-10  
Wednesday: Work 9-5, Home ~5:30, Forge available 5:30-10
Thursday: Work 9-5, Home ~5:30, Forge available 5:30-10
Friday: Work 9-5, Home ~5:30, Forge available 5:30-12
Saturday: Flexible, Forge available as needed
Sunday: Flexible, Forge available as needed
```

### Task Distribution Rules
**High Priority (Forge Available)**:
- Complex coding tasks
- Code reviews & debugging  
- Strategic planning sessions
- Quality assurance & testing
- Creative content production

**Medium Priority (Gentech Execution)**:
- Simple automation scripts
- Data processing & analysis
- Monitoring & alerting
- Documentation updates
- Research & synthesis

**Low Priority (Queue for Next Session)**:
- Experimental features
- Non-critical optimizations
- Long-term research projects
- Optional enhancements

## 🔄 Handoff Protocol

### Daily Handoff (4:30 PM)
1. Gentech reviews completed tasks
2. Prioritizes Forge-available work
3. Prepares handoff summary
4. Updates working memory

### Forge Activation (5:30 PM)  
1. Gentech provides prioritized task list
2. Forge executes complex coding tasks
3. Real-time collaboration as needed
4. End-of-session coordination

## 🧠 Memory Management

### Session Handoff Protocol
**Trigger**: Memory ≥95% capacity
**Process**:
1. Archive critical data to vault/session-archives/YYYY-MM/
2. Sync to GitHub when available
3. Clear memory entries (78% capacity target)
4. Preserve core identity/infrastructure facts

### Vault Integration Points
- **Session Archives**: `11-Mess Hall/session-archives/YYYY-MM/`
- **System State**: `00-HQ/system-state/`
- **Context Bridge**: `09-Green Room/context-bridge/`
- **Memory Protocol**: `09-Green Room/memory-cleanup-protocol.md`

## 📊 Performance Metrics

### Success Indicators
- Task completion rate per session
- Context switching efficiency
- Quality of Forge-produced work
- Cost optimization effectiveness
- Memory usage stability

### Weekly Review
- Schedule adherence tracking
- Task distribution optimization
- Performance benchmarking
- Next week planning

---

*Created: June 29, 2026*
*Status: Implementation Phase*