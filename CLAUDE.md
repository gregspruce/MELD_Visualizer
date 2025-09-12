# CLAUDE.md - Universal Standing Instructions

This document contains universal standing instructions for AI assistants working on any software project. These instructions are project-agnostic and can be applied across different codebases.

---

## 🔴 EXPLICIT STANDING INSTRUCTIONS (Required)

These instructions MUST be followed when working on any software project:

### 1. Tool & Agent Awareness
- **STAY AWARE** of all available subagents at all times
- **PROACTIVELY USE** relevant subagents without being asked when appropriate
- **STAY AWARE** of all available MCPs (Model Context Protocols)
- **PROACTIVELY USE** relevant MCPs when they can improve task completion
- **MANDATORY USE** of mcp__sequentialthinking__sequentialthinking for complex planning and analysis
- **VERIFY CLAUDE.md COMPLIANCE** regularly using compliance-auditor agent
- **INTEGRATE** TodoWrite tool for continuous progress tracking on multi-step tasks

### 2. Code Organization & Quality
- **KEEP** repository structure logical, organized, and neat
- **ENSURE** all code includes useful and understandable comments for both humans and AI
  - Comments should explain WHY, not just WHAT
  - Complex logic should be thoroughly documented
  - API interactions should include example requests/responses in comments
- **ENFORCE** file and script naming conventions that are concise but understandable
  - Use descriptive names that clearly indicate purpose and functionality
  - Employ sequential naming (01_, 02_, 03_) for workflow scripts when appropriate
  - Avoid ambiguous or overly abbreviated names that require context to understand
- **REMOVE** scripts or documentation files that are replaced by newer versions
  - Maintain an explicit log file detailing what files are removed
  - Document commit/branch/repo information for recovery if needed
  - Preserve removal context for later human/AI understanding
- **PERIODICALLY RE-EVALUATE** repository structure and imports using appropriate subagents
  - Use code-reviewer and architect-reviewer agents to assess organization
  - Identify redundant functionality and consolidation opportunities
  - Ensure logical grouping and clear dependency relationships

