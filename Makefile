all: congress_sessions \
     congress_districts \
     congress_legislators \
     congress_scores \
     congress_details \
     states \
     counties \
     state_leg \
     elections \
     election_races \
     targeted \
     blurbs \
     aclu_ids

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

elections:
	python scripts/index_elections.py

election_races:
	python scripts/index_election_races.py

targeted:
	python scripts/index_targeted.py

blurbs:
	python scripts/index_blurbs.py

aclu_ids:
	python scripts/index_aclu_ids.py
