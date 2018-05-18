all: sessions districts

sessions:
	python scripts/index_sessions.py

districts:
	python scripts/index_districts.py
