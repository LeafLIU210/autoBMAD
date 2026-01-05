# Development Guidance

## Implementation Standards
- Follow Ralph's four principles (DRY, KISS, YAGNI, Occam's Razor)
- Write clean, maintainable code
- Include comprehensive tests
- Document all changes

## Code Quality Requirements
- Type hints for all functions
- Docstrings for public APIs
- Unit test coverage > 80%
- No linting errors
- Follow PEP 8 style guidelines

## DRY (Don't Repeat Yourself)
- Extract duplicate logic into reusable functions
- Create shared utilities for common operations
- Use configuration files for constants
- Avoid copy-paste coding

## KISS (Keep It Simple, Stupid)
- Choose the simplest solution that works
- Write self-documenting code
- Avoid premature optimization
- Keep functions small and focused

## YAGNI (You Aren't Gonna Need It)
- Implement only what's required now
- Remove unused code
- Avoid speculative generalization
- Defer future features to future stories

## Occam's Razor
- Prefer simple solutions over complex ones
- Minimize assumptions
- Choose the solution with fewest moving parts
- When in doubt, simplify

## Testing Requirements
- Write tests before or alongside code
- Include unit, integration, and E2E tests as appropriate
- Use descriptive test names
- Ensure tests are deterministic and isolated

## Documentation
- Document all public APIs
- Include code comments for complex logic
- Update relevant documentation files
- Add examples for usage patterns
