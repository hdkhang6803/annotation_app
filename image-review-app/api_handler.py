import requests

API_URL = "http://server.selab.edu.vn:20711/explore/explore_neighbor_images"

def get_neighbors(image_url, span=6):
    """Fetches neighboring images from the API."""
    payload = {"image_url": image_url, "span": span}
    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        neighbors = response.json().get("response", [])
        final_res = []
        for neighbor in neighbors:
            neighbor = neighbor["img_link"].replace("http://127.0.0.1:8000/", "").replace(".jpg", "")
            final_res.append(neighbor)
        return final_res
    return []
