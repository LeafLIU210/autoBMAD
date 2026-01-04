# Epic: User Authentication System

**Epic ID**: EPIC-EXAMPLE-001
**Version**: 1.0
**Date**: 2026-01-04

---

## Overview

This epic demonstrates the implementation of a complete user authentication system using the BMAD methodology. The example covers frontend components, backend API integration, database operations, and comprehensive testing.

This example epic contains 5 complete stories that demonstrate different aspects of the BMAD workflow:
1. **Backend Story**: User registration API endpoint
2. **Frontend Story**: Login form UI component
3. **Integration Story**: Authentication flow end-to-end
4. **Database Story**: User table schema and migrations
5. **Testing Story**: Comprehensive test suite

Each story includes complete sections as required by BMAD: Story, Acceptance Criteria, Tasks/Subtasks, Dev Notes, Testing, etc.

---

## Story References

### Backend Stories

- **[Story 001: User Registration API](../stories/user-registration-api.md)** - Implement backend endpoint for user registration with validation and error handling
- **[Story 003: User Authentication API](../stories/user-authentication-api.md)** - Create login endpoint with JWT token generation

### Frontend Stories

- **[Story 002: Login Form Component](../stories/login-form-component.md)** - Build React component for user login with form validation

### Integration Stories

- **[Story 004: End-to-End Authentication Flow](../stories/e2e-auth-flow.md)** - Implement complete authentication flow from login to protected routes

### Database Stories

- **[Story 005: User Database Schema](../stories/user-database-schema.md)** - Design and implement user table with proper indexing and constraints

---

## Implementation Notes

### Story Structure

Each story in this example follows the complete BMAD story template:

```markdown
# Story xxx: [Title]

**Epic**: [Epic Reference]

---

## Status
**Status**: [Draft|Approved|In Progress|Ready for Review|Completed]

---

## Story
**As a** [user type],
**I want to** [action],
**So that** [benefit]

---

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

---

## Tasks / Subtasks
- [ ] Task 1: Description
  - [ ] Subtask 1.1: Detail
  - [ ] Subtask 1.2: Detail

---

## Dev Notes
### Implementation Notes
- Key technical details
- Architecture decisions
- Dependencies

### Technical Details
- API specifications
- Data models
- Component structure

---

## Testing
### Testing Standards
- Framework used
- Coverage requirements
- Test types

### Specific Testing Requirements
- Unit tests
- Integration tests
- E2E tests

---

## Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-01-04 | 1.0 | Initial story creation | Author |

---

## Dev Agent Record
*Populated during implementation*

### Agent Model Used
{{agent_model_name_version}}

### Debug Log References
*Links to debug logs*

### Completion Notes List
*Implementation notes*

### File List
*Files created/modified*

### Change Log
*Detailed change log*

---

## QA Results
*Populated by QA agent*
```

### Story Patterns Demonstrated

#### Pattern 1: Backend API Story
- Story 001: User Registration API
- Demonstrates: API endpoint creation, validation, error handling, testing

#### Pattern 2: Frontend Component Story
- Story 002: Login Form Component
- Demonstrates: UI component development, form handling, validation, styling

#### Pattern 3: Integration Story
- Story 004: End-to-End Authentication Flow
- Demonstrates: Multi-component integration, state management, routing

#### Pattern 4: Database Story
- Story 005: User Database Schema
- Demonstrates: Schema design, migrations, indexing, constraints

#### Pattern 5: Testing Story
- Story 003: User Authentication API (with comprehensive testing)
- Demonstrates: Test-driven development, coverage, test types

### File Naming Convention

Stories use descriptive, kebab-case filenames:
- `user-registration-api.md`
- `login-form-component.md`
- `user-authentication-api.md`
- `e2e-auth-flow.md`
- `user-database-schema.md`

### Story Dependencies

Stories can reference each other to show dependencies:
- Story 002 (Frontend) depends on Story 001 (Backend API)
- Story 004 (Integration) depends on Stories 001, 002, and 003
- Story 005 (Database) is a prerequisite for all backend stories

### Acceptance Criteria Types

This example demonstrates different types of acceptance criteria:

1. **Functional Criteria**: Specific behaviors (user can register, form validates input)
2. **Technical Criteria**: Performance, security, scalability (API response time, JWT security)
3. **User Experience Criteria**: UI/UX requirements (form feedback, error messages)
4. **Quality Criteria**: Testing, documentation (test coverage, code comments)

### Task Breakdown Patterns

Stories show various task breakdown approaches:

1. **Sequential Tasks**: One task leads to the next
2. **Parallel Tasks**: Independent tasks that can run concurrently
3. **Hierarchical Tasks**: Tasks with multiple subtasks
4. **Testing Tasks**: Dedicated testing tasks separate from implementation

### Dev Notes Content

Dev Notes sections include:

1. **Implementation Notes**: High-level approach and architecture
2. **Technical Details**: Specific technologies, libraries, patterns
3. **API Specifications**: Endpoint details, request/response formats
4. **Component Structure**: Props, state, lifecycle methods
5. **Database Schema**: Tables, columns, relationships, indexes
6. **Testing Approach**: Testing pyramid, mock strategies, test data

---

## How to Use This Example

### For New BMAD Users

1. **Read the Epic Overview**: Understand the overall goal
2. **Review Each Story**: Study the structure and content
3. **Note the Patterns**: Observe how different types of stories are structured
4. **Check Dependencies**: See how stories reference each other

### For Epic Creation

1. **Follow the Template**: Use this epic as a template for new epics
2. **Adapt the Structure**: Modify story patterns to fit your domain
3. **Maintain Consistency**: Keep the same section structure across stories
4. **Document Dependencies**: Clearly show story relationships

### For Story Writing

1. **Complete All Sections**: Don't skip optional sections
2. **Be Specific**: Use concrete acceptance criteria
3. **Break Down Tasks**: Divide work into manageable pieces
4. **Include Testing**: Plan testing from the start
5. **Add Context**: Provide implementation guidance in Dev Notes

---

## Example Execution

To process this example epic:

```bash
python autoBMAD/epic_automation/epic_driver.py test-docs/epics/example-epic.md --verbose
```

This will:
1. Parse the epic and identify all 5 stories
2. Process each story through SM-Dev-QA cycle
3. Execute tasks and subtasks in order
4. Generate Dev Agent Records
5. Create QA reports
6. Provide detailed progress logging

---

## Customization

This example can be customized for different domains:

- **E-commerce**: Products, Cart, Checkout, Payment, Orders
- **Content Management**: Articles, Media, Comments, Users, Permissions
- **Financial**: Transactions, Accounts, Reports, Compliance, Audits
- **Healthcare**: Patients, Appointments, Records, Billing, Prescriptions

Simply replace the authentication system stories with stories relevant to your domain, maintaining the same structure and completeness.

---

## Conclusion

This example epic demonstrates the complete BMAD methodology with realistic, production-quality stories. Use it as a reference when creating your own epics and stories.

For more information, see the [BMAD Documentation](../README.md).
