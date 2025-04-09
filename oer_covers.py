from bs4 import BeautifulSoup
import csv
import requests
import sys
import xlsxwriter

# csv file names
# you may need to adjust these depending how you call the script
source_file = sys.argv[1]
output_file = sys.argv[2]


# requests headers etc
headers = {
    "user-agent": "OER-Covers-Fetcher/0.0.1"
}

# set up xlsx file
workbook = xlsxwriter.Workbook(sys.argv[2])
worksheet = workbook.add_worksheet()
worksheet.write_row("A1", ("001","95642$u", "95642$3","95642$9","Title"))
index = 2

#  read csv of book URLs
with open(source_file, "r") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # for each link, use Beautiful Soup to find the image URL
        try:
            for key in ["Portfolio Static URL", "Portfolio Static URL (override)", "Portfolio Parser Parameters"]:
                if row[key]:
                    url = row[key][5:] # remove 'jkey=' or 'bkey= '
                else:
                    # you probably need to update this OER ebook record...
                    continue

            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")

            # each source will have the images in a different element, choose the right one
            source = ""
            if "latrobe.edu.au" in url:
                images = soup.find_all("img")
                sources = [image["src"] for image in images if "book-covers" in image["src"]]
                if len(sources) > 0:
                    source = sources[0]
                else:
                    continue # if there is no image for this book, skip it
            elif "oercollective.caul.edu.au" in url:
                source = soup.find("div", class_="book-header__cover__image").find("img")["src"]
            elif "milneopentextbooks.org" in url:
                figures = soup.find_all("figure")
                for fig in figures:
                    if fig.find("img") and "wp-content/uploads" in fig.find("img")["src"]:
                        source = fig.find("img")["src"]
                        break # only break from this loop
            elif "library.oapen.org" in url:
                raw_source = soup.find("img", class_="img-thumbnail")["src"]
                source = f"https://library.oapen.org/{raw_source}"
            elif "openstax.org" in url:
                # openstax book covers are All Rights Reserved Rice University
                continue
            else:
                # we don't know about that source - log an issue so it can be added :)
                continue
        
            # add the image url to the entry for that book
            data = (str(row["MMS Id"]), source, "Thumbnail", "local", row["Title"])
            worksheet.write_row(f"A{index}", data)
            index = index + 1
        except Exception as e:
            # very lazy exception handling, sorry
            print(row["Title"], type(e), e)
            continue

workbook.close()