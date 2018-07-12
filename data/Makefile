all: congress_districts_115 \
     congress_districts_116_pa \
     congress_legislators \
     congress_photos \
     states \
     counties \
     state_leg \
     simplify_geometries

congress_districts_115:
	python ../scripts/data_congress_districts_tiger.py --start 115 --end 115

congress_districts_116_pa:
	python ../scripts/data_congress_districts_116_pa.py

congress_legislators:
	python ../scripts/data_congress_legislators.py

congress_photos:
	../scripts/data_congress_photos.sh

states:
	python ../scripts/data_states.py

counties:
	python ../scripts/data_counties.py

state_leg:
	python ../scripts/data_state_leg.py

simplify_geometries:
	python ../scripts/data_simplify_geometries.py
