# QA Review Guidance

## Review Checklist
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Type checking passes
- [ ] No linting errors
- [ ] Documentation is complete
- [ ] Security considerations addressed
- [ ] Performance is acceptable
- [ ] Error handling is robust

## Quality Gates

### BasedPyright (Type Checking)
- **Target**: 0 errors, minimal warnings
- **Action**: Fix all type errors
- **Warning**: Review and address or document acceptable warnings
- **Retry**: Up to 3 automatic retry attempts with auto-fix

### Ruff (Linting)
- **Target**: 0 errors
- **Action**: Auto-fix where possible, manual fix for rest
- **Coverage**: PEP 8, complexity, imports, best practices
- **Performance**: Very fast, mostly I/O bound

### Fixtest (Test Automation)
- **Target**: All tests pass
- **Action**: Fix failing tests
- **Coverage**: Unit, integration, E2E tests
- **Debug**: Debugpy integration for persistent failures
- **Retry**: Up to 5 automatic retry attempts

## QA Scoring System
- **Document Completeness**: 70% (must reach 100%)
  - Story title and status
  - Acceptance criteria completion
  - Task completion
- **Tool Validation**: 30%
  - PASS: 30 points
  - CONCERNS: 15 points
  - FAIL: 0 points
  - WAIVED: 20 points (tools unavailable)

## Pass Criteria
A story passes QA if and only if:
1. Document completeness = 100%
2. No critical failures
3. Tool results ≠ FAIL (PASS, CONCERNS, or WAIVED acceptable)

## QA Status Definitions
- **PASS**: All checks pass, story complete
- **CONCERNS**: Minor issues found, acceptable with attention
- **FAIL**: Critical issues found, must fix before proceeding
- **WAIVED**: Tools unavailable, continuing with reduced validation

## Review Process
1. **Document Review**: Verify story completeness
2. **Code Review**: Check implementation quality
3. **Test Review**: Ensure test coverage and quality
4. **Tool Validation**: Run quality gates
5. **Final Decision**: Pass/fail/waive with detailed feedback

## Feedback Requirements
- List all failures with specific details
- Provide actionable fix recommendations
- Include links to relevant documentation
- Suggest improvements for future stories
