"""Minimal synthetic-only Community Cloud custom-route experiment."""
import streamlit as st
from starlette.responses import JSONResponse
from starlette.routing import Route


async def health(request):
    return JSONResponse({'ok': True})


async def echo(request):
    return JSONResponse({
        'authorization_present': 'authorization' in request.headers,
        'if_match_present': 'if-match' in request.headers,
        'range_present': 'range' in request.headers,
    })


app = st.App('probe_page.py', routes=[
    Route('/api/karte/v1/health', health, methods=['GET']),
    Route('/api/karte/v1/echo', echo, methods=['GET']),
])
