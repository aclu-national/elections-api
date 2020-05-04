all: congress_sessions \
     congress_districts \
     congress_legislators \
     congress_details \
     congress_scores \
     states \
     counties \
     state_leg \
     elections \
     blurbs \
     aclu_ids

congress_sessions:
	python scripts/index_congress_sessions.py

congress_districts:
	python scripts/index_congress_districts.py

congress_legislators:
	python scripts/index_congress_legislators.py

congress_scores:
	python scripts/index_congress_scores.py 115 --reset
	python scripts/index_congress_scores.py 116

congress_details:
	python scripts/index_congress_details.py 115 --reset
	python scripts/index_congress_details.py 116

states:
	python scripts/index_states.py

counties:
	python scripts/index_counties.py

state_leg:
	python scripts/index_state_leg.py

elections:
	python scripts/index_elections.py

blurbs:
	python scripts/index_blurbs.py

aclu_ids:
	python scripts/index_aclu_ids.py

decache:
	python scripts/decache_google_civic_info.py

election_races:
	python scripts/index_election_races.py
	psql ${DATABASE_URL} < sources/aclu/aclu_election_races.sql

election_candidates:
	python scripts/index_election_candidates.py

targeted:
	python scripts/index_targeted.py
