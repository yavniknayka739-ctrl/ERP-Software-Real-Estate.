def test_login_success(client, admin_user):
    client.cookies.set("csrf_token", "test-token")
    response = client.post("/login", data={"username": "admin_test", "password": "pass", "csrf_token": "test-token"})
    assert response.status_code == 200

def test_login_failure(client, admin_user):
    client.cookies.set("csrf_token", "test-token")
    response = client.post("/login", data={"username": "admin_test", "password": "wrong", "csrf_token": "test-token"})
    assert b"Invalid username or password" in response.content

def test_unauthorized_access(client):
    response = client.get("/clients/")
    assert response.status_code == 401

def test_rbac_commercial_dashboard_forbidden_for_tech(tech_client):
    response = tech_client.get("/dashboard/commercial")
    assert response.status_code == 403

def test_rbac_commercial_dashboard_allowed_for_comm(comm_client):
    response = comm_client.get("/dashboard/commercial")
    assert response.status_code == 200
