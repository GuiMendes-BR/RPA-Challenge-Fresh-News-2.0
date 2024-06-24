from pathlib import Path

from robocorp import workitems
from robocorp.tasks import get_output_dir, task
from RPA.Excel.Files import Files as Excel
from selenium import webdriver

from pages import ApNewsPage

@task
def producer():
    """Split Excel rows into multiple output Work Items for the next step."""
    output = get_output_dir() or Path("output")
    filename = "orders.xlsx"

    for item in workitems.inputs:
        path = item.get_file(filename, output / filename)

        excel = Excel()
        excel.open_workbook(path)
        rows = excel.read_worksheet_as_table(header=True)

        for row in rows:
            payload = {
                "Name": row["Name"],
                "Zip": row["Zip"],
                "Product": row["Item"],
            }
            workitems.outputs.create(payload)


@task
def consumer():
    """Process all the produced input Work Items from the previous step."""

    driver = webdriver.Chrome()

    ap_news = ApNewsPage(driver)
    ap_news.open()

    for item in workitems.inputs:
        try:
            keyword = item.payload["keyword"]
            category = item.payload["category"]
            months_to_extract = item.payload["months_to_extract"]

            ap_news.search_keyword(keyword)
            ap_news.search_category(category)
            


            item.done()
        except AssertionError as err:
            item.fail("BUSINESS", code="INVALID_ORDER", message=str(err))
        except KeyError as err:
            item.fail("APPLICATION", code="MISSING_FIELD", message=str(err))


def open_news_page():
    pass

# def search_for_keyword():
#     pass

def search_for_category():
    pass

def scrape_news(months=0):
    pass

