DELETE FROM election_races
WHERE state = 'ca'
  AND office_type = 'district_attorney'
  AND ocd_id IN (
	'ocd-division/country:us/state:ca/county:alameda',
	'ocd-division/country:us/state:ca/county:fresno',
	'ocd-division/country:us/state:ca/county:orange',
	'ocd-division/country:us/state:ca/county:riverside',
	'ocd-division/country:us/state:ca/county:sacramento',
	'ocd-division/country:us/state:ca/county:san_bernardino',
	'ocd-division/country:us/state:ca/county:san_diego',
	'ocd-division/country:us/state:ca/county:san_joaquin',
	'ocd-division/country:us/state:ca/county:santa_clara'
);
