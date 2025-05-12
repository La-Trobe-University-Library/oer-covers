from bs4 import BeautifulSoup
import csv
import requests
import sys
import time
from urllib.parse import urlparse
import xlsxwriter


def get_cover_image(row):
    """find the URL of the cover image and add it to a row in the export file"""

    # for each link, use Beautiful Soup to find the image URL
    if row["URL"]:
        raw_url = row["URL"].strip() # remove any spaces on either end
        url = raw_url.split(" ")[0] # remove anything after the URL e.g. providerid from parser parameters

        try:

            if "open.umn.edu" in url: # OTL is rate-limited, avoid 429 errors by slowing down
                time.sleep(1) 
            headers = {"user-agent": "OER-Covers-Retry/0.0.1"} # don't use a generic user agent
            page = requests.get(url, headers=headers)
            page.raise_for_status() # raise the error immediately if we didn't get a successful page load
            soup = BeautifulSoup(page.content, "html.parser")

            # each source will have the images in a different element, choose the right one
            source = ""

            pressbooks = ["oercollective.caul.edu.au", "jcu.pressbooks.pub", "milnepublishing.geneseo.edu"]
            if any(x in url for x in pressbooks): # Pressbooks sites
                source = soup.find("div", class_="book-header__cover__image").find("img")["src"]

            elif "latrobe.edu.au" in url: # La Trobe eBureau
                images = soup.find_all("img")
                sources = [image["src"] for image in images if "book-covers" in image["src"]]
                if len(sources) > 0:
                    source = sources[0]
                else:
                    return 

            elif "milneopentextbooks.org" in url: #Milne Library Publishing at SUNY Geneseo
                figures = soup.find_all("figure")
                for fig in figures:
                    if fig.find("img") and "wp-content/uploads" in fig.find("img")["src"]:
                        source = fig.find("img")["src"]
                        break # only break from this loop

            elif "library.oapen.org" in url: # OAPEN
                raw_source = soup.find("img", class_="img-thumbnail")["src"]
                source = f"https://library.oapen.org/{raw_source}"


            elif "open.umn.edu" in url: # Open Textbook Library
                source = soup.find("div", id="cover").find("img")["src"]

                if "placeholder" in source:
                    return # don't bother with the relative placeholder paths from OTL

            elif "openstax.org" in url: # OpenStax
                # openstax book covers are All Rights Reserved Rice University
                # so cannot be used
                return

            else:
                # we don't know about that source - log an issue so it can be added :)
                p = urlparse(url)
                print(f"Cannot parse from this OER source: {p.hostname}")
                return

            # add the image url to the entry for that book
            data = (str(row["MMS Id"]), source, "Thumbnail", "local", str(row["MMS Id"]))
            return {"type": "cover", "data": data}

        except requests.exceptions.HTTPError:

            data = (str(row["MMS Id"]), url, page.status_code)
            return {"type": "error", "data": data}

        except requests.exceptions.ConnectionError:

            data = (str(row["MMS Id"]), url, "ConnectionError")
            return {"type": "error", "data": data}

        except KeyboardInterrupt:

            exit()

        except Exception as e:

            # Something else went wrong
            print(row["MMS Id"], type(e), e)
            return

    else:
        # it's empty
        return

if __name__ == '__main__':
    """When the script is called..."""

    # csv/xlsx file names
    # you may need to adjust these depending how you call the script
    source_file = sys.argv[1]
    output_file = sys.argv[2]

    # set up
    workbook = xlsxwriter.Workbook(output_file)
    
    worksheet = workbook.add_worksheet("covers_for_upload")
    worksheet.write_row("A1", ("001","95642$u", "95642$3","95642$9","MMS Id"))

    errors = workbook.add_worksheet("errors") 
    errors.write_row("A1", ("MMS Id", "URL", "Error code")) 

    #  read csv of book URLs
    with open(source_file, "r") as csvfile:
        reader = csv.DictReader(csvfile)

        index = 2
        error_index = 2

        # run get_cover_image() for each row, the slow way
        # the most likely errors are 404 and 429
        for row in reader:
            value = get_cover_image(row)
            if value:
                if value.get("type") == "error":
                    errors.write_row(f"A{error_index}", value["data"])
                    error_index += 1
                else:
                    worksheet.write_row(f"A{index}", value["data"])
                    index += 1

    workbook.close()