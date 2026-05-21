from tools import _extract_json_from_text

tests = [
    '{"a":1}',
    'Here is JSON:\n```json\n{"hcp_name":"Dr. Smith"}\n```',
    'No JSON here'
]

for i, t in enumerate(tests, 1):
    try:
        print(f"TEST{i}", _extract_json_from_text(t))
    except Exception as e:
        print(f"TEST{i}-ERR", e)
