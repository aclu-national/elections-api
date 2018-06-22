all: congress_sessions \
     congress_districts \
     congress_legislators \
     congress_scores \
     congress_details \
     states \
     counties \
     state_leg \
     ballotpedia_races \
     elections \
     targeted \
     blurbs

congress_sessions:
	python scripts/index_congress_sessions.py

congress_districts:
	python scripts/index_congress_districts.py

congress_legislators:
	python scripts/index_congress_legislators.py

congress_scores:
	python scripts/index_congress_scores.py

congress_details:
	python scripts/index_congress_details.py

states:
	python scripts/index_states.py

counties:
	python scripts/index_counties.py

state_leg:
	python scripts/index_state_leg.py

ballotpedia_races:
	python scripts/index_ballotpedia_races.py

elections:
	python scripts/index_elections.py

targeted:
	python scripts/index_targeted.py

blurbs:
	python scripts/index_blurbs.py
