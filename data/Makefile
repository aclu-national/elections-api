all: districts_113 districts_116_pa legislators states counties state_leg

districts_113:
	python ../scripts/build_districts_census.py --start 113 --end 115

districts_116_pa:
	python ../scripts/build_districts_116_pa.py

legislators:
	python ../scripts/build_legislators.py

states:
	python ../scripts/build_states.py

counties:
	python ../scripts/build_counties.py

state_leg:
	python ../scripts/build_state_leg.py
