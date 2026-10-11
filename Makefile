.PHONY: test attacks attack-lab demo run lint clean

test:
	python -m pytest agents/tests attacks/tests/test_attack_lab.py -v --tb=short

attacks:
	python attacks/runner/run_attacks.py

attack-lab:
	python -m webbrowser "file://$(CURDIR)/attacks/lab-ui/index.html"

demo:
	python scripts/demo.py

run:
	python -m uvicorn agents.main:app --host 0.0.0.0 --port 8002 --reload

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
