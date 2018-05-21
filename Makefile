all: sessions districts legislators

sessions:
	python scripts/index_sessions.py

districts:
	python scripts/index_districts.py

legislators:
	python scripts/index_legislators.py
