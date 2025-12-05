# RFC: New Page Range Endpoints for Scraping

## Summary

This RFC proposes adding two new endpoints to support page range scraping while maintaining the existing endpoints that use the `max_pages` parameter. The new endpoints will accept `page_from` and `page_to` parameters to allow users to specify a range of pages to scrape.

## Motivation

Currently, the scraping endpoints only accept a `max_pages` parameter which limits the number of pages to scrape from the beginning. This approach doesn't provide users with the flexibility to scrape specific ranges of pages, which is needed in scenarios such as:

- Resuming interrupted scraping operations
- Re-scraping specific page ranges for updates
- Targeting specific sections of paginated data
- Parallelizing scraping operations across different page ranges

## Proposed Solution

### New Endpoints

Add two new endpoints alongside the existing ones:
- `/scrap/csv/range` - To get CSV data for a specified page range
- `/scrap/json/range` - To get JSON data for a specified page range

### Parameter Changes

The new endpoints will accept these parameters:
- `page_from`: The starting page number to scrape (inclusive)
- `page_to`: The ending page number to scrape (inclusive)

The existing endpoints `/scrap/csv` and `/scrap/json` will continue to work with the `max_pages` parameter.

### Examples

Existing usage (unchanged):
```
/scrap/csv?max_pages=5
/scrap/json?max_pages=10
```

New usage:
```
/scrap/csv/range?page_from=5&page_to=10
/scrap/json/range?page_from=1&page_to=5
```

### Implementation Details

#### New Endpoint Specifications

1. `/scrap/csv/range`
   - Accepts `page_from` and `page_to` parameters
   - Validates that `page_from` is less than or equal to `page_to`
   - Validates that both parameters are positive integers
   - Scrapes data from page `page_from` to page `page_to` (inclusive)
   - Returns CSV formatted data

2. `/scrap/json/range`
   - Accepts `page_from` and `page_to` parameters
   - Validates that `page_from` is less than or equal to `page_to`
   - Validates that both parameters are positive integers
   - Scrapes data from page `page_from` to page `page_to` (inclusive)
   - Returns JSON formatted data

#### Validation Rules

For the new endpoints:
1. `page_from` must be a positive integer ≥ 1
2. `page_to` must be a positive integer ≥ `page_from`
3. Both parameters must be provided together (no partial specification allowed)

For the existing endpoints with `max_pages`:
1. `max_pages` must be a positive integer
2. Existing validation rules remain unchanged

## Alternatives Considered

### Alternative 1: Modify existing endpoints (was considered but not selected)
Replace `max_pages` parameter with `page_from`/`page_to` in existing endpoints.
- Pros: Simpler endpoint structure
- Cons: Breaks backward compatibility

### Alternative 2: Add optional page range parameters to existing endpoints (was considered but not selected)
Keep `max_pages` and add `page_from`/`page_to` as optional parameters.
- Pros: Maintains backward compatibility
- Cons: More complex parameter validation, potential conflicts between parameters

### Alternative 3: Create new endpoints with page range parameters (selected approach)
Keep existing endpoints with `max_pages` parameter and create new `/range` endpoints for page range functionality.
- Pros: Maintains backward compatibility, clean separation of functionality, no parameter conflicts
- Cons: Slightly more complex API surface with additional endpoints

## Security Considerations

- Input validation is crucial to prevent page number manipulation
- Range limits should be enforced to prevent excessive resource consumption
- Both parameters should be validated as positive integers to prevent injection attacks
- Rate limiting should apply to the new endpoints as well to prevent API abuse

## Testing Strategy

1. Unit tests for parameter validation for both new and existing endpoints
2. Integration tests for the new endpoints with various page range combinations
3. Integration tests for existing endpoints to ensure no regression
4. Edge case tests (single page, invalid ranges, etc.)
5. Error handling tests for invalid input in both endpoint sets
6. Performance tests to ensure new endpoints don't cause resource issues

## Rollout Plan

1. Implement the new range endpoints
2. Update API documentation to include the new endpoints
3. Add comprehensive tests for the new functionality
4. Deploy to staging for validation
5. Deploy to production with documentation updates

## Future Considerations

- Pagination metadata in response headers
- Rate limiting per page range to prevent API abuse
- Support for more complex page selection patterns (e.g., specific page lists)
- Consider deprecating `max_pages` parameter in future versions after users migrate to range endpoints