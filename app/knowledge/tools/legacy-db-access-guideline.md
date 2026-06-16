# Legacy Database Access Guidelines

## Overview
Some enterprise systems still use legacy databases that require special handling to access safely.

## Connection Patterns
- **Read-Only Mode**: Preferred for initial data discovery
- **Parameterized Queries**: Required to prevent SQL injection
- **Connection Pooling**: Use managed pool, never create raw connections
- **Timeout Limits**: 30-second max query timeout to prevent hangs

## Safe Data Access
✓ SELECT queries with WHERE clauses
✓ Joining to reference tables for context
✓ Filtering by date ranges
✗ INSERT, UPDATE, DELETE without explicit approval
✗ Transactions that lock tables
✗ Backup or maintenance operations

## Troubleshooting Legacy Systems
When accessing legacy databases:
1. Try read-only connection first
2. Use connection timeout: 30 seconds
3. If timeout occurs, escalate to DBAs
4. Never retry without investigating root cause
5. Log all connection failures for monitoring

## Performance Considerations
Legacy systems are often performance-sensitive:
- Limit result sets to 1000 rows maximum
- Add LIMIT clauses to all queries
- Avoid complex JOINs across many tables
- Test queries on staging before production
- Schedule heavy operations during off-peak hours

## Access Control
Different user roles have different access:
- Read-only role: SELECT only
- Analytics role: SELECT + aggregate functions
- Admin role: Full access (restricted users only)
