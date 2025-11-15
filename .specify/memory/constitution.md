# Splitfool Project Constitution

**Version**: 1.0.0  
**Last Updated**: November 15, 2025

## Preamble

### Purpose
This constitution establishes the foundational principles, standards, and governance framework for the Splitfool project. It serves as a binding agreement for all technical decisions, implementations, and contributions to ensure consistent quality, maintainability, and user experience across the entire codebase.

### Scope
These principles apply to:
- All source code, documentation, and configuration files
- All development workflows and processes
- All integrations and external dependencies
- All MCP (Model Context Protocol) server implementations
- All testing and deployment procedures

### Authority
This constitution has binding authority over all technical decisions. Deviations require explicit documentation and approval through the governance process outlined in Section VII.

---

## I. Code Quality Principles

### 1.1 Readability First
**Principle**: Code must be written for human comprehension first, machine execution second.

**Requirements**:
- Use descriptive, intention-revealing names for all variables, functions, classes, and modules
- Maintain consistent naming conventions throughout the project (snake_case for Python)
- Keep functions focused on a single responsibility (max 50 lines recommended)
- Avoid deep nesting (max 3 levels)
- Use whitespace and formatting to enhance readability

**Rationale**: Code is read far more often than it is written. Readable code reduces cognitive load, accelerates onboarding, and minimizes bugs.

### 1.2 Type Safety and Annotations
**Principle**: All Python code must use type hints comprehensively.

**Requirements**:
- All function signatures must include type hints for parameters and return values
- Use `typing` module constructs (Union, Optional, List, Dict, etc.) appropriately
- Enable strict type checking in development tools (mypy with `--strict` mode)
- Document complex type definitions with inline comments
- Never use `Any` type without explicit justification

**Rationale**: Type hints catch bugs at development time, improve IDE support, and serve as inline documentation.

### 1.3 Documentation Standards
**Principle**: Every public interface must have comprehensive documentation.

**Requirements**:
- All modules must have module-level docstrings explaining purpose and usage
- All public functions/methods must have docstrings following the Google style guide
- Include parameter descriptions, return value descriptions, and raised exceptions
- Complex algorithms must have inline comments explaining the approach
- Maintain up-to-date README.md files in all packages

**Example**:
```python
def calculate_split(
    total: Decimal, 
    participants: list[str], 
    custom_weights: dict[str, float] | None = None
) -> dict[str, Decimal]:
    """Calculate how to split an expense among participants.
    
    Args:
        total: The total amount to split
        participants: List of participant identifiers
        custom_weights: Optional weights for unequal splitting
        
    Returns:
        Dictionary mapping participant IDs to their share amounts
        
    Raises:
        ValueError: If total is negative or participants list is empty
    """
```

### 1.4 Error Handling
**Principle**: All error conditions must be explicitly handled with appropriate recovery strategies.

**Requirements**:
- Never use bare `except:` clauses
- Create custom exception classes for domain-specific errors
- Log all exceptions with contextual information
- Provide meaningful error messages to users
- Use context managers for resource cleanup
- Implement retry logic with exponential backoff for transient failures

### 1.5 Dependency Management
**Principle**: Dependencies must be carefully evaluated, minimized, and pinned.

**Requirements**:
- All dependencies must be declared in `pyproject.toml`
- Pin dependency versions for reproducible builds
- Review security advisories for all dependencies monthly
- Document rationale for each major dependency
- Prefer standard library solutions when performance is acceptable
- Maximum dependency tree depth of 4 levels

### 1.6 Code Organization
**Principle**: Code must be organized in a logical, modular structure.

**Requirements**:
- Follow the project's established directory structure
- One class per file for classes > 100 lines
- Group related functionality into modules
- Use `__init__.py` files to expose clean public APIs
- Separate business logic from infrastructure concerns
- Maximum file length: 500 lines

### 1.7 Configuration Management
**Principle**: All configuration must be externalized and environment-specific.

**Requirements**:
- Never hardcode configuration values in source code
- Use environment variables for runtime configuration
- Provide sensible defaults for all configuration values
- Document all configuration options
- Validate configuration at application startup
- Support multiple environment profiles (dev, staging, production)

### 1.8 Security First
**Principle**: Security considerations must be integral to all design and implementation decisions.

**Requirements**:
- Never commit secrets or credentials to version control
- Use parameterized queries for all database operations
- Validate and sanitize all external input
- Implement principle of least privilege for all operations
- Keep dependencies updated with security patches
- Perform security review for all external integrations

### 1.9 Immutability Preference
**Principle**: Prefer immutable data structures and functional approaches where practical.

