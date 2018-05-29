all: sessions districts legislators scores counties

sessions:
	python scripts/index_sessions.py

districts:
	python scripts/index_districts.py

legislators:
	python scripts/index_legislators.py

scores:
	python scripts/index_scores.py

states:
	python scripts/index_states.py

counties:
	python scripts/index_counties.py
