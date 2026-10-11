.PHONY: test demo run lint clean

test:
	python -m pytest agents/tests -v

demo:
	python scripts/demo.py

run:
	python -m uvicorn agents.main:app --host 0.0.0.0 --port 8002 --reload

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