**Requirements**:
- Use `dataclasses` with `frozen=True` for data models
- Avoid mutable default arguments
- Return new objects rather than modifying in place
- Use `tuple` instead of `list` when collection won't change
- Document any necessary mutability with clear rationale

### 1.10 Code Reuse and DRY
**Principle**: Eliminate duplication through abstraction, but avoid premature abstraction.

**Requirements**:
- Apply the "Rule of Three" - refactor after third duplication
- Extract common functionality into utility modules
- Use inheritance and composition appropriately
- Create reusable patterns for common operations
- Document reusable components for discoverability

---

## II. Testing Standards

### 2.1 Test Coverage Requirements
**Principle**: Maintain high test coverage to ensure code reliability.

**Requirements**:
- Minimum 80% code coverage for all modules
- Minimum 95% coverage for business logic
- 100% coverage for critical paths (payment processing, security)
- Coverage reports generated on every CI run
- Declining coverage blocks merge requests

### 2.2 Test Structure and Organization
**Principle**: Tests must be well-organized, independent, and maintainable.

**Requirements**:
- Mirror source code structure in test directory
- One test file per source file (`test_module.py` for `module.py`)
- Use descriptive test names: `test_<behavior>_when_<condition>_then_<result>`
- Group related tests in test classes
- Use fixtures for common test setup
- Maximum 15 test cases per test file

### 2.3 Test Independence
**Principle**: Each test must be completely independent and repeatable.

**Requirements**:
- Tests must pass in any order
- Use mocks and stubs to isolate units under test
- Clean up all test artifacts (files, database records, etc.)
- No shared state between tests
- Each test should take < 1 second to execute

### 2.4 Test Types
**Principle**: Employ multiple testing strategies for comprehensive coverage.

**Requirements**:
- **Unit Tests**: Test individual functions/classes in isolation (70% of tests)
- **Integration Tests**: Test component interactions (20% of tests)
- **End-to-End Tests**: Test complete user workflows (10% of tests)
- **Property Tests**: Use hypothesis for property-based testing on algorithms
- **Performance Tests**: Benchmark critical paths with pytest-benchmark

### 2.5 Test Data Management
**Principle**: Test data must be realistic, consistent, and maintainable.

**Requirements**:
- Use factories (e.g., factory_boy) for test data generation
- Store complex test data in fixtures directory
- Use realistic data that represents production scenarios
- Never use production data in tests
- Document test data requirements

### 2.6 Assertion Quality
**Principle**: Assertions must be specific and provide clear failure messages.

**Requirements**:
- Use specific assertions (`assertEqual`, `assertIn`) over generic `assertTrue`
- Include custom messages for assertions: `assert x > 0, f"Value must be positive, got {x}"`
- One logical assertion per test method
- Use assertion libraries (assertpy) for complex assertions

### 2.7 Test Automation
**Principle**: All tests must run automatically in CI/CD pipeline.

**Requirements**:
- Tests run on every pull request
- Failed tests block merging
- Flaky tests must be fixed or removed within 24 hours
- Test execution time monitored and optimized
- Test results published with detailed reports

### 2.8 Mocking Standards
**Principle**: Use mocking judiciously to isolate units under test.

**Requirements**:
- Mock external services and APIs
- Mock database connections in unit tests
- Use pytest-mock or unittest.mock consistently
- Verify mock interactions when testing integration points
- Avoid over-mocking - prefer real objects for simple dependencies

---

## III. User Experience Consistency

### 3.1 Error Messages
**Principle**: Error messages must be helpful, consistent, and actionable.

**Requirements**:
- Use consistent error message format: `[ERROR_CODE] Clear description. Suggested action.`
- Never expose stack traces or internal details to end users
- Provide specific guidance on how to resolve the error
- Use consistent terminology across all error messages
- Support error message internationalization

**Example**:
```
[SPLIT_001] Unable to split expense: Total amount must be greater than zero. 
Please enter a valid positive amount and try again.
```

### 3.2 API Design Consistency
**Principle**: All APIs must follow RESTful principles and consistent patterns.

**Requirements**:
- Use standard HTTP methods appropriately (GET, POST, PUT, DELETE)
- Consistent URL structure: `/api/v1/resource/{id}/sub-resource`
- Return consistent JSON response format
- Use HTTP status codes correctly
- Include pagination for list endpoints
- Version all APIs explicitly

