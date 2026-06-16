# Query Template Policy

## Standard Query Templates
This policy defines approved query patterns and templates for common operations.

## Read-Only Query Template
```sql
SELECT column_list
FROM table_name
WHERE filter_conditions
ORDER BY sort_column
LIMIT 1000;
```

### Rules:
- Always include WHERE clause
- Always include LIMIT
- Test on staging first
- Document query purpose

## Aggregate Query Template
```sql
SELECT group_column, COUNT(*) as count, AVG(metric) as avg_value
FROM table_name
WHERE date_range_filter
GROUP BY group_column
ORDER BY count DESC
LIMIT 100;
```

### Rules:
- Use meaningful aliases
- Filter by time range when possible
- Limit result set size
- Validate GROUP BY columns exist

## Approved Query Patterns
- Dimension analysis (GROUP BY on categorical columns)
- Time-series analysis (GROUP BY date ranges)
- Filtering and sorting
- Simple JOINs (max 3 tables)
- Window functions (PARTITION BY, RANK)

## Prohibited Query Patterns
- DELETE without WHERE clause (all rows)
- UPDATE that modifies audit columns
- ALTER TABLE statements
- Stored procedure calls (unless pre-approved)
- Dynamic SQL without parameterization

## Query Review Checklist
Before executing any query:
- [ ] Uses approved template
- [ ] Parameterizes all inputs
- [ ] Includes row limits
- [ ] Where/filtering appropriate
- [ ] Tested on sample data
- [ ] Impact on production assessed
