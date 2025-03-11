import requests
import argparse
from libs.beans import Pusher
from config.settings import BEANS

# URL API
PROJECTS_URL = 'https://v5.external.dashboard.nolimit.id/project-management/projects/list?is_active=true'
OBJECTS_URL = 'https://v5.external.dashboard.nolimit.id/project-management/projects/object-list?project_id={}'

def get_projects():
    """Ambil daftar proyek yang aktif dari API."""
    response = requests.get(PROJECTS_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching projects: {response.status_code}")
        return []

def get_project_objects(project_id):
    url = OBJECTS_URL.format(project_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching objects for project {project_id}: {response.status_code}")
        return []

def main(priority_level, priority, project_id=None):
    projects = get_projects()
    
    if not projects:
        print("Tidak ada proyek yang ditemukan.")
        return
    
    objects = []
    
    if project_id:
        objects = get_project_objects(project_id)
    else:
        for project in projects:
            objects.extend(get_project_objects(project["uuid"]))
    
    # Filter objek berdasarkan kriteria
    filtered_objects = [
        obj for obj in objects if obj.get("socialMedia") == "instagram" 
        and obj.get("streamType") == "keyword"
    ]

    if not filtered_objects:
        print("Tidak ada objek yang memenuhi kriteria.")
        return
    
    # Tentukan antrean
    tubename = '{}_crawler_instagram_hashtag'.format(BEANS['default']['prefix'])
    pusher = Pusher(tubename, host=BEANS['default']['host'], port=BEANS['default']['port'])

    for obj in filtered_objects:
        message = f"{obj['content']}|{obj['extraContent']}" if obj.get("extraContent") else obj["content"]
        pusher.setJob(message, priority=priority if priority else priority_level * 100)
        print(f"Pushed: {message}")

    pusher.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Push Instagram Hashtag to Queue")
    parser.add_argument("--priority-level", type=int, default=1, help="Priority Level")
    parser.add_argument("--priority", type=int, default=None, help="Priority")
    parser.add_argument("--project-id", type=str, help="Project ID (optional)")

    args = parser.parse_args()
    main(args.priority_level, args.priority, args.project_id)