**Response Format**:
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "metadata": {
    "timestamp": "2025-11-15T10:30:00Z",
    "request_id": "abc-123"
  }
}
```

### 3.3 CLI Interface Standards
**Principle**: Command-line interfaces must be intuitive and follow Unix conventions.

**Requirements**:
- Use standard flag patterns (`-v/--verbose`, `-h/--help`)
- Provide clear, concise help text for all commands
- Use consistent command structure: `splitfool <resource> <action> [options]`
- Support both interactive and non-interactive modes
- Provide progress indicators for long-running operations
- Return appropriate exit codes (0 for success, non-zero for errors)

### 3.4 Accessibility
**Principle**: All user interfaces must be accessible to users with disabilities.

**Requirements**:
- Support screen readers with proper ARIA labels
- Ensure sufficient color contrast (WCAG AA minimum)
- Provide keyboard navigation for all functionality
- Include alternative text for all visual elements
- Support browser zoom up to 200%
- Test with accessibility tools (axe, WAVE)

### 3.5 Internationalization
**Principle**: Design for global users from the start.

**Requirements**:
- Externalize all user-facing strings
- Use i18n framework for translations
- Support Unicode (UTF-8) throughout
- Format dates, times, and numbers per locale
- Design UI to accommodate text expansion (30-40%)
- Test with RTL languages

### 3.6 Terminology Consistency
**Principle**: Use consistent terminology throughout the application.

**Requirements**:
- Maintain a project glossary of standard terms
- Use the same term for the same concept everywhere
- Avoid synonyms (e.g., don't mix "user" and "member")
- Document domain-specific terminology
- Review all user-facing text for consistency

---

## IV. Performance Requirements

### 4.1 Response Time Targets
**Principle**: All operations must meet defined response time thresholds.

**Requirements**:
- API endpoints: < 200ms for 95th percentile
- Database queries: < 50ms for simple queries, < 500ms for complex
- Page load time: < 2 seconds for initial load
- CLI commands: < 1 second for simple operations
- Background jobs: Process within defined SLA per job type
- Monitor and alert on performance degradation > 20%

### 4.2 Resource Utilization
**Principle**: Applications must use system resources efficiently.

**Requirements**:
- Memory usage: < 500MB for typical workloads
- CPU usage: < 70% sustained under normal load
- Database connections: Pool and reuse connections
- File handles: Close all file handles promptly
- Network connections: Implement connection pooling
- Monitor resource usage in production

### 4.3 Scalability
**Principle**: Design for horizontal scalability from the start.

**Requirements**:
- Stateless application design (store session state externally)
- Support for multiple concurrent instances
- Database queries optimized with proper indexing
- Implement caching for frequently accessed data
- Use asynchronous processing for heavy workloads
- Load test with 10x expected traffic

### 4.4 Database Performance
**Principle**: Optimize database operations for performance and scalability.

**Requirements**:
- Index all foreign keys and frequently queried columns
- Avoid N+1 query problems (use eager loading)
- Implement query result caching where appropriate
- Use database connection pooling
- Monitor slow query log and optimize queries > 100ms
- Implement pagination for large result sets

### 4.5 Caching Strategy
**Principle**: Implement intelligent caching to reduce latency and load.

**Requirements**:
- Cache frequently accessed, rarely changing data
- Use appropriate TTL values based on data volatility
- Implement cache invalidation strategies
- Use Redis or similar for distributed caching
- Monitor cache hit rates (target > 80%)
- Never cache sensitive or user-specific data without encryption

### 4.6 Asynchronous Processing
**Principle**: Offload long-running tasks to background workers.

**Requirements**:
- Use task queues (Celery, RQ) for async operations
- Provide user feedback for long-running operations
- Implement retry logic with exponential backoff
- Set appropriate timeouts for all operations
- Monitor task queue depth and processing times

### 4.7 Load Testing
**Principle**: Validate performance under realistic load conditions.

**Requirements**:
- Perform load testing before each major release
- Test with 2x expected peak traffic
- Identify and document performance bottlenecks
- Establish performance baselines and track regression
- Use tools like Locust or JMeter for load testing

---

## V. MCP Server Usage Principles

### 5.1 Server Mode Selection
**Principle**: Choose the appropriate MCP server mode based on use case and requirements.

**Requirements**:
- **Single Tool Proxy Mode**: Use when exposing one tool that wraps an entire service
- **Namespace Proxy Mode**: Use for grouping tools by service namespace (storage, keyvault, etc.)
- **Consolidated Proxy Mode**: Use for AI agents requiring optimized, grouped operations
- **All Tools Mode**: Use for development and when exposing every tool individually
- Document mode selection rationale in configuration
- Default to Namespace Proxy Mode for production deployments

**Configuration Example**:
```json
{
  "servers": {
    "splitfool-mcp": {
      "command": "splitfool",
      "args": ["server", "start", "--mode", "namespace"],
      "type": "stdio"
    }
  }
}
```

### 5.2 Transport Type Selection
**Principle**: Select transport type based on deployment context and security requirements.

**Requirements**:
- **StdIO Transport**: Default for local CLI integration and VS Code
- **HTTP Transport**: Use for remote access and microservices architecture
- Implement authentication for HTTP transport (Bearer tokens)
- Use TLS/SSL for all HTTP transport in production
- Document transport selection and security implications
- Monitor transport performance and error rates

### 5.3 Tool Metadata Compliance
**Principle**: All MCP tools must declare accurate metadata for safe operation.

**Requirements**:
- **Destructive**: Set to `true` if tool modifies environment/data
- **Idempotent**: Set to `true` if repeated execution produces same result
- **ReadOnly**: Set to `true` if tool has no side effects
- **OpenWorld**: Set to `true` if tool interacts with external entities
- **Secret**: Set to `true` if tool handles sensitive data
- **LocalRequired**: Set to `true` if tool needs local execution
- Document metadata decisions in code comments

**Example**:
```python
@property
def metadata(self) -> ToolMetadata:
    return ToolMetadata(
        destructive=False,
        idempotent=True,
        read_only=True,
        open_world=False,
        local_required=False,
        secret=False
    )
