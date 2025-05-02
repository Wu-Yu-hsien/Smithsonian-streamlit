import streamlit as st
import requests

def search_smithsonian_api(keyword, api_key, rows=10):
    url = "https://api.si.edu/openaccess/api/v1.0/search"
    params = {
        "q": keyword,
        "fq": "online_media_type:Images",
        "rows": rows,
        "start": 0,
        "api_key": api_key
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return []

    data = response.json()
    results = []

    for item in data.get("response", {}).get("rows", []):
        title = item.get("title", "N/A")
        edan_id = item.get("url", "").replace("edanmdm:", "")
        content = item.get("content", {})
        media = content.get("descriptiveNonRepeating", {}).get("online_media", {}).get("media", [])
        digitized = bool(media)
        image_url = media[0].get("thumbnail", "") if media else ""

        results.append({
            "title": title,
            "link": f"https://collections.si.edu/search/detail/{edan_id}",
            "digitized": digitized,
            "image": image_url
        })

    return results

# Streamlit UI
st.title("Smithsonian Digitized Collection Search")

# 🔐 安全地從 .streamlit/secrets.toml 中讀取 API Key
api_key = st.secrets["api"]["smithsonian_key"]

keyword = st.text_input("Enter a keyword to search:")
rows = st.slider("Number of results", 5, 50, 10)

if st.button("Search") and keyword:
    with st.spinner("Searching Smithsonian collections..."):
        results = search_smithsonian_api(keyword, api_key, rows=rows)

    if results:
        for r in results:
            st.markdown(f"### {r['title']}")
            st.markdown(f"**Digitized:** {'✅ Yes' if r['digitized'] else '❌ No'}")
            if r['image']:
                st.image(r['image'], width=300)
            st.markdown(f"[View on Smithsonian site]({r['link']})", unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.warning("❌ No digitized image found for this keyword. Try searching for 'mask', 'painting', or 'bird'.")
