.PHONY: test demo seed reset run run-gate run-agents lint clean

test:
	python -m pytest agents/tests -v --tb=short --ignore=agents/tests/test_live_openai_smoke.py

demo:
	python scripts/demo.py

seed:
	python scripts/seed.py

reset:
	python scripts/reset.py

run:
	python -m uvicorn agents.main:app --host 0.0.0.0 --port 8002 --reload

run-gate:
	python -m uvicorn actiongate.main:app --host 0.0.0.0 --port 8001 --reload

run-agents:
	python -m uvicorn agents.main:app --host 0.0.0.0 --port 8002 --reload

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
