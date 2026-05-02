# Migration Documentation

## Backup Information

This directory contains documentation for the kimi-agent-sdk migration process.

### Backup Branch

The existing KimiClient code has been backed up in the following location:

- **Branch**: `backup/pre-sdk-migration`
- **Tag**: `v-pre-sdk-migration`

#### How to Access the Backup

To view the backup:
```bash
git checkout backup/pre-sdk-migration
```

To checkout the tag:
```bash
git checkout v-pre-sdk-migration
```

To restore specific files from backup:
```bash
git checkout backup/pre-sdk-migration -- docuswarm/llm/
```

### Files Backed Up

The following files are included in the backup:

#### LLM Module
- `docuswarm/llm/__init__.py`
- `docuswarm/llm/client.py` - Main KimiClient implementation
- `docuswarm/llm/config.py` - LLM configuration
- `docuswarm/llm/rate_limit.py` - Rate limiting
- `docuswarm/llm/response.py` - Response handling
- `docuswarm/llm/retry.py` - Retry logic
- `docuswarm/llm/tools.py` - Tool definitions

#### Agent Files
- `docuswarm/agents/base.py` - Base agent class (references KimiClient)
- `docuswarm/agents/independent.py` - Independent agent (references KimiClient)
- `docuswarm/agents/evaluator.py` - Evaluator agent (references KimiClient)
- `docuswarm/agents/persona.py` - Persona loader

### Rollback Instructions

If the SDK migration encounters issues and you need to rollback:

1. **Checkout the backup branch**:
   ```bash
   git checkout backup/pre-sdk-migration
   ```

2. **Or checkout specific files**:
   ```bash
   git checkout backup/pre-sdk-migration -- docuswarm/llm/
   git checkout backup/pre-sdk-migration -- docuswarm/agents/
   ```

3. **Return to main branch after rollback**:
   ```bash
   git checkout main
   ```

### Important Notes

- The backup branch is **read-only** - do not make changes to it
- The backup represents the state of main branch at the time of backup creation
- All team members can access this backup for rollback purposes
