"""
Permissions helpers - groups, group membership, and list-item role assignments.
"""

ASSOCIATED_GROUP_TYPES = ("owner", "member", "visitor")


def get_site_users(ctx):
    """Returns the site's loaded user collection - every user who has visited
    or been granted access, not just group members. Like Get-PnPUser."""
    users = ctx.web.site_users
    ctx.load(users)
    ctx.execute_query()
    return users


def get_groups(ctx):
    """Returns the site's loaded group collection. Like Get-PnPGroup (all)."""
    groups = ctx.web.site_groups
    ctx.load(groups)
    ctx.execute_query()
    return groups


def get_group(ctx, group_name):
    """Returns a single loaded Group by name. Like Get-PnPGroup -Identity <name>."""
    group = ctx.web.site_groups.get_by_name(group_name)
    ctx.load(group)
    ctx.execute_query()
    return group


def get_associated_group(ctx, group_type):
    """Returns the site's associated Owner/Member/Visitor group. group_type must be
    one of "owner", "member", "visitor". Like Get-PnPGroup -AssociatedOwnerGroup /
    -AssociatedMemberGroup / -AssociatedVisitorGroup."""
    if group_type not in ASSOCIATED_GROUP_TYPES:
        raise ValueError(f"group_type must be one of {ASSOCIATED_GROUP_TYPES}, got {group_type!r}")

    group = {
        "owner": ctx.web.associated_owner_group,
        "member": ctx.web.associated_member_group,
        "visitor": ctx.web.associated_visitor_group,
    }[group_type]

    ctx.load(group)
    ctx.execute_query()
    return group


def get_group_members(ctx, group_name):
    """Returns the loaded members of a group by name. Like Get-PnPGroupMembers."""
    group = ctx.web.site_groups.get_by_name(group_name)
    members = group.users
    ctx.load(members)
    ctx.execute_query()
    return members


def break_item_role_inheritance(ctx, list_title, item_id, copy_role_assignments=True, clear_sub_scopes=True):
    """Breaks role inheritance on a list item, giving it its own unique permissions.
    Like $item.BreakRoleInheritance() in PnP PowerShell scripts."""
    target_list = ctx.web.lists.get_by_title(list_title)
    item = target_list.get_item_by_id(item_id)
    item.break_role_inheritance(copy_role_assignments, clear_sub_scopes)
    ctx.execute_query()


def reset_item_role_inheritance(ctx, list_title, item_id):
    """Resets a list item back to inheriting permissions from its parent list."""
    target_list = ctx.web.lists.get_by_title(list_title)
    item = target_list.get_item_by_id(item_id)
    item.reset_role_inheritance()
    ctx.execute_query()


def get_item_role_assignments(ctx, list_title, item_id):
    """Returns the loaded role assignments (principal -> roles) for a list item.
    Like Get-PnPListItemPermission."""
    target_list = ctx.web.lists.get_by_title(list_title)
    item = target_list.get_item_by_id(item_id)
    assignments = item.role_assignments
    ctx.load(assignments, ["Member", "RoleDefinitionBindings"])
    ctx.execute_query()
    return assignments


def add_item_role(ctx, list_title, item_id, principal_name, role_name):
    """Grants `role_name` (e.g. "Read", "Contribute", "Full Control") to `principal_name`
    (a user login name or group name) on a list item. The item must already have unique
    permissions (call break_item_role_inheritance first). Like
    Set-PnPListItemPermission -AddRole."""
    target_list = ctx.web.lists.get_by_title(list_title)
    item = target_list.get_item_by_id(item_id)
    role_def = ctx.web.role_definitions.get_by_name(role_name)
    item.add_role_assignment(principal_name, role_def)
    ctx.execute_query()


def remove_item_role(ctx, list_title, item_id, principal_name, role_name):
    """Revokes `role_name` from `principal_name` on a list item. Like
    Set-PnPListItemPermission -RemoveRole."""
    target_list = ctx.web.lists.get_by_title(list_title)
    item = target_list.get_item_by_id(item_id)
    role_def = ctx.web.role_definitions.get_by_name(role_name)
    item.remove_role_assignment(principal_name, role_def)
    ctx.execute_query()
