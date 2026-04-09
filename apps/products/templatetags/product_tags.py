from django import template

register = template.Library()


@register.filter
def parse_specs(text):
    """
    Parse a plain-text specifications block into a list of (label, value) tuples.
    Lines that contain ':' are split on the first colon.
    Lines without ':' are kept as (None, line) so the template can render them
    as full-width rows or separators.
    Blank lines are skipped.
    """
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if ':' in line:
            label, _, value = line.partition(':')
            rows.append((label.strip(), value.strip()))
        else:
            rows.append((None, line))
    return rows
