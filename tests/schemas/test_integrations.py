from healthchecks_io.schemas.integrations import Integration

def test_badge_from_api_result():
    int_dict = {      
      "id": "4ec5a071-2d08-4baa-898a-eb4eb3cd6941",
      "name": "My Work Email",
      "kind": "email"
    }
    this_integration = Integration.from_api_result(int_dict)
    assert this_integration.id == int_dict['id']
    assert this_integration.name == int_dict['name']
