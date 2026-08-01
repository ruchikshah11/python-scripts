"""
Connection helpers - interactive sign-in and ClientContext creation.
"""

from datetime import datetime, timedelta

import msal
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.token_response import TokenResponse


def _acquire_token(site_url, client_id, tenant_id, logger=None):
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.PublicClientApplication(client_id=client_id, authority=authority)

    resource = site_url.split("/sites/")[0]
    scopes = [f"{resource}/.default"]

    if logger:
        logger.info("Opening browser for interactive sign-in")
    result = app.acquire_token_interactive(scopes=scopes)

    if "access_token" not in result:
        raise Exception(f"Could not acquire token: {result.get('error_description')}")

    return result


def connect(site_url, client_id, tenant_id, logger=None):
    """Returns (ctx, token_result) - an authenticated ClientContext for site_url
    via interactive (browser) sign-in, plus the raw MSAL token result."""
    token_result = _acquire_token(site_url, client_id, tenant_id, logger)
    ctx = ClientContext(site_url).with_access_token(lambda: TokenResponse.from_json(token_result))
    return ctx, token_result


def get_connection_info(ctx, token_result, client_id, site_url):
    """Returns a dict describing the active connection: site url, web title,
    connected user, tenant id, client id, and token type/scope/expiry."""
    web = ctx.web
    ctx.load(web)
    ctx.execute_query()

    claims = token_result.get("id_token_claims", {})
    expires_at = datetime.now() + timedelta(seconds=token_result.get("expires_in", 0))

    return {
        "site_url": site_url,
        "web_title": web.properties.get("Title"),
        "connected_as": claims.get("preferred_username", claims.get("upn", "Unknown")),
        "tenant_id": claims.get("tid", "Unknown"),
        "client_id": client_id,
        "token_type": token_result.get("token_type"),
        "token_scope": token_result.get("scope"),
        "token_expires_at": expires_at,
    }
