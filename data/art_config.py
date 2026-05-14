"""Card art URL resolution.

Convention: every card with art lives at
``art/<kind>/<card_id>.webp`` in the repo root, where ``<kind>`` is
``maid`` | ``tool`` | ``chaos`` | ``raid_boss``. The plugin builds the
public URL from ``BASE_URL`` + the convention path at runtime — no
need to maintain a list as long as filenames match card IDs.

``OVERRIDES`` lets you point a specific card at any URL (handy for
non-webp files, cross-repo assets, or per-card CDN overrides).

If a card has no art (file missing AND no override), the embed renders
without an image — exactly the text card view we already had.

WebP was picked over PNG because:
  - Discord supports it natively in embeds.
  - File sizes are 5-6x smaller than equivalent PNG at the same
    visible quality — keeps the repo lean and embeds snappy on mobile.
"""
from __future__ import annotations

# Public base URL where the art directory is served. The art lives on
# a separate ``card-art`` branch in this repo so the plugin's ``main``
# branch stays under the platform's 10 MB GitHub-fetch limit. GitHub
# raw serves any branch, so swap the branch name here if the assets
# ever move (e.g. to a dedicated CDN).
BASE_URL = "https://raw.githubusercontent.com/NotUSeee/Maid-Mayhem/card-art/art"

# Default extension for convention-derived URLs.
DEFAULT_EXT = "webp"


# Per-card URL overrides. Keyed by ``f"{kind}/{card_id}"``. Map to any
# fully-qualified URL. Useful for off-repo CDNs, animated GIFs for
# Mythic cards, or temporary placeholders.
#
# Example::
#
#     OVERRIDES = {
#         "maid/aurelia": "https://example.com/aurelia-animated.gif",
#         "tool/golden_feather_duster": "https://imgur.com/xyz.png",
#     }
OVERRIDES: dict[str, str] = {}


# Cards we know lack art so we can suppress 404 fetches by Discord.
# Populate as you ship art per-card. Listing cards here is purely an
# optimisation — Discord will silently 404 anyway, just less cleanly.
KNOWN_MISSING: set[str] = set()


def image_url_for(kind: str, card_id: str) -> str | None:
    """Return the public image URL for a card, or None if no art is
    expected to exist. Always returns None when ``card_id`` is empty.
    """
    if not card_id or not kind:
        return None
    key = f"{kind}/{card_id}"
    if key in OVERRIDES:
        return OVERRIDES[key]
    if key in KNOWN_MISSING:
        return None
    if not BASE_URL:
        return None
    return f"{BASE_URL.rstrip('/')}/{kind}/{card_id}.{DEFAULT_EXT}"
