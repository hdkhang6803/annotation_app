import requests
import os 
from constant import base_path
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

class RestClient:
    _instance = None  # Private class attribute to store the single instance

    user_id = os.getenv('USER_ID')  # Public instance attribute to store the user ID

    def __new__(cls, base_url=None):
        if cls._instance is None:
            if base_url is None:
                raise ValueError("First instantiation requires a base_url.")
            cls._instance = super(RestClient, cls).__new__(cls)
            cls._instance.base_url = base_url  # Set the base URL only once
        return cls._instance

    def get_similars(self, image_name, no_return_records):
        url = f"{self.base_url.replace('8004', '8001')}/get_similar"
        payload = {"image_id": image_name, "no_return_records": no_return_records} 

        response = requests.get(url, params=payload, timeout=5)
        response.raise_for_status() 
        
        data = response.json()
        data = data['data']

        # Append base_path to each response item if needed
        for i in range(len(data)):
            data[i] = os.path.join(base_path, data[i])  
            

        return data
    
    def init(self, video_id, annotated_images, session_id=None):
        if session_id is None:
            session_id = self.user_id
        url = f"{self.base_url}/init"
        image_ids = []
        for image in annotated_images:
            image_ids.append(image.split("/")[-1])
        payload = {"user": session_id, "video_id": video_id, "prev_ann_image_ids": annotated_images}
        print(payload)

        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        if response.status_code == 200:
            return True
        else:
            print(response.text)
            return False
        
    def clear_session(self, session_id=None):
        if session_id is None:
            session_id = self.user_id
        url = f"{self.base_url}/clear"
        payload = {"user": session_id}

        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        if response.status_code == 200:
            return True
        else:
            print(response.text)
            return False
        
    def send_accepted_data(self, accepted_images, session_id=None):
        if session_id is None:
            session_id = self.user_id
        url = f"{self.base_url}/update"
        payload = {"user": session_id, "new_ann_image_ids": accepted_images}
        print(payload)

        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        if response.status_code == 200:
            return True
        else:
            print(response.text)
            return False
    