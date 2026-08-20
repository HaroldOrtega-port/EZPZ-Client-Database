import pytest
from app import create_app, db, Client

@pytest.fixture()
def app():
    return create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "SECRET_KEY": "test"})

@pytest.fixture()
def client(app):
    return app.test_client()

def test_complete_client_crud_with_repeatable_people(app, client):
    payload = {"name":"Apartment Corp","status":"active","industry":"Property Management","client_since":"2023-06-07","contracted_hours":"200","schedule_mode":"individual","contact_role[]":["CEO","Operations Manager"],"contact_name[]":["Marc Menowitz","Nicole Chriqui"],"contact_email[]":["marc@example.com","nicole@example.com"],"contact_phone[]":["111","222"],"team_role[]":["Account Executive","Accounting Clerk"],"team_name[]":["Peter Jorgenson","Ruth Arances"],"team_email[]":["peter@ezpz.com","ruth@ezpz.com"],"team_work_days[]":["Tue,Wed,Thu,Fri","Mon,Tue,Wed,Thu,Fri"],"team_start_time[]":["08:00","05:00"],"team_end_time[]":["18:00","16:00"]}
    response = client.post("/clients/new", data=payload)
    assert response.status_code == 302
    page = client.get(response.headers["Location"])
    assert b"Apartment Corp" in page.data and b"Marc Menowitz" in page.data and b"Peter Jorgenson" in page.data
    assert b"Tue-Fri 8 AM - 6 PM" in page.data
    with app.app_context():
        saved = db.session.get(Client, 1)
        assert saved.status == "active" and len(saved.contacts) == 2 and len(saved.team_members) == 2
    updated = client.post("/clients/1/edit", data={"name":"Apartment Corp","status":"inactive","contact_name[]":["Marc Menowitz"]}, follow_redirects=True)
    assert b"Inactive" in updated.data
    assert b"Apartment Corp" in client.get("/?status=inactive").data
    assert b"Client profile deleted" in client.post("/clients/1/delete", follow_redirects=True).data

def test_client_name_validation(client):
    response = client.post("/clients/new", data={"name":"","status":"active"}, follow_redirects=True)
    assert b"Client name is required" in response.data

def test_form_timezone_options_and_directory_status_groups(client):
    form = client.get("/clients/new")
    for label in (b"Eastern Time (ET)", b"Central Time (CT)", b"Mountain Time (MT)", b"Pacific Time (PT)"):
        assert label in form.data
    assert b'name="time_check_url"' not in form.data
    assert b"https://www.worldtimebuddy.com/" in form.data
    client.post("/clients/new", data={"name":"Active Co","status":"active","time_zone":"Eastern Time (ET)"})
    client.post("/clients/new", data={"name":"Inactive Co","status":"inactive","time_zone":"Pacific Time (PT)"})
    directory = client.get("/")
    assert b"_5-Client Operations" in directory.data
    assert b"04-Active Clients" in directory.data and b"05-Inactive Clients" in directory.data
    profile = client.get("/clients/1")
    assert b"https://www.worldtimebuddy.com/" in profile.data

def test_shared_team_schedule(client):
    response = client.post("/clients/new", data={"name":"Shared Schedule Co","status":"active","schedule_mode":"shared","shared_work_days":"Mon-Thu","shared_start_time":"07:00","shared_end_time":"19:00","team_name[]":["Alex","Taylor"],"team_role[]":["Clerk","Manager"],"team_email[]":["a@example.com","t@example.com"]})
    profile = client.get(response.headers["Location"])
    assert profile.data.count(b"Mon-Thu 7 AM - 7 PM") == 2
    form = client.get("/clients/1/edit")
    assert b"Same schedule for everyone" in form.data and b"Set schedule for each member" in form.data
    assert form.data.count(b'class="day-option') >= 14
    assert b'type="time"' not in form.data
    assert b'<option value="07:00"' in form.data and b'>7:00 AM</option>' in form.data

def test_all_clients_table_view_contains_searchable_details(client):
    client.post("/clients/new", data={"name":"Table View Client","status":"active","industry":"Healthcare","time_zone":"Central Time (CT)","contact_name[]":["Pat Contact"],"contact_email[]":["pat@client.com"],"team_name[]":["Jamie Team"],"team_role[]":["Bookkeeper"],"team_email[]":["jamie@ezpz.com"],"schedule_mode":"shared","shared_work_days":"Mon,Tue,Wed,Thu","shared_start_time":"07:00","shared_end_time":"18:00"})
    page = client.get("/?view=table")
    assert page.status_code == 200
    for text in (b"Search across all client details", b"Table View Client", b"Healthcare", b"Pat Contact", b"Jamie Team", b"Mon-Thu 7 AM - 6 PM"):
        assert text in page.data
    assert b'id="client-directory-table"' in page.data

def test_multiple_sop_resource_links(client):
    response = client.post("/clients/new", data={"name":"Multi Resource Client","status":"active","sop_url":"https://example.com/bookkeeping","sop_url_label":"Bookkeeping","sop_url_secondary":"https://example.com/admin","sop_url_secondary_label":"Administrative Support (CAM)"})
    profile = client.get(response.headers["Location"])
    assert b"Bookkeeping" in profile.data
    assert b"Administrative Support (CAM)" in profile.data

def test_marketing_software_field(client):
    response = client.post("/clients/new", data={"name":"Marketing Client","status":"active","marketing_software":"Buildout, Canva"})
    profile = client.get(response.headers["Location"])
    assert b"Marketing Software:" in profile.data and b"Buildout, Canva" in profile.data
