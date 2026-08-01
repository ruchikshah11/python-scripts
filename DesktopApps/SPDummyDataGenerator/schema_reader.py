"""
Reads a SharePoint list's writable, populatable fields - the schema that
drives value_generator.py / item_creator.py. Hidden fields, read-only fields,
and an explicit skip-list of system internal names are excluded, mirroring
the same field-selection rules as the original C# SPDummyDataGenerator tool
(C:\\Ruchik\\Csom\\SPDummyDataGenerator) this is a Python + Tkinter port of.

Field properties are read straight from Field.properties (the raw REST JSON
payload Office365-REST-Python-Client stores on every entity) rather than via
each field subclass's named accessors. SharePoint's REST API returns a field's
full set of type-specific properties (Choices, LookupList, TermSetId, etc.) in
one response regardless of subclass - unlike CSOM, which needs a separate
CastTo<T>() + Include() round-trip per field type. That's what lets this
module do in one ctx.load()/execute_query() what the C# version needed two
round-trips and half a dozen CastTo<T>() calls for.
"""

# Internal names that are never populated even if not hidden/read-only -
# system/administrative columns that either can't be set directly via the
# REST item-creation payload or would corrupt list state if randomized.
# Same list the C# tool uses.
SKIP_INTERNAL_NAMES = {
    "ContentTypeId", "Attachments", "Edit", "LinkTitle", "LinkTitleNoMenu",
    "LinkTitle2", "SelectTitle", "InstanceID", "Order", "GUID", "WorkflowInstanceID",
    "FileRef", "FileDirRef", "File_x0020_Type", "FSObjType", "PermMask", "AppAuthor",
    "AppEditor", "ProgId", "ScopeId", "VirusStatus", "CheckedOutTitle", "CheckedOutUserId",
    "IsCheckedoutToLocal", "_ModerationStatus", "_ModerationComments", "WorkflowVersion",
    "ParentVersionString", "ParentLeafName", "_UIVersionString", "MetaInfo",
    "ItemChildCount", "FolderChildCount",
}

# TypeAsString values value_generator.py knows how to produce a value for.
# Anything else comes back from get_writable_fields() with is_supported=False
# so the caller can show it in the UI as skipped, rather than silently
# dropping it (matches the C# tool's SupportedFieldKind.Unsupported).
SUPPORTED_TYPES = {
    "Text", "Note", "Choice", "MultiChoice", "Number", "Currency", "Boolean",
    "DateTime", "URL", "Guid", "User", "Lookup",
    "TaxonomyFieldType", "TaxonomyFieldTypeMulti", "Geolocation",
}


def get_writable_fields(ctx, list_title):
    """Returns a list of dicts describing every non-hidden, non-read-only,
    non-system field on `list_title`. Each dict has:
        internal_name, title, type_as_string, required, is_supported,
        choices, lookup_list, lookup_field, allow_multiple_values,
        term_set_id, display_format, rich_text
    Fields with a Lookup list ID that's empty/missing, or a Taxonomy field
    with no term_set_id, are marked is_supported=False - same "can't safely
    generate a value" cases the C# tool treats as unsupported."""
    target_list = ctx.web.lists.get_by_title(list_title)
    fields = target_list.fields
    ctx.load(fields)
    ctx.execute_query()

    writable = []
    for field in fields:
        properties = field.properties
        internal_name = properties.get("InternalName")

        if properties.get("Hidden") or properties.get("ReadOnlyField"):
            continue
        if internal_name in SKIP_INTERNAL_NAMES:
            continue

        type_as_string = properties.get("TypeAsString")
        lookup_list = properties.get("LookupList") or None
        term_set_id = properties.get("TermSetId") or None

        is_supported = type_as_string in SUPPORTED_TYPES
        if type_as_string == "Lookup" and not lookup_list:
            is_supported = False
        if type_as_string in ("TaxonomyFieldType", "TaxonomyFieldTypeMulti") and not term_set_id:
            is_supported = False

        writable.append({
            "internal_name": internal_name,
            "title": properties.get("Title"),
            "type_as_string": type_as_string,
            "required": bool(properties.get("Required")),
            "is_supported": is_supported,
            "choices": list(properties.get("Choices") or []),
            "lookup_list": lookup_list,
            "lookup_field": properties.get("LookupField") or "Title",
            "allow_multiple_values": bool(properties.get("AllowMultipleValues")),
            "term_set_id": term_set_id,
            "display_format": properties.get("DisplayFormat"),
            "rich_text": bool(properties.get("RichText")),
        })

    return writable


def get_assignable_content_type_ids(ctx, list_title):
    """Returns the string content type IDs assignable on `list_title`,
    excluding hidden content types and the built-in Folder type (ID prefix
    "0x0120") - same filter the C# tool applies before randomly assigning one
    per item. Returns an empty list if the list only has one (or zero)
    assignable content types, since there's nothing to randomize then."""
    import sharepoint  # noqa: E402 - see spdummydatagenerator.py for the sys.path setup

    content_types = sharepoint.get_content_types(ctx, list_title=list_title)
    return [
        content_type.properties["StringId"]
        for content_type in content_types
        if not content_type.properties.get("Hidden")
        and not content_type.properties["StringId"].startswith("0x0120")
    ]
