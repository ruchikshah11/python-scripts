"""
List and list-item read/write helpers.
"""


def get_lists(ctx):
    """Returns the site's loaded list collection - iterate for .properties['Title'], etc."""
    lists = ctx.web.lists
    ctx.load(lists)
    ctx.execute_query()
    return lists


def get_list(ctx, list_title):
    """Returns a single loaded List object by title."""
    target_list = ctx.web.lists.get_by_title(list_title)
    ctx.load(target_list)
    ctx.execute_query()
    return target_list


def get_list_items(ctx, list_title, top=10, fields=None):
    """Returns up to `top` loaded items from the given list, selecting only
    `fields` (default: Id, Title, Modified) rather than every column.

    Requesting every field by default pulls in any lookup/person/workflow-status
    columns the list has too - lists with many of those (common on process-heavy
    lists) can trip SharePoint's list view lookup-column threshold (usually 8),
    causing a 500 SPQueryThrottledException. Selecting a minimal, explicit field
    list avoids that entirely."""
    if fields is None:
        fields = ["Id", "Title", "Modified"]
    target_list = ctx.web.lists.get_by_title(list_title)
    return target_list.items.select(fields).top(top).get().execute_query()


def add_list_item(ctx, list_title, fields):
    """Adds a new item to the given list. `fields` is a dict of internal field
    name -> value (e.g. {"Title": "New Item"}). Returns the created ListItem."""
    target_list = ctx.web.lists.get_by_title(list_title)
    new_item = target_list.add_item(fields)
    ctx.execute_query()
    return new_item


def update_list_item(ctx, list_title, item_id, fields, system_update=False):
    """Updates an existing item by ID. `fields` is a dict of internal field
    name -> value. Returns the updated ListItem.

    system_update=False (default): normal update() - creates a new version and
    updates Modified/Modified By, like Set-PnPListItem without -SystemUpdate.

    system_update=True: system_update() - like Set-PnPListItem -SystemUpdate.
    Does NOT create a new version and does NOT change Modified/Modified By or
    trigger workflows. Use this for housekeeping edits you don't want to show
    up as a change in the item's history."""
    target_list = ctx.web.lists.get_by_title(list_title)
    item = target_list.get_item_by_id(item_id)
    for key, value in fields.items():
        item.set_property(key, value)

    if system_update:
        item.system_update()
    else:
        item.update()

    ctx.execute_query()
    return item


def delete_list_item(ctx, list_title, item_id, permanent=False):
    """Deletes an item by ID from the given list.

    permanent=False (default): moves the item to the site's Recycle Bin -
    like Remove-PnPListItem. Recoverable from the Recycle Bin afterward.

    permanent=True: moves the item to the Recycle Bin, then immediately
    purges that Recycle Bin entry - like Remove-PnPListItem followed by
    Clear-PnPRecycleBinItem. NOT recoverable - SharePoint has no single call
    that deletes a list item while bypassing the Recycle Bin entirely."""
    target_list = ctx.web.lists.get_by_title(list_title)
    item = target_list.get_item_by_id(item_id)
    result = item.recycle()
    ctx.execute_query()

    if permanent:
        recycle_bin_id = result.value
        ctx.web.recycle_bin.get_by_id(recycle_bin_id).delete_object()
        ctx.execute_query()
