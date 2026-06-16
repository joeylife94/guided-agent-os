# Human Review Policy

## Review Triggers
The following scenarios require human review:

### Decision-Related Triggers
- Agent confidence score below 70% on critical decisions
- Multiple policy sources give conflicting guidance
- Decision involves sensitive data or high-risk operations
- Customer escalation or complaint is involved

### Operational Triggers
- First time encountering a new query type
- Recommendation involves changes to production systems
- External party communication is needed
- Knowledge base query returned no matches

### Escalation Workflow
1. Agent flags decision as requiring review
2. Provides full reasoning chain with citations
3. Routes to appropriate human reviewer based on domain
4. Human reviews and approves, rejects, or modifies recommendation
5. Agent documents human decision and reason

## Human Reviewer Responsibilities
- Review provided reasoning and citations
- Validate that all relevant policies were considered
- Check for logical consistency and factual accuracy
- Provide feedback for future agent improvements
- Sign off on final recommendation

## Approval SLAs
- Critical decisions: Review within 1 hour
- High priority: Review within 4 hours  
- Standard: Review within 24 hours
