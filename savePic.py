import subprocess

def run_curl_command(image_filename):
    command = [
        "curl",
        "--location",
        "https://api.luxand.cloud/v2/person/48cefc17-304f-11ee-a913-0242ac120002",
        "--header",
        "token: ebcc162f5fc3445da79cf5d77c5d6b2d",
        "--form",
        f'photos=@"{image_filename}"',
        "--form",
        "store=1"
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Image {image_filename} processed successfully.")
            print("Response:", result.stdout)
        else:
            print(f"Failed to process image {image_filename}.")
            print("Error:", result.stderr)
    except Exception as e:
        print(f"An error occurred while processing image {image_filename}: {e}")

if __name__ == "__main__":
    folder_path = "/home/jov/Hubo/staff_pictures/Ritin"
    for i in range(1, 11):
        image_filename = os.path.join(folder_path, f"pic{i}.jpg")
        run_curl_command(image_filename)

