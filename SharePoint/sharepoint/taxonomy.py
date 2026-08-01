"""
Taxonomy export helpers.

IMPORTANT - this is NOT a PnP-template-compatible export. Export-PnPTermGroupToXml
produces XML in PnP's own provisioning-template schema, which no Python library
(including this one) reimplements - see SharePoint/sharepoint/README.md for why.
The functions below return plain dicts (name/termSets/terms/labels) meant for
backup, reference, or diffing - not for re-importing via PnP or any other tool.

Implemented via raw REST calls against the SharePoint v2.1 Term Store API,
NOT Office365-REST-Python-Client's TaxonomyService object model. That object
model's internal path names ("termGroups"/"termSets") don't match the actual
documented API ("groups"/"sets"/"terms"), which caused it to silently return
empty results against a real tenant instead of raising an error. Raw REST
calls avoid that mismatch and are easy to inspect/debug if something's still
off (the JSON responses are plain dicts, printable as-is).
"""

import requests


def _term_store_base_url(ctx):
    return f"{ctx.service_root_url()}/v2.1/termStore"


def _get(url, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json;odata=nometadata",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def _term_to_dict(term_json):
    return {
        "id": term_json.get("id"),
        "labels": [
            {"name": label.get("name"), "languageTag": label.get("languageTag"), "isDefault": label.get("isDefault")}
            for label in term_json.get("labels", [])
        ],
    }


def _term_set_to_dict(term_store_base_url, term_set_json, access_token):
    set_id = term_set_json.get("id")
    terms_json = _get(f"{term_store_base_url}/sets/{set_id}/terms", access_token).get("value", [])
    return {
        "id": set_id,
        "name": term_set_json["localizedNames"][0]["name"] if term_set_json.get("localizedNames") else None,
        "terms": [_term_to_dict(term) for term in terms_json],
    }


def _group_to_dict(term_store_base_url, group_json, access_token):
    group_id = group_json.get("id")
    sets_json = _get(f"{term_store_base_url}/groups/{group_id}/sets", access_token).get("value", [])
    return {
        "name": group_json.get("displayName"),
        "termSets": [_term_set_to_dict(term_store_base_url, term_set_json, access_token) for term_set_json in sets_json],
    }


def export_term_group(ctx, group_name, token_result):
    """Returns a dict snapshot of a single term group: {"name": ..., "termSets": [...]}.
    Matches group_name case-insensitively and ignoring leading/trailing whitespace.
    NOT a PnP provisioning template - see the module docstring above."""
    term_store_base_url = _term_store_base_url(ctx)
    access_token = token_result["access_token"]

    groups_json = _get(f"{term_store_base_url}/groups", access_token).get("value", [])

    normalized_target = group_name.strip().lower()
    target_group = next(
        (group for group in groups_json if (group.get("displayName") or "").strip().lower() == normalized_target),
        None,
    )
    if target_group is None:
        available = ", ".join(repr(group.get("displayName")) for group in groups_json)
        raise ValueError(f"Term group '{group_name}' not found. Available term groups: {available}")

    return _group_to_dict(term_store_base_url, target_group, access_token)


def export_term_store(ctx, token_result):
    """Returns a list of dict snapshots - one per term group in the entire term
    store, same shape as export_term_group(). Use this when you don't need to
    target one specific group, or want everything at once. NOT a PnP
    provisioning template - see the module docstring above."""
    term_store_base_url = _term_store_base_url(ctx)
    access_token = token_result["access_token"]

    groups_json = _get(f"{term_store_base_url}/groups", access_token).get("value", [])
    return [_group_to_dict(term_store_base_url, group_json, access_token) for group_json in groups_json]


def get_terms_for_set(ctx, term_set_id, token_result):
    """Returns every non-deprecated term in a term set as a flat list of
    {"id": ..., "label": ...} dicts - e.g. the candidate pool a Managed
    Metadata field's value would be randomly picked from. Uses the same
    raw-REST v2.1 Term Store API as export_term_group/export_term_store, for
    the same reason (see module docstring)."""
    term_store_base_url = _term_store_base_url(ctx)
    access_token = token_result["access_token"]

    terms_json = _get(f"{term_store_base_url}/sets/{term_set_id}/terms", access_token).get("value", [])
    return [
        {"id": term.get("id"), "label": term["labels"][0]["name"] if term.get("labels") else ""}
        for term in terms_json
        if not term.get("isDeprecated", False)
    ]
