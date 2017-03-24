curl -H "Content-Type: application/json" -X POST -d '{"command":"read_session_vars","cookie":"abc123","session_keys":["first_key","second_key"]}' http://localhost:8000/api
