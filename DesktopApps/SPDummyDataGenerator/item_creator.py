"""
Creates dummy list items in batches - queues `batch_size` items' worth of
add_item() calls, then flushes with a single execute_query(), same batching
model as the C# tool's ListItemCreator (its "Batch size" setting controls how
many items accumulate before a network round-trip).
"""

import random

from value_generator import UNSUPPORTED


def create_items(ctx, list_title, fields, content_type_ids, item_count, batch_size, generator, progress_callback, logger):
    """Creates `item_count` items on `list_title`, each populated from
    `fields` (schema_reader.get_writable_fields() output, already filtered to
    is_supported fields only) via `generator.generate_value()`. Randomly
    assigns one of `content_type_ids` per item if there's more than one
    (empty list = don't set ContentTypeId at all). Calls
    progress_callback(items_created_so_far) after each batch flush."""
    target_list = ctx.web.lists.get_by_title(list_title)
    created = 0

    for start in range(0, item_count, batch_size):
        batch_end = min(start + batch_size, item_count)
        for _ in range(start, batch_end):
            values = {}
            for field in fields:
                value = generator.generate_value(field)
                if value is UNSUPPORTED:
                    continue
                values[field["internal_name"]] = value

            if len(content_type_ids) > 1:
                values["ContentTypeId"] = random.choice(content_type_ids)

            target_list.add_item(values)

        ctx.execute_query()
        created = batch_end
        logger.info("Created %s/%s items", created, item_count)
        progress_callback(created)

    return created
