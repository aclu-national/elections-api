# ACLU Elections API documentation

* [API endpoints](endpoints.md) ([v1 endpoints](endpoints-v1.md))
* [How to install](install.md)
* [Care and maintenance](maintenance.md)
* [Common tasks](tasks.md)

## Generating endpoints docs

The API endpoints documentation is generated programmatically:

```
python scripts/md-endpoints.py | pbcopy
```

This will copy the API endpoints Markdown to your clipboard.
