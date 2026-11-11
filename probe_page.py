import streamlit as st

st.title('Karte minimal route probe')
st.write('Synthetic-only experiment. No athlete data or API keys are configured.')
st.code('GET /api/karte/v1/health\nGET /api/karte/v1/echo')
st.caption(f'Streamlit {st.__version__}')
