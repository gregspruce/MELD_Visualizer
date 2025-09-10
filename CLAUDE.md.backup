# Claude Standing Instructions for HA_Claude_Integration Project

This document contains standing instructions for AI assistants working on the Home Assistant Claude Integration project. Instructions are separated into explicit requirements and suggested best practices.

---

## 🔴 EXPLICIT STANDING INSTRUCTIONS (Required)

These instructions have been explicitly stated by the project owner and MUST be followed:

### 1. Tool & Agent Awareness
- **STAY AWARE** of all available subagents at all times
- **PROACTIVELY USE** relevant subagents without being asked when appropriate
- **STAY AWARE** of all available MCPs (Model Context Protocols)
- **PROACTIVELY USE** relevant MCPs when they can improve task completion

### 2. Code Organization & Quality
- **KEEP** repository structure logical, organized, and neat
- **ENSURE** all code includes useful and understandable comments for both humans and AI
  - Comments should explain WHY, not just WHAT
  - Complex logic should be thoroughly documented
  - API interactions should include example requests/responses in comments

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
- **ASSUME** later users and developers may be of ANY skill level
  - Include basic setup instructions
  - Provide advanced configuration options
  - Add troubleshooting guides
  - Include code examples for common use cases

### 6. Home Assistant Integration Safety
- **INTERACTIONS** with Home Assistant CANNOT break existing functionalities without explicit confirmation
  - Always test in a safe environment first
  - Provide rollback instructions
  - Document any breaking changes clearly
  - Request explicit user confirmation before implementing breaking changes

### 7. Performance Priority
- **PRIORITIZE** efficiency in both code execution and application resource usage
  - Minimize API calls
  - Implement caching where appropriate
  - Use async operations for I/O bound tasks
  - Profile and optimize bottlenecks

---

## 🔵 SUGGESTED BEST PRACTICES (Recommended)

These practices are suggested to enhance project quality and maintainability:

### Development Workflow
1. **Test-Driven Development**
   - Write tests before implementing features
   - Maintain >80% code coverage
   - Include integration tests for Home Assistant interactions

2. **Version Control Hygiene**
   - Use semantic versioning (MAJOR.MINOR.PATCH)
   - Write clear, descriptive commit messages
   - Create feature branches for significant changes
   - Squash commits before merging to main

3. **Error Handling**
   - Implement comprehensive error handling
   - Provide meaningful error messages to users
   - Log errors appropriately (don't expose sensitive data)
   - Include recovery mechanisms where possible

4. **Security Considerations**
   - Never commit secrets or API keys
   - Use environment variables for sensitive configuration
   - Validate all user inputs
   - Implement rate limiting for API calls
   - Follow OWASP security guidelines

5. **Code Style**
   - Follow PEP 8 for Python code
   - Use type hints for all function signatures
   - Implement docstrings for all classes and functions
   - Keep functions small and focused (Single Responsibility Principle)

6. **Home Assistant Specific**
   - Follow Home Assistant development guidelines
   - Use the latest Home Assistant APIs
   - Implement proper entity naming conventions
   - Support Home Assistant's configuration validation
   - Include device_class and unit_of_measurement where applicable

7. **Performance Monitoring**
   - Log performance metrics
   - Implement timeout handling for external calls
   - Use connection pooling for database/API connections
   - Implement circuit breakers for external services

8. **User Experience**
   - Provide clear setup instructions in README.md
   - Include configuration examples
   - Implement helpful default values
   - Provide migration guides for breaking changes
   - Include a FAQ section for common issues

9. **Continuous Improvement**
   - Regularly update dependencies
   - Monitor for security vulnerabilities
   - Refactor code when patterns emerge
   - Seek feedback from users
   - Keep up with Home Assistant updates

10. **AI-Specific Considerations**
    - Structure code to be easily understood by future AI assistants
    - Include context about design decisions
    - Document any non-obvious architectural choices
    - Maintain a glossary of project-specific terms

---

## 📋 Project-Specific Context

### Project Goals
- Create a seamless integration between Claude AI and Home Assistant
- Enable natural language control of home automation
- Provide intelligent automation suggestions
- Maintain privacy and local control where possible

### Key Components
- `claude_ha_bridge.py`: Main bridge between Claude and Home Assistant
- `ha_native_claude_integration.yaml`: Home Assistant configuration examples
- `claude_code_ha_setup.md`: Setup and configuration documentation

### Technology Stack
- Python 3.9+ (Home Assistant requirement)
- Home Assistant Core
- Claude API (Anthropic)
- Async/await patterns for non-blocking operations

### Location & Timezone
- **User Location**: DFW (Dallas-Fort Worth), Texas, USA
- **Timezone**: CST/CDT (UTC-6/UTC-5)
- All timestamps and scheduling should account for Central Time

### Testing Requirements
- Unit tests for all core functions
- Integration tests for Home Assistant interactions
- Mock external API calls in tests
- Test error conditions and edge cases

---

## 🔄 Update History

- **2025-08-23**: Initial CLAUDE.md created with explicit and suggested instructions

---

## 📝 Notes for AI Assistants

When working on this project:
1. Always read this file first when starting a new session
2. Check TODO.md for pending tasks
3. Review CHANGELOG.md for recent changes
4. Ensure all changes align with these standing instructions
5. Update documentation immediately after code changes
6. Test thoroughly before committing
7. Ask for clarification if instructions conflict

Remember: The goal is to create code that is not just functional, but exemplary - the kind of solution that makes other developers say "Of course, that's exactly how it should be done."