```

### 5.4 Read-Only Mode Enforcement
**Principle**: Use read-only mode to prevent destructive operations in sensitive environments.

**Requirements**:
- Enable read-only mode in production monitoring contexts
- Filter out all destructive tools when read-only mode is active
- Clearly indicate read-only status in server responses
- Test read-only mode enforcement regularly
- Document which operations are restricted in read-only mode

### 5.5 Command Implementation Standards
**Principle**: All MCP commands must follow consistent implementation patterns.

**Requirements**:
- Inherit from appropriate base command class
- Implement all required methods: `RegisterOptions`, `BindOptions`, `ExecuteAsync`
- Use dependency injection for service dependencies
- Implement comprehensive error handling
- Return standardized `CommandResponse` format
- Include detailed logging at appropriate levels
- Validate all inputs before execution

### 5.6 Service Registration Pattern
**Principle**: Use IAreaSetup interface for modular service registration.

**Requirements**:
- Create an AreaSetup class for each service domain
- Implement `ConfigureServices` for dependency registration
- Implement `RegisterCommands` for command group creation
- Use meaningful namespace and title identifiers
- Register all service implementations as singletons
- Organize commands into logical command groups

**Example**:
```python
class ExpenseSetup(IAreaSetup):
    @property
    def name(self) -> str:
        return "expense"
    
    @property
    def title(self) -> str:
        return "Expense Management"
    
    def configure_services(self, services: ServiceCollection) -> None:
        services.add_singleton(IExpenseService, ExpenseService)
        services.add_singleton(ExpenseCreateCommand)
        services.add_singleton(ExpenseListCommand)
