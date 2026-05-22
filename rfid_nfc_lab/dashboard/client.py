#!/usr/bin/env python3
"""Lightweight client to push events to the dashboard"""
import time
try:
    import requests
except Exception:
    requests = None

DASHBOARD_URL = 'http://127.0.0.1:8080/api/log'

def send_event(evt: dict) -> None:
    """Send an event to the dashboard; fail silently if unavailable."""
    if requests is None:
        return
    try:
        requests.post(DASHBOARD_URL, json=evt, timeout=0.5)
    except Exception:
        # best-effort only
        return
