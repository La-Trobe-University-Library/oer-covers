# Copyright

Other than any prior works of which it is a derivative, the copyright in this work is owned by La Trobe University.

# Licenses

Rights of use and distribution are granted under the terms of the GNU Affero General Public License version 3 (AGPL-3.0). You should find a copy of this license in the root of the repository.

# Acknowledgements

La Trobe University Library is grateful to [all who have contributed to this project](ACKNOWLEDGEMENTS.md).

# Contact

The maintainer of this repository is Hugh Rundle, who can be contacted at h.rundle@latrobe.edu.au

# Description 

This is a basic Python script for scraping book covers for Open Educational Resources for import into Ex Libris Alma.

The script takes an input file which should be an export from Alma converted to CSV format.

Run the script against a file exported from Alma with your OER URLs. It will produce an `xlsx` file with all the cover images it can find for the books in your list. You can then import this file back into Alma to update your local records.

## Installation

This is a Python script. An easy way to run it is to use [the `uv` package and project manager](https://docs.astral.sh/uv). Install `uv` according to [their instructions](https://docs.astral.sh/uv/getting-started/installation).

## Preparing your source file

The script operates on a report exported from Alma Analytics. To recreate it in Alma Analytics:

1. In Subject area E-Inventory:

    *Select*
    * Electronic Collection - Electronic Collection Public Name
    * Bibliographic Details - Title
    * Bibliographic Details - MMS Id
    * Portfolio URL Information - Portfolio Static URL
    * Portfolio URL Information - Portfolio Static URL (override)
    * Portfolio URL Information - Portfolio URL Type
    * Portfolio URL Information - Portfolio Parser Parameters
    * Electronic Collection URL Information - Electronic Collection Level URL

    *Filters*:
    
    Filter to your requirements, e.g.

    * Electronic Collection Public Name is equal to / is in  CAUL OER Collective; La Trobe University eBureau; Milne Open Textbooks (Open SUNY Textbooks); OpenStax College; OAPEN
    * `AND`	 Availability is equal to / is in  Available
    * `AND`	 Lifecycle is equal to / is in  In Repository
 
or if you prefer SQL:

```sql
SELECT
0 s_0,
"E-Inventory"."Bibliographic Details"."MMS Id" s_1,
"E-Inventory"."Bibliographic Details"."Title" s_2,
"E-Inventory"."Electronic Collection URL Information"."Electronic Collection Level URL" s_3,
"E-Inventory"."Electronic Collection"."Electronic Collection Public Name" s_4,
"E-Inventory"."Portfolio URL Information"."Portfolio Parser Parameters" s_5,
"E-Inventory"."Portfolio URL Information"."Portfolio Static URL (override)" s_6,
"E-Inventory"."Portfolio URL Information"."Portfolio Static URL" s_7,
"E-Inventory"."Portfolio URL Information"."Portfolio URL Type" s_8
FROM "E-Inventory"
WHERE
(("Electronic Collection"."Electronic Collection Public Name" IN ('CAUL OER Collective', 'La Trobe University eBureau', 'Milne Open Textbooks (Open SUNY Textbooks)', 'OpenStax College', 'OAPEN')) AND ("Portfolio"."Availability" = 'Available') AND ("Portfolio"."Lifecycle" = 'In Repository'))
ORDER BY 5 ASC NULLS FIRST, 3 ASC NULLS FIRST, 2 ASC NULLS FIRST, 8 ASC NULLS FIRST, 7 ASC NULLS FIRST, 9 ASC NULLS FIRST, 4 ASC NULLS FIRST, 6 ASC NULLS FIRST
FETCH FIRST 10000001 ROWS ONLY
```

## Running the script

Then run the script from a terminal/PowerShell:

`uv run oer_cover_scraper.py inputfilename outputfilename` 

_inputfilename_ should be your file exported from Alma and converted to csv.
_outputfilename_ should be a new `.xslx` filename that will contain the output.

e.g.

```sh
uv run oer_cover_scraper.py alma_export.csv output_file.xslx
```

## Importing the output file

Once you have your output file, you need to do something with it!

In Alma: 

1. Click on `Resources > Import`. 
2. Locate the Load cover images import profile.
3. Click on the ellipsis button and select Run.
4. Select the spreadsheet as the file to load.
5. Click Submit.

The job will add the 956 field to matching bibliographic records. This may take a few hours to show up in your discovery interface.

## Logging

The script will spit out errors including HTTP errors. You might like to send them to a log file rather than your terminal:

```sh
uv run oer_cover_scraper.py source_file.csv output_file.xslx >> logfile.txt
```

## Image sources

Currently this will only work for books from:

* latrobe.edu.au
* library.oapen.org
* milneopentextbooks.org
* oercollective.caul.edu.au

You can add your own or log an Issue with a request for a new source. 
Note that Rice University inexplicably reserves all copyrights on OpenStax book covers, so they cannot be used.