### 3. Project Management
- **MAINTAIN** a running CHANGELOG.md file
  - Update with every significant change
  - Follow [Keep a Changelog](https://keepachangelog.com/) format
- **MAINTAIN** a running TODO.md list
  - Update immediately when items are completed
  - Add new items as they are discovered
  - Include priority levels and deadlines when known

### 4. Code Excellence Standard
- **ALWAYS AIM** for code and implementations that, in retrospect, are the ONLY solution any expert would arrive at
  - This means choosing the most elegant, efficient, and maintainable approach
  - Avoid clever tricks in favor of clear, obvious solutions
  - The code should feel inevitable, not arbitrary

### 5. Documentation Requirements
- **MAINTAIN** updated documentation for both users and developers
- **ENSURE EXPERT & NOVICE ACCESSIBILITY** in all documentation and project structure
  - **Expert Recognition**: Structures must be immediately recognizable as high-quality by experienced developers
  - **Novice Navigation**: Organization must be intuitive enough for novices to logically find what they need
  - **Documentation Consolidation**: Reduce file count while maintaining logical separation - prefer multiple well-organized files over one unwieldy document
- **ASSUME** later users and developers may be of ANY skill level
  - Include basic setup instructions with clear entry points
  - Provide advanced configuration options with expert-level depth
  - Add troubleshooting guides with progressive complexity
  - Include code examples for common use cases with context
- **UPDATE** scripts and documentation for ALL changes, especially when approaches change
  - When libraries/frameworks are replaced due to insufficiency, remove old references from active docs
  - References to deprecated approaches should only remain in changelogs and history documents
  - User guides, APIs, and README files must reflect current/working approaches only
  - Maintain "Last Updated" entries in all documentation files
  - Add changelog summaries to track approach evolution and reasoning

### 6. Code Compatibility
- **AVOID** using unicode symbols in code and scripts where they will cause logic or visual errors
  - Verify any unicode that is still used will not cause any errors before reporting success

### 7. Performance Priority
- **PRIORITIZE** efficiency in both code execution and application resource usage
  - Minimize API calls
  - Implement caching where appropriate
  - Use async operations for I/O bound tasks
  - Profile and optimize bottlenecks

### 8. Safety First Principle
- **INTERACTIONS** with production systems CANNOT break existing functionalities without explicit confirmation
  - Always test in a safe environment first
  - Provide rollback instructions
  - Document any breaking changes clearly
  - Request explicit user confirmation before implementing breaking changes
- **COMPREHENSIVE REFERENCE DEPENDENCY MAPPING** before any structural changes
  - Map all file references, imports, and cross-dependencies
  - Identify script-to-file references and hard-coded paths
  - Create dependency matrix showing what references what
  - Assess change impact with risk categorization (Critical/High/Medium/Low)
  - Define testing procedures and rollback plans for each proposed change
- **CHECKPOINT SYSTEMS** for safe operation
  - Create state snapshots before high-risk operations
  - Implement validation checkpoints after each major change
  - Maintain rollback capability at every step
  - Document all changes for recovery purposes

### 9. Ultrathink Planning & Sequential Reasoning
- **MANDATORY** use of mcp__sequentialthinking__sequentialthinking for complex tasks and analysis
- **DEEP PLANNING** required before execution of multi-step processes
  - Break down complex problems into comprehensive step-by-step approaches
  - Consider multiple solution paths and their trade-offs
  - Document reasoning chains and decision points
  - Identify potential risks and mitigation strategies
  - Plan optimal execution sequences
- **HYPOTHESIS GENERATION AND VERIFICATION** methodology
  - Form clear hypotheses about solutions and approaches
  - Test hypotheses systematically with validation steps
  - Iterate and refine based on findings
  - Document learning and insights for future application
- **CONTEXT PRESERVATION** throughout reasoning process
  - Maintain awareness of original goals and constraints
  - Connect insights across different analysis phases
  - Preserve decision rationale for future reference

### 10. Multi-Phase Progress Management
- **MANDATORY TodoWrite INTEGRATION** for all non-trivial tasks
- **CONTINUOUS PROGRESS TRACKING** with real-time updates
  - Mark tasks as in_progress before beginning work
  - Update status immediately upon completion
  - Maintain exactly ONE task in_progress at any time
  - Document progress with specific accomplishments and outcomes
- **PHASE-BASED EXECUTION** for complex projects
  - Break large tasks into distinct phases with clear deliverables
  - Implement validation checkpoints between phases
  - Allow for iterative refinement based on phase outcomes
  - Maintain progress visibility throughout entire process
- **RESILIENCE PLANNING** for long-running processes
  - Create recovery checkpoints for system interruption scenarios
  - Use project-state-save.md tool proactively during extended work
  - Document intermediate findings and decision points
  - Prepare continuation strategies for workflow resumption

### 11. Recovery & Resilience Systems
- **PROACTIVE STATE PERSISTENCE** for mission-critical work
  - Use /tools project-state-save regularly during long processes
  - Capture original user prompts and intent preservation
  - Document mental models and reasoning chains
  - Save multi-agent coordination context and findings
- **COMPREHENSIVE RESTORATION CAPABILITY**
  - Use /tools project-state-restore after any interruption
  - Validate restored context matches pre-interruption state
  - Verify all critical knowledge and insights are preserved
  - Confirm immediate next steps are clear and actionable
- **CHECKPOINT RECOVERY PROTOCOLS**
  - Maintain multiple backup locations for state files
  - Create human-readable recovery summaries
  - Implement validation steps to ensure successful restoration
  - Document any knowledge gaps identified during recovery
- **INTERRUPTION-RESISTANT WORKFLOWS**
  - Design processes that can be safely paused and resumed
  - Maintain detailed audit trails for all significant actions
  - Prepare rollback procedures for incomplete operations
  - Test recovery mechanisms during development phases

### 12. Comprehensive Safety Protocols
- **FUNCTIONALITY PRESERVATION IS PARAMOUNT** - no changes without explicit confirmation if breaking
- **DEPENDENCY ANALYSIS** required before structural modifications
  - Complete reference mapping across all project files
  - Impact assessment for proposed changes with risk categorization
  - Validation procedures for each change group
  - Rollback procedures tested and documented
- **CHANGE SEQUENCING** for safe implementation
  - Low-risk changes implemented first
  - Medium and high-risk changes with comprehensive testing
  - Reference updates performed in dependency order
  - Functionality verification after each change group
- **VALIDATION PROTOCOLS** throughout modification process
  - Critical path testing after structural changes
  - Cross-reference verification for renamed files/folders
  - Configuration consistency checks
  - User confirmation for any breaking modifications
- **EMERGENCY PROCEDURES** for failed operations
  - Immediate rollback capability at every step
  - State restoration from most recent checkpoint
  - Damage assessment and repair procedures
  - Lessons learned documentation for prevention

### 13. Engineering Excellence & Strategic Problem-Solving
- **STRATEGIC CONFIDENCE** - commit to optimal solutions and fix them rather than fallback
  - Avoid suboptimal fallbacks - be confident and competent in the chosen strategy
  - Fix the optimal strategy rather than reverting to inferior approaches
  - Challenge suboptimal patterns when encountered - don't accept mediocrity
  - Maintain conviction in well-reasoned technical decisions
- **ROOT CAUSE ANALYSIS** - solve fundamental problems, not surface symptoms
  - Identify root cause, not symptoms - dig deeper for true understanding
  - Conduct additional research where needed to fully understand problem domains
  - Question assumptions and verify underlying causes before implementing fixes
  - Document root cause analysis for future reference and learning
- **SOLUTION OPTIMIZATION** - leverage existing solutions intelligently while avoiding forced fits
  - Don't reinvent the wheel - if a solution exists, utilize and modify for specific use case
  - However, do NOT force inappropriate solutions (square peg into round hole approach)
  - If a new solution is demonstrably better or more efficient, create it
  - Use industry best practices as foundation, adapting intelligently to context
  - Research established patterns before implementing custom solutions
- **PROFESSIONAL EXCELLENCE STANDARDS** - maintain high standards with transparent communication
  - Do not be a yes-man - provide honest assessments of approaches and trade-offs
  - Proactively use agents, tools, and workflows without being asked when appropriate
  - Solutions must be Simple, streamlined, with no redundancy and 100% complete (not 99%)
  - Present best solution with trade-offs clearly explained
  - Remember user requirements and ask for input before significant changes to strategy
  - Maintain professional integrity while being collaborative and responsive

---

## 🔵 SUGGESTED BEST PRACTICES (Recommended)

These practices are suggested to enhance project quality and maintainability:

### Development Workflow
1. **Test-Driven Development**
   - Write tests before implementing features
   - Maintain >80% code coverage
   - Include integration tests for component interactions
   - Test edge cases and error conditions

2. **Version Control Hygiene**
   - Use semantic versioning (MAJOR.MINOR.PATCH)
   - Write clear, descriptive commit messages
   - Create feature branches for significant changes
   - Squash commits before merging to main
   - Tag releases appropriately

3. **Error Handling**
   - Implement comprehensive error handling
   - Provide meaningful error messages to users
   - Log errors appropriately (don't expose sensitive data)
   - Include recovery mechanisms where possible
   - Use proper exception hierarchies

4. **Security Considerations**
   - Never commit secrets or API keys
   - Use environment variables for sensitive configuration
   - Validate all user inputs
   - Implement rate limiting for API calls
   - Follow OWASP security guidelines
   - Regular security audits and dependency updates

5. **Code Style**
   - Follow language-specific style guides (PEP 8 for Python, etc.)
   - Use type hints/annotations where available
   - Implement docstrings/JSDoc for all public APIs
   - Keep functions small and focused (Single Responsibility Principle)
   - Use meaningful variable and function names

6. **Performance Monitoring**
   - Log performance metrics
   - Implement timeout handling for external calls
   - Use connection pooling for database/API connections
   - Implement circuit breakers for external services
   - Profile code to identify bottlenecks
   - Cache expensive computations

7. **User Experience**
   - Provide clear setup instructions in README.md
   - Include configuration examples
   - Implement helpful default values
   - Provide migration guides for breaking changes
   - Include a FAQ section for common issues
   - Maintain comprehensive documentation

8. **Continuous Improvement**
   - Regularly update dependencies
   - Monitor for security vulnerabilities
   - Refactor code when patterns emerge
   - Seek feedback from users
   - Keep up with framework/library updates
   - Regular code reviews

9. **AI-Specific Considerations**
   - Structure code to be easily understood by future AI assistants
   - Include context about design decisions
   - Document any non-obvious architectural choices
   - Maintain a glossary of project-specific terms
   - Use clear, consistent naming conventions

10. **Collaboration Best Practices**
    - Write self-documenting code
    - Maintain up-to-date documentation
    - Use issue templates for bug reports and feature requests
    - Implement PR templates with checklists
    - Document architectural decisions (ADRs)
    - Maintain a contribution guide

---

## 📋 Universal Development Principles

### SOLID Principles
- **Single Responsibility**: Each module/class should have one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes must be substitutable for base types
- **Interface Segregation**: Depend on abstractions, not concretions
- **Dependency Inversion**: High-level modules shouldn't depend on low-level modules

### DRY (Don't Repeat Yourself)
- Extract common functionality into reusable components
- Use configuration files for values that might change
- Create utility functions for repeated operations
- Maintain single sources of truth

### KISS (Keep It Simple, Stupid)
- Favor simple solutions over complex ones
- Write code that is easy to understand
- Avoid premature optimization
- Remove unnecessary complexity

### YAGNI (You Aren't Gonna Need It)
- Don't add functionality until it's needed
- Avoid speculative generality
- Focus on current requirements
- Refactor when patterns emerge

### Boy Scout Rule
- Leave the code better than you found it
- Fix broken windows (small issues) immediately
- Refactor as you go
- Update documentation when you change code

---

## 🔧 Universal Troubleshooting Approach

### Debugging Strategy
1. **Reproduce the issue** - Ensure you can consistently reproduce the problem
2. **Isolate the problem** - Narrow down to the smallest failing case
3. **Form hypotheses** - Think about what could cause the issue
4. **Test systematically** - Test one hypothesis at a time
5. **Document the fix** - Record what caused the issue and how it was fixed

### Common Debugging Techniques
- Use debugger tools and breakpoints
- Add strategic logging statements
- Use binary search to find issues
- Check recent changes (git bisect)
- Verify assumptions with assertions
- Test in isolation (unit tests)
- Check external dependencies
- Review error messages carefully

### Performance Optimization
1. **Measure first** - Profile before optimizing
2. **Identify bottlenecks** - Find the actual slow parts
3. **Optimize algorithms** - Better algorithms beat micro-optimizations
4. **Cache appropriately** - Store expensive computations
5. **Batch operations** - Reduce round trips
6. **Use appropriate data structures** - Choose the right tool for the job
7. **Monitor in production** - Real-world performance matters

---

## 🔄 Update History

- **2025-08-30**: Enhanced with advanced project methodology strategies
  - Added Ultrathink Planning & Sequential Reasoning (mandatory mcp__sequentialthinking__sequentialthinking)
  - Added Multi-Phase Progress Management (mandatory TodoWrite integration)
  - Added Recovery & Resilience Systems (project-state-save/restore tools)
  - Added Comprehensive Safety Protocols (dependency mapping, change sequencing)
  - Added Engineering Excellence & Strategic Problem-Solving (strategic confidence, root cause analysis)
  - Enhanced Tool & Agent Awareness with CLAUDE.md compliance verification
  - Enhanced Documentation Requirements with Expert & Novice Accessibility principles
  - Enhanced Safety First Principle with comprehensive reference dependency mapping
- **2025-08-25**: Created general CLAUDE.md from project-specific instructions

---

## 📝 Notes for AI Assistants

When working on any project:
1. Check for project-specific CLAUDE.md or similar documentation
2. Read README.md to understand the project
3. Review recent commits to understand current work
4. Check for TODO.md or issue tracker for pending tasks
5. Ensure all changes align with standing instructions
6. Update documentation immediately after code changes
7. Test thoroughly before committing
8. Ask for clarification if instructions conflict

### Priority Order for Instructions
1. **Project-specific CLAUDE.md** (highest priority)
2. **This general CLAUDE.md**
3. **Project README and documentation**
4. **Framework/library best practices**
5. **General programming principles** (lowest priority)

Remember: The goal is to create code that is not just functional, but exemplary - the kind of solution that makes other developers say "Of course, that's exactly how it should be done."

### Working with Different Technology Stacks

#### For Python Projects
- Follow PEP 8 style guide
- Use type hints for function signatures
- Prefer pathlib over os.path
- Use context managers for resource handling
- Virtual environments for dependency isolation

#### For JavaScript/TypeScript Projects
- Follow ESLint/Prettier configurations
- Use modern ES6+ features appropriately
- Implement proper error boundaries
- Handle promises and async/await properly
- Consider bundle size and performance

#### For Web Applications
- Ensure accessibility (WCAG compliance)
- Implement responsive design
- Optimize for performance (Core Web Vitals)
- Consider SEO requirements
- Implement proper security headers

#### For APIs
- Follow RESTful principles or GraphQL best practices
- Implement proper authentication/authorization
- Version APIs appropriately
- Document with OpenAPI/Swagger
- Implement rate limiting and pagination

#### For Databases
- Use migrations for schema changes
- Implement proper indexing
- Avoid N+1 query problems
- Use transactions appropriately
- Regular backups and monitoring

---

## 🌟 Excellence Indicators

Your code should exhibit these qualities:

### Readability
- Code reads like well-written prose
- Intent is immediately clear
- Naming is self-documenting
- Structure is logical and intuitive

### Maintainability
- Easy to modify and extend
- Well-organized and modular
- Properly abstracted
- Minimal technical debt

### Reliability
- Comprehensive error handling
- Robust testing coverage
- Predictable behavior
- Graceful degradation

### Performance
- Efficient algorithms
- Optimized for common cases
- Appropriate caching
- Minimal resource usage

### Security
- Input validation
- Proper authentication
- Secure data handling
- Regular updates

---

This document serves as a foundation for excellence in software development, regardless of the specific project or technology stack.
