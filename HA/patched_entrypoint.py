#!/usr/bin/env python3
"""Startup wrapper that fixes DCL timeout issues."""
import os
import sys
import asyncio

print("[patched_entrypoint] Starting up...", flush=True)

# Import aiohttp first
from aiohttp import ClientSession, ClientTimeout

_fetch_timeout = ClientTimeout(total=30)

# Patch strategy: import the server module first (which binds original functions),
# then override those bindings.

# First, import the server module to trigger all module-level imports
import matter_server.server.server as srv_mod
print("[patched_entrypoint] Server module loaded", flush=True)

# Now patch vendor_info
import matter_server.server.vendor_info as vi_mod
print("[patched_entrypoint] Vendor info module loaded", flush=True)

_orig_fetch = vi_mod.VendorInfo._fetch_vendors

async def patched_fetch(self):
    import logging
    LOGGER = logging.getLogger(__name__)
    LOGGER.info("Fetching vendor info from DCL (patched with 30s timeout).")
    vendors = {}
    try:
        async with ClientSession(raise_for_status=True, timeout=_fetch_timeout) as session:
            page_token = ""
            while page_token is not None:
                async with session.get(
                    f"{vi_mod.PRODUCTION_URL}/dcl/vendorinfo/vendors",
                    params={"pagination.key": page_token},
                ) as response:
                    data = await response.json()
                    for vendorinfo in data["vendorInfo"]:
                        vendors[vendorinfo["vendorID"]] = vi_mod.VendorInfoModel(
                            vendor_id=vendorinfo["vendorID"],
                            vendor_name=vendorinfo["vendorName"],
                            company_legal_name=vendorinfo["companyLegalName"],
                            company_preferred_name=vendorinfo["companyPreferredName"],
                            vendor_landing_page_url=vendorinfo["vendorLandingPageURL"],
                            creator=vendorinfo["creator"],
                        )
                    page_token = data.get("pagination", {}).get("next_key", None)
    except Exception as err:
        LOGGER.error("Unable to fetch vendor info from DCL: %s", err)
    else:
        LOGGER.info("Fetched %s vendors from DCL.", len(vendors))
    self._data.update(vendors)

vi_mod.VendorInfo._fetch_vendors = patched_fetch
print("[patched_entrypoint] Vendor info patched", flush=True)

# Patch PAA certs - override the binding in the server module
_orig_fetch_certs = srv_mod.fetch_certificates

async def patched_fetch_certs(*args, **kwargs):
    print("[patched_entrypoint] PAA cert fetch called, timeout=30s", flush=True)
    try:
        result = await asyncio.wait_for(_orig_fetch_certs(*args, **kwargs), timeout=30)
        print("[patched_entrypoint] PAA cert fetch completed", flush=True)
        return result
    except asyncio.TimeoutError:
        print("[patched_entrypoint] PAA cert fetch TIMED OUT", flush=True)
        return

srv_mod.fetch_certificates = patched_fetch_certs
print("[patched_entrypoint] PAA cert fetch patched", flush=True)

# Now import and run main
from matter_server.server.__main__ import main
print("[patched_entrypoint] Starting main()...", flush=True)
sys.exit(main())
