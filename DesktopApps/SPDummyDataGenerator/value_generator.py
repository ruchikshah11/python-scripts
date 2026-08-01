"""
Generates a random value for each supported field kind schema_reader.py
returns, using the Faker library - Python's rough equivalent of the C# tool's
Bogus library. Reference data needed to generate realistic values (site
users, lookup-list candidate items, Managed Metadata terms) is fetched once
per generation run and cached, since it doesn't change mid-run and re-fetching
per item would be one extra round-trip per field per item.
"""

import random
import uuid

from faker import Faker
from office365.sharepoint.fields.lookup_value import FieldLookupValue
from office365.sharepoint.fields.multi_lookup_value import FieldMultiLookupValue
from office365.sharepoint.fields.multi_user_value import FieldMultiUserValue
from office365.sharepoint.fields.url_value import FieldUrlValue
from office365.sharepoint.fields.user_value import FieldUserValue
from office365.sharepoint.taxonomy.field_value import TaxonomyFieldValue, TaxonomyFieldValueCollection

import sharepoint  # noqa: E402 - see spdummydatagenerator.py for the sys.path setup

# Sentinel: this field's type isn't one generate_value() knows how to
# produce a value for. Distinct from None/"" so a genuinely blank generated
# value (which shouldn't happen, but just in case) isn't mistaken for "skip".
UNSUPPORTED = object()

LOOKUP_ITEM_SAMPLE_SIZE = 100


class DummyValueGenerator:
    def __init__(self, ctx, token_result, logger):
        self.ctx = ctx
        self.token_result = token_result
        self.logger = logger
        self.faker = Faker()
        self._user_ids_cache = None
        self._lookup_items_cache = {}  # lookup_list_id -> [(id, title), ...]
        self._term_cache = {}          # term_set_id -> [{"id", "label"}, ...]

    # ---------- cached reference data ----------

    def _get_user_ids(self):
        if self._user_ids_cache is None:
            users = sharepoint.get_site_users(self.ctx)
            ids = [
                user.properties["Id"] for user in users
                if user.properties.get("PrincipalType") == 1  # 1 == User (vs SecurityGroup/SharePointGroup/etc.)
                and "system" not in (user.properties.get("LoginName") or "").lower()
            ]
            if not ids:
                self.ctx.load(self.ctx.web.current_user)
                self.ctx.execute_query()
                ids = [self.ctx.web.current_user.properties["Id"]]
                self.logger.info("No selectable site users found - falling back to the current user")
            self._user_ids_cache = ids
        return self._user_ids_cache

    def _get_lookup_items(self, lookup_list_id):
        if lookup_list_id not in self._lookup_items_cache:
            lookup_list = self.ctx.web.lists.get_by_id(lookup_list_id)
            items = lookup_list.items.select(["Id", "Title"]).top(LOOKUP_ITEM_SAMPLE_SIZE).get().execute_query()
            self._lookup_items_cache[lookup_list_id] = [
                (item.properties["Id"], item.properties.get("Title") or "") for item in items
            ]
        return self._lookup_items_cache[lookup_list_id]

    def _get_terms(self, term_set_id):
        if term_set_id not in self._term_cache:
            self._term_cache[term_set_id] = sharepoint.get_terms_for_set(self.ctx, term_set_id, self.token_result)
        return self._term_cache[term_set_id]

    # ---------- value generation ----------

    def generate_value(self, field):
        """Returns a value suitable for ItemCreator to assign to
        field["internal_name"] on a new item, or UNSUPPORTED if this field's
        type/reference data isn't one this generator can handle (e.g. a
        Lookup list or term set that resolved to zero candidate values)."""
        handler = self._HANDLERS.get(field["type_as_string"])
        if handler is None:
            return UNSUPPORTED
        return handler(self, field)

    def _text(self, field):
        return self.faker.bs()[:255]

    def _note(self, field):
        text = self.faker.paragraph(nb_sentences=random.randint(2, 3))
        return f"<p>{text}</p>" if field["rich_text"] else text

    def _choice(self, field):
        if not field["choices"]:
            return UNSUPPORTED
        return random.choice(field["choices"])

    def _multi_choice(self, field):
        if not field["choices"]:
            return UNSUPPORTED
        sample_size = random.randint(1, min(3, len(field["choices"])))
        return random.sample(field["choices"], sample_size)

    def _number(self, field):
        return round(random.uniform(0, 10000), 2)

    def _currency(self, field):
        return round(random.uniform(1, 5000), 2)

    def _boolean(self, field):
        return random.choice([True, False])

    def _date_time(self, field):
        value = self.faker.date_time_between(start_date="-1y", end_date="+3M")
        if field["display_format"] == 0:  # 0 == date-only, 1 == date and time
            value = value.date()
        return value.isoformat()

    def _url(self, field):
        return FieldUrlValue(self.faker.url(), self.faker.catch_phrase())

    def _guid(self, field):
        return str(uuid.uuid4())

    def _geolocation(self, field):
        return {"Latitude": float(self.faker.latitude()), "Longitude": float(self.faker.longitude())}

    def _user(self, field):
        user_ids = self._get_user_ids()
        if not user_ids:
            return UNSUPPORTED

        if field["allow_multiple_values"]:
            picked = random.sample(user_ids, k=random.randint(1, min(3, len(user_ids))))
            value = FieldMultiUserValue()
            for user_id in picked:
                value.add(FieldUserValue(user_id))
            return value
        return FieldUserValue(random.choice(user_ids))

    def _lookup(self, field):
        if not field["lookup_list"]:
            return UNSUPPORTED
        candidates = self._get_lookup_items(field["lookup_list"])
        if not candidates:
            return UNSUPPORTED

        if field["allow_multiple_values"]:
            picked = random.sample(candidates, k=random.randint(1, min(3, len(candidates))))
            value = FieldMultiLookupValue()
            for lookup_id, lookup_value in picked:
                value.add(FieldLookupValue(lookup_id, lookup_value))
            return value
        lookup_id, lookup_value = random.choice(candidates)
        return FieldLookupValue(lookup_id, lookup_value)

    def _taxonomy(self, field):
        if not field["term_set_id"]:
            return UNSUPPORTED
        terms = self._get_terms(field["term_set_id"])
        if not terms:
            return UNSUPPORTED

        if field["type_as_string"] == "TaxonomyFieldTypeMulti":
            picked = random.sample(terms, k=random.randint(1, min(3, len(terms))))
            return TaxonomyFieldValueCollection([
                TaxonomyFieldValue(term["label"], term["id"], -1) for term in picked
            ])
        term = random.choice(terms)
        return TaxonomyFieldValue(term["label"], term["id"], -1)

    _HANDLERS = {
        "Text": _text,
        "Note": _note,
        "Choice": _choice,
        "MultiChoice": _multi_choice,
        "Number": _number,
        "Currency": _currency,
        "Boolean": _boolean,
        "DateTime": _date_time,
        "URL": _url,
        "Guid": _guid,
        "Geolocation": _geolocation,
        "User": _user,
        "Lookup": _lookup,
        "TaxonomyFieldType": _taxonomy,
        "TaxonomyFieldTypeMulti": _taxonomy,
    }
