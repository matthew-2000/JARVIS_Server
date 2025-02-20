import os
import requests

def test_audio_files(server_url, test_folder):
    files = [f for f in os.listdir(test_folder) if f.endswith((".wav", ".mp3"))]

    for file in files:
        file_path = os.path.join(test_folder, file)
        print(f"Testing {file}...")

        with open(file_path, "rb") as audio:
            response = requests.post(
                f"{server_url}/process_audio",
                files={"audio": audio}
            )

        if response.status_code == 200:
            print(f"Success: {response.json()}")
        else:
            print(f"Error ({response.status_code}): {response.text}")

if __name__ == "__main__":
    SERVER_URL = "http://127.0.0.1:5000"
    TEST_FOLDER = "test_files"
    test_audio_files(SERVER_URL, TEST_FOLDER)
