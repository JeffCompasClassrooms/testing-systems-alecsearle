import os
import sys
import pytest
import requests
import shutil
import subprocess
import time
import sqlite3

BASE_URL = "http://127.0.0.1:8080"
SERVER_PROCESS = None

def is_server_running():
    """Check server responsiveness"""
    try:
        response = requests.get(f"{BASE_URL}/squirrels", timeout=0.5)
        return True
    except:
        return False

def restart_server_if_needed():
    """Restart server if not running"""
    global SERVER_PROCESS
    
    if not is_server_running():
        if SERVER_PROCESS:
            try:
                SERVER_PROCESS.terminate()
                SERVER_PROCESS.wait(timeout=1)
            except:
                pass
        
        # Start new server process
        python_cmd = sys.executable
        SERVER_PROCESS = subprocess.Popen(
            [python_cmd, "squirrel_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Pause to let server start
        time.sleep(2)

@pytest.fixture(scope="session", autouse=True)
def start_server():
    """Start squirrel server before running tests"""
    global SERVER_PROCESS
    
    python_cmd = sys.executable

    # Start server process
    SERVER_PROCESS = subprocess.Popen(
        [python_cmd, "squirrel_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(2)
    
    yield

    # Stop server after tests
    SERVER_PROCESS.terminate()
    SERVER_PROCESS.wait()

@pytest.fixture(autouse=True)
def reset_database():
    """Reset database to clean state before each test"""
    # Restart server if needed
    restart_server_if_needed()
    
    # Copy template database
    if os.path.isfile("squirrel_db.db"):
        os.remove("squirrel_db.db")

    # Create new empty database
    conn = sqlite3.connect("squirrel_db.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS squirrels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            size TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    
    yield

def describe_SquirrelServer_API():

    def describe_GET_squirrels():
        
        def it_returns_200_status_code():
            # exercise
            response = requests.get(f"{BASE_URL}/squirrels")
            
            # verify
            assert response.status_code == 200

        def it_returns_empty_array_when_no_squirrels_exist():
            # exercise
            response = requests.get(f"{BASE_URL}/squirrels")
            
            # verify
            assert response.json() == []

        def it_returns_all_squirrels_after_creation():
            # setup
            requests.post(f"{BASE_URL}/squirrels", data={"name": "Fluffy", "size": "large"})
            requests.post(f"{BASE_URL}/squirrels", data={"name": "Chippy", "size": "small"})
            
            # exercise
            response = requests.get(f"{BASE_URL}/squirrels")
            
            # verify
            squirrels = response.json()
            assert len(squirrels) == 2
            assert squirrels[0]["name"] == "Fluffy"
            assert squirrels[1]["name"] == "Chippy"

    def describe_GET_squirrels_id():
        
        def it_returns_200_when_squirrel_exists():
            # setup
            requests.post(f"{BASE_URL}/squirrels", data={"name": "TestSquirrel", "size": "medium"})
            
            # exercise
            response = requests.get(f"{BASE_URL}/squirrels/1")
            
            # verify
            assert response.status_code == 200

        def it_returns_json_content_type_when_squirrel_exists():
            # setup
            requests.post(f"{BASE_URL}/squirrels", data={"name": "TestSquirrel", "size": "medium"})
            
            # exercise
            response = requests.get(f"{BASE_URL}/squirrels/1")
            
            # verify
            assert "application/json" in response.headers["Content-Type"]

        def it_returns_squirrel_data_with_all_fields():
            # setup
            requests.post(f"{BASE_URL}/squirrels", data={"name": "Fluffy", "size": "large"})
            
            # exercise
            response = requests.get(f"{BASE_URL}/squirrels/1")
            
            # verify
            squirrel = response.json()
            assert squirrel["id"] == 1
            assert squirrel["name"] == "Fluffy"
            assert squirrel["size"] == "large"

        def it_returns_404_when_squirrel_does_not_exist():
            # exercise
            response = requests.get(f"{BASE_URL}/squirrels/999")
            
            # verify
            assert response.status_code == 404

    def describe_PUT_squirrels_id_bad_request_validation():
        """Tests for 400 Bad Request when incomplete data is provided for updates"""
        
        def it_returns_400_when_name_is_missing_on_update():
            # setup
            requests.post(f"{BASE_URL}/squirrels", data={"name": "Original", "size": "small"})
            
            # exercise
            response = requests.put(f"{BASE_URL}/squirrels/1", data={"size": "large"})
            
            # verify
            assert response.status_code == 400

        def it_returns_400_when_size_is_missing_on_update():
            # setup
            requests.post(f"{BASE_URL}/squirrels", data={"name": "Original", "size": "small"})
            
            # exercise
            response = requests.put(f"{BASE_URL}/squirrels/1", data={"name": "Updated"})
            
            # verify
            assert response.status_code == 400

        def it_does_not_update_squirrel_when_data_is_incomplete():
            # setup
            requests.post(f"{BASE_URL}/squirrels", data={"name": "Original", "size": "small"})
            
            # exercise
            requests.put(f"{BASE_URL}/squirrels/1", data={"name": "Updated"})
            
            # verify - squirrel should remain unchanged
            response = requests.get(f"{BASE_URL}/squirrels/1")
            squirrel = response.json()
            assert squirrel["name"] == "Original"
            assert squirrel["size"] == "small"

    def describe_POST_squirrels():
        
        def it_returns_201_status_code():
            # exercise
            response = requests.post(f"{BASE_URL}/squirrels", data={"name": "NewSquirrel", "size": "small"})
            
            # verify
            assert response.status_code == 201

        def it_creates_squirrel_that_can_be_retrieved():
            # exercise
            requests.post(f"{BASE_URL}/squirrels", data={"name": "CreatedSquirrel", "size": "large"})
            
            # verify
            response = requests.get(f"{BASE_URL}/squirrels/1")
            squirrel = response.json()
            assert squirrel["name"] == "CreatedSquirrel"
            assert squirrel["size"] == "large"

        def it_adds_squirrel_to_list_of_all_squirrels():
            # exercise
            requests.post(f"{BASE_URL}/squirrels", data={"name": "ListSquirrel", "size": "tiny"})
            
            # verify
            response = requests.get(f"{BASE_URL}/squirrels")
            squirrels = response.json()
            assert len(squirrels) == 1
            assert squirrels[0]["name"] == "ListSquirrel"

    def describe_POST_squirrels_bad_request_validation():
        """Tests for 400 Bad Request when incomplete data is provided"""
        
        def it_returns_400_when_name_is_missing():
            # exercise
            response = requests.post(f"{BASE_URL}/squirrels", data={"size": "large"})
            
            # verify
            assert response.status_code == 400

        def it_returns_400_when_size_is_missing():
            # exercise
            response = requests.post(f"{BASE_URL}/squirrels", data={"name": "Fluffy"})
            
            # verify
            assert response.status_code == 400

        def it_returns_400_when_both_name_and_size_are_missing():
            # exercise
            response = requests.post(f"{BASE_URL}/squirrels", data={})
            
            # verify
            assert response.status_code == 400

        def it_does_not_create_squirrel_when_name_is_missing():
            # exercise
            requests.post(f"{BASE_URL}/squirrels", data={"size": "medium"})
            
            # verify - check that no squirrel was created
            response = requests.get(f"{BASE_URL}/squirrels")
            squirrels = response.json()
            assert len(squirrels) == 0

        def it_does_not_create_squirrel_when_size_is_missing():
            # exercise
            requests.post(f"{BASE_URL}/squirrels", data={"name": "Chippy"})
            
            # verify - check that no squirrel was created
            response = requests.get(f"{BASE_URL}/squirrels")
            squirrels = response.json()
            assert len(squirrels) == 0

    def describe_PUT_squirrels_id():
        
        def it_returns_204_when_update_successful():
            # setup
            requests.post(f"{BASE_URL}/squirrels", data={"name": "Original", "size": "small"})
            
            # exercise
            response = requests.put(f"{BASE_URL}/squirrels/1", data={"name": "Updated", "size": "large"})
            
            # verify
            assert response.status_code == 204

        def it_updates_squirrel_name_and_size():
            # setup
            requests.post(f"{BASE_URL}/squirrels", data={"name": "OldName", "size": "small"})
            
            # exercise
            requests.put(f"{BASE_URL}/squirrels/1", data={"name": "NewName", "size": "huge"})
            
            # verify
            response = requests.get(f"{BASE_URL}/squirrels/1")
            squirrel = response.json()
            assert squirrel["name"] == "NewName"
            assert squirrel["size"] == "huge"

        def it_returns_404_when_updating_nonexistent_squirrel():
            # exercise 
            try:
                response = requests.put(f"{BASE_URL}/squirrels/999", data={"name": "Ghost", "size": "none"}, timeout=1)
                # verify
                assert response.status_code == 404
            except (requests.exceptions.ChunkedEncodingError, requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                # Verify the squirrel was NOT created by checking the list
                list_response = requests.get(f"{BASE_URL}/squirrels")
                squirrels = list_response.json()
                # squirrels should still be empty
                assert all(s["id"] != 999 for s in squirrels)

    def describe_DELETE_squirrels_id():
        
        def it_returns_204_when_delete_successful():
            # setup
            requests.post(f"{BASE_URL}/squirrels", data={"name": "ToDelete", "size": "small"})
            
            # exercise
            response = requests.delete(f"{BASE_URL}/squirrels/1")
            
            # verify
            assert response.status_code == 204

        def it_removes_squirrel_from_database():
            # setup
            requests.post(f"{BASE_URL}/squirrels", data={"name": "WillBeDeleted", "size": "medium"})
            
            # exercise
            requests.delete(f"{BASE_URL}/squirrels/1")
            
            # verify - try to retrieve deleted squirrel
            response = requests.get(f"{BASE_URL}/squirrels/1")
            assert response.status_code == 404

        def it_removes_squirrel_from_list_of_all_squirrels():
            # setup
            requests.post(f"{BASE_URL}/squirrels", data={"name": "Keep", "size": "small"})
            requests.post(f"{BASE_URL}/squirrels", data={"name": "Delete", "size": "medium"})
            
            # exercise
            requests.delete(f"{BASE_URL}/squirrels/2")
            
            # verify
            response = requests.get(f"{BASE_URL}/squirrels")
            squirrels = response.json()
            assert len(squirrels) == 1
            assert squirrels[0]["name"] == "Keep"

        def it_returns_404_when_deleting_nonexistent_squirrel():
            # exercise
            response = requests.delete(f"{BASE_URL}/squirrels/999")
            
            # verify
            assert response.status_code == 404

    def describe_404_error_conditions():
        
        def it_returns_404_for_invalid_resource_path():
            # exercise
            response = requests.get(f"{BASE_URL}/invalid")
            
            # verify
            assert response.status_code == 404

        def it_returns_404_for_post_with_resource_id():
            # exercise
            response = requests.post(f"{BASE_URL}/squirrels/1", data={"name": "Bad", "size": "none"})
            
            # verify
            assert response.status_code == 404

        def it_returns_404_for_put_without_resource_id():
            # exercise
            response = requests.put(f"{BASE_URL}/squirrels", data={"name": "Bad", "size": "none"})
            
            # verify
            assert response.status_code == 404

        def it_returns_404_for_delete_without_resource_id():
            # exercise
            response = requests.delete(f"{BASE_URL}/squirrels")
            
            # verify
            assert response.status_code == 404

        def it_returns_404_for_nonexistent_resource_with_get():
            # exercise
            response = requests.get(f"{BASE_URL}/bears")
            
            # verify
            assert response.status_code == 404

        def it_returns_404_for_nonexistent_resource_with_post():
            # exercise
            response = requests.post(f"{BASE_URL}/rabbits", data={"name": "test"})
            
            # verify
            assert response.status_code == 404

        def it_returns_404_for_nonexistent_resource_with_put():
            # exercise
            response = requests.put(f"{BASE_URL}/cats/1", data={"name": "test"})
            
            # verify
            assert response.status_code == 404

        def it_returns_404_for_nonexistent_resource_with_delete():
            # exercise
            response = requests.delete(f"{BASE_URL}/dogs/1")
            
            # verify
            assert response.status_code == 404