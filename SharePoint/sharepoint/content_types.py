"""
Content type read helpers.
"""


def get_content_types(ctx, list_title=None):
    """Returns the loaded content type collection - site content types if
    list_title is None, otherwise the content types assignable on that list.
    Like Get-PnPContentType."""
    if list_title:
        content_types = ctx.web.lists.get_by_title(list_title).content_types
    else:
        content_types = ctx.web.content_types
    ctx.load(content_types)
    ctx.execute_query()
    return content_types


def get_content_type(ctx, name):
    """Returns a single loaded ContentType by name. Like Get-PnPContentType -Identity."""
    content_type = ctx.web.content_types.get_by_name(name)
    ctx.load(content_type)
    ctx.execute_query()
    return content_type
