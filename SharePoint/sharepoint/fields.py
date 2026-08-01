"""
Field (site column) read helpers.
"""


def get_fields(ctx, list_title=None):
    """Returns the loaded field collection - site fields if list_title is None,
    otherwise the fields of that specific list. Like Get-PnPField."""
    if list_title:
        target_list = ctx.web.lists.get_by_title(list_title)
        fields = target_list.fields
    else:
        fields = ctx.web.fields

    ctx.load(fields)
    ctx.execute_query()
    return fields


def get_field(ctx, field_name, list_title=None):
    """Returns a single loaded Field by internal name or title - site-scoped if
    list_title is None, otherwise scoped to that list. Like Get-PnPField -Identity."""
    if list_title:
        target_list = ctx.web.lists.get_by_title(list_title)
        field = target_list.fields.get_by_internal_name_or_title(field_name)
    else:
        field = ctx.web.fields.get_by_internal_name_or_title(field_name)

    ctx.load(field)
    ctx.execute_query()
    return field
