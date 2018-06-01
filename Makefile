all: congress_sessions \
     congress_districts \
     congress_legislators \
     congress_scores \
     states \
     counties \
     state_leg

congress_sessions:
	python scripts/index_congress_sessions.py

congress_districts:
	python scripts/index_congress_districts.py

congress_legislators:
	python scripts/index_congress_legislators.py

congress_scores:
	python scripts/index_congress_scores.py

states:
	python scripts/index_states.py

counties:
	python scripts/index_counties.py

state_leg:
	python scripts/index_state_leg.py