```

### 5.7 Error Handling and Logging
**Principle**: Implement comprehensive error handling and logging for all MCP operations.

**Requirements**:
- Log all command executions with context
- Use structured logging with appropriate log levels
- Handle all exceptions and return meaningful error responses
- Set activity status codes appropriately
- Include request IDs for traceability
- Never expose sensitive data in logs
- Monitor error rates and patterns

### 5.8 Configuration Management
**Principle**: MCP server configuration must be externalized and validated.

**Requirements**:
- Support multiple configuration sources (files, environment, command-line)
- Validate configuration at startup
- Provide clear error messages for configuration issues
- Support environment-specific configurations
- Document all configuration options
- Use secure defaults for all settings

**Configuration File Example**:
```json
{
  "serverMode": "namespace",
  "readOnly": false,
  "enabledServices": ["expense", "participant", "settlement"],
  "logging": {
    "level": "INFO",
    "format": "json"
  },
  "performance": {
    "maxConcurrentRequests": 100,
    "requestTimeout": 30
  }
}
```

### 5.9 Best Practices for Tool Design
**Principle**: Design MCP tools for clarity, safety, and composability.

**Requirements**:
- Keep tool scope focused and single-purpose
- Use clear, descriptive tool names and descriptions
- Provide comprehensive parameter documentation
- Implement input validation with helpful error messages
- Return structured, well-documented responses
- Support idempotent operations where possible
- Design for composition with other tools

### 5.10 Testing MCP Implementations
**Principle**: MCP servers and tools must be thoroughly tested.

**Requirements**:
- Unit test all command implementations
- Integration test server startup and configuration
- Test all transport types independently
- Verify tool metadata accuracy
- Test error handling and edge cases
- Validate read-only mode enforcement
- Load test server under expected usage patterns

---

## VI. Governance Framework

### 6.1 Decision Authority
**Principle**: Technical decisions must be made at appropriate levels with clear authority.

**Levels**:
1. **Routine Decisions**: Individual developer authority (follows established patterns)
2. **Significant Decisions**: Team lead approval required (new patterns, tools, approaches)
3. **Architectural Decisions**: Architecture review board required (fundamental changes)
4. **Constitutional Decisions**: Project stakeholder approval required (principle modifications)

### 6.2 Architecture Review Process
**Principle**: Significant technical decisions require formal review and documentation.

**Requirements**:
- Create Architecture Decision Records (ADRs) for significant decisions
- ADRs must include: context, decision, consequences, alternatives considered
- Store ADRs in `/docs/architecture/decisions/` directory
- Review ADRs in team meetings before implementation
- Re-evaluate ADRs annually or when circumstances change

### 6.3 Code Review Requirements
**Principle**: All code changes must be reviewed before merging.

**Requirements**:
- Minimum one approval from code owner required
- Automated checks must pass (tests, linting, coverage)
- Reviewer must verify adherence to constitution principles
- Complex changes require design review before implementation
- Review turnaround time target: < 24 hours
- Address all review comments or provide rationale

### 6.4 Exception Handling Process
**Principle**: Deviations from constitutional principles require justification and approval.

**Process**:
1. Document the specific principle requiring exception
2. Provide detailed rationale for deviation
3. Describe mitigation strategies for risks
4. Specify duration of exception (temporary or permanent)
5. Obtain approval from architecture review board
6. Document exception in code and architecture documents
7. Review all temporary exceptions quarterly

### 6.5 Continuous Improvement
**Principle**: This constitution is a living document that evolves with the project.

**Requirements**:
- Review constitution quarterly for relevance
- Collect feedback from team on principle effectiveness
- Propose amendments through formal process
- Track adherence metrics and improve problem areas
- Share learnings with the team regularly

### 6.6 Conflict Resolution
**Principle**: Technical disagreements must be resolved constructively and efficiently.

**Process**:
1. Team members attempt to reach consensus through discussion
2. If unresolved, escalate to team lead for mediation
3. Team lead makes decision based on constitution principles
4. If constitutional interpretation unclear, escalate to architecture board
5. Document decision and rationale
6. All parties commit to supporting final decision

### 6.7 Metrics and Monitoring
**Principle**: Track metrics to ensure adherence to constitutional principles.

**Required Metrics**:
- Code coverage percentage
- Test pass rate
- Build success rate
- Code review turnaround time
- Performance metrics (response times, resource usage)
- Technical debt tracking
- Security vulnerability count
- Constitution compliance score

### 6.8 Enforcement
**Principle**: Constitution principles are enforced through automated and manual processes.

**Mechanisms**:
- Automated linting and formatting checks
- Pre-commit hooks for basic validation
- CI/CD pipeline enforcement of test and coverage requirements
- Code review process verification
- Regular architecture reviews
- Periodic constitution compliance audits

---

## VII. Amendment Process

### 7.1 Proposal
Any team member may propose amendments to this constitution by:
1. Creating a detailed amendment proposal document
2. Providing rationale and expected benefits
3. Analyzing impact on existing code and processes
4. Presenting to architecture review board

### 7.2 Review and Approval
Amendment proposals are:
1. Reviewed by architecture board within 2 weeks
2. Discussed in team meeting with all stakeholders
3. Refined based on feedback
4. Voted on by project stakeholders (majority required)
5. Documented with effective date

### 7.3 Implementation
Approved amendments:
1. Are incorporated into this document with version increment
2. Include transition period for compliance (typically 30-90 days)
3. Trigger review of affected code and documentation
4. Are communicated to all team members
5. Are reflected in automated tooling where applicable

### 7.4 Versioning
This constitution follows semantic versioning:
- **Major version**: Fundamental principle changes
- **Minor version**: New principles or significant clarifications
- **Patch version**: Corrections, clarifications, formatting

---

## VIII. Conclusion

This constitution represents our shared commitment to excellence in software development. By adhering to these principles, we ensure that Splitfool remains maintainable, scalable, secure, and user-friendly as it grows and evolves.

Every team member is responsible for:
- Understanding and following these principles
- Raising concerns when principles are unclear or inadequate
- Proposing improvements through the amendment process
- Mentoring others in constitutional compliance
- Leading by example in code quality and professionalism

**Constitution Version**: 1.0.0  
**Effective Date**: November 15, 2025  
**Next Review Date**: February 15, 2026

---

*"Quality is not an act, it is a habit." - Aristotle*
