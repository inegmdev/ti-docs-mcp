# ti-docs-mcp Constitution

## Core Principles

### I. MCP Protocol Compliance
- Strict adherence to Model Context Protocol specification
- Use official MCP schemas and message formats
- Handle protocol errors gracefully with appropriate error codes
- Support all required message types for tools and resources
- Validate all inputs and outputs against schemas
- **Non-negotiable for:** Any public-facing API or tool interface

### II. Error-First Design
- Errors are first-class citizens with structured responses
- Every tool/resource has defined error cases and codes
- Clients receive actionable feedback (never generic "unknown error")
- Error responses include: error code, message, and optional details
- All error paths are tested

### III. Resource Safety & Cleanup
- No resource leaks (connections, files, handles)
- Clean shutdown guaranteed on termination signals
- Proper timeout handling for all I/O operations
- Connection pooling with configured limits
- All async operations have cancellation support

### IV. Tool-First Modularity
- Each tool is independent, testable, and self-contained
- Tools don't share mutable state (read-only context is acceptable)
- Each tool has its own input validation
- Tools can be added/removed without breaking others
- Tool contracts are versioned

### V. Input Validation (NON-NEGOTIABLE)
- All external inputs validated before processing
- Never trust client input
- Schema validation on all requests
- Fail fast with clear error messages
- Sanitize all inputs before processing

## Compatibility

### GLM 4.7 Support
- Must work with Zai/GLM-4.7 model
- Tool outputs compatible with GLM 4.7 token limits and formats
- Error messages clear enough for GLM 4.7 to provide useful feedback

### Transport Layer
- Support stdio transport (required by MCP spec)
- Support HTTP/SSE transport (optional, for web clients)
- Graceful degradation when transport is unavailable

### Protocol Versioning
- Track MCP protocol version in all messages
- Support backwards compatibility for minor versions
- Clear deprecation path for breaking changes

## Performance Standards

### Latency Targets
- Simple tools: <500ms response time (P95)
- Complex tools: <2s response time (P95)
- Streaming tools: First chunk within 200ms

### Concurrency
- Support at least 10 concurrent requests
- No global locks that block unrelated requests
- Thread-safe tool execution

### Streaming
- Support streaming responses for long-running operations
- Provide progress updates where applicable
- Cancellation support for streaming operations

## Security

### Authentication
- No authentication required for local stdio transport
- If HTTP transport is added, support optional API key authentication
- Secure storage of credentials (never log or expose in errors)

### Sandboxing
- Tools execute in controlled environment
- File system access limited to approved directories
- No arbitrary code execution tools

### Rate Limiting
- Protect against abuse and resource exhaustion
- Per-client and global rate limits
- Rate limit errors communicated clearly

## Testing Philosophy

### Unit Tests
- Every tool function covered by unit tests
- All error paths tested
- Mock external dependencies
- >80% code coverage required for core logic

### Integration Tests
- Full MCP message flow tested
- Test with real MCP client implementations
- Test both stdio and HTTP transports (if implemented)
- Test error scenarios and recovery

### Mock Clients
- Use mock MCP clients for testing
- Test against protocol edge cases
- Validate JSON schema compliance

## Documentation Standards

### Tool Schemas
- Auto-generate schemas from tool definitions
- Publish schemas in standard format (JSON Schema)
- Document all parameters, return types, and errors

### Examples
- Usage examples for every tool
- Show both success and error responses
- Examples in multiple languages if applicable

### Change Management
- Maintain CHANGELOG for all versions
- Document breaking changes prominently
- Migration guides for major version upgrades

## Observability

### Logging
- Structured logs (JSON format preferred)
- Log levels: DEBUG, INFO, WARN, ERROR
- Never log sensitive data (API keys, user content)
- Log all tool invocations with timing

### Metrics
- Track request latency (P50, P95, P99)
- Track error rates by tool
- Track concurrent request count
- Track transport-level metrics (connectivity, throughput)

### Debug Mode
- Verbose mode for troubleshooting
- Detailed logging without exposing sensitive data
- Protocol-level debugging (message dumps, sanitized)

## Development Workflow

### TDD Cycle
- Tests written before implementation
- All tests must fail initially (red)
- Implement to make tests pass (green)
- Refactor without breaking tests

### Code Review
- All changes require review
- Review checklist: protocol compliance, error handling, tests
- One approval required for core changes, two for protocol changes

### Continuous Integration
- All tests must pass before merge
- Static analysis (linting, type checking)
- Integration tests run on every PR

## Governance

### Amendment Process
- Constitution supersedes all other practices
- Amendments require documentation in CHANGELOG
- Breaking changes require migration plan and team approval
- Minor clarifications can be made with single approval

### Runtime Guidance
- Use this constitution as the primary decision framework
- When in doubt, prioritize: Protocol Compliance > Safety > Usability
- Document any exceptions with rationale

---

**Version:** 1.0.0 | **Ratified:** 2026-02-11 | **Last Amended:** 2026-02-11
