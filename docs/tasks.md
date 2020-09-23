[*ACLU Elections API*](https://github.com/aclu-national/elections-api)

# Common Tasks

Note that all references to scorecard data can be ignored if you are not running the ACLU instance of the Elections API, since that part depends on a private data repo.

## A legislator has left office

Once a given legislator leaves office the following things should happen:

1. Update the `congress_legislators` source (delete the `congress_legislators` directory and then run `make congress_legislators` from the sources folder), assuming the [unitedstates source repo](https://github.com/unitedstates/congress-legislators) is updated
2. Update the `data` records: `python scripts/data_congress_legislators.py`
3. Commit/push any changed JSON records
4. Update the current scorecard spreadsheet
5. Run `make` from `elections-api-private` to download the scorecard CSVs
6. Run the following commands locally, from the elections-api root:  
    ```
    make congress_legislators
    make congress_details
    make congress_scores
    ```
7. From the product-dev-ops directory, deploy to staging:
    ```
    ./scripts/api-deploy.sh elections-stg "make congress_legislators && make congress_details && make congress_scores"
    ```
8. If things look okay on staging, deploy it on production:
    ```
    ./scripts/api-deploy.sh elections "make congress_legislators && make congress_details && make congress_scores"
    ```

## A legislator was running for president, but they've dropped out

1. Update the "Congress Legislator Details" spreadsheet
2. Download the CSV and save it as `sources/aclu/aclu_[chamber]_[session].csv` (depending on the current session and whether the legislator is a House Rep or a Senator)
3. Run the following commands locally, from the elections-api root:  
    ```
    make congress_details
    make congress_scores
    ```
4. From the product-dev-ops directory, deploy to staging:
    ```
    ./scripts/api-deploy.sh elections-stg "make congress_details && make congress_scores"
    ```
5. If things look okay on staging, deploy it on production:
    ```
    ./scripts/api-deploy.sh elections "make congress_details && make congress_scores"
    ```

You might be wondering, "why should we `make congress_scores` if this is only updating the details spreadsheet? The reason is that we store some aggregate scorecard data in the details table, so that means rebuilding the details table will erase all those scorecard-related values.
