from pathlib import Path

from robocorp import workitems
from robocorp.tasks import get_output_dir, task
from RPA.Excel.Files import Files as Excel
from selenium import webdriver
import pandas as pd
import re

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
            if category != "":
                ap_news.search_category(category)
            ap_news.sort_by('Newest')
            news = ap_news.scrape_news(months_to_extract)
            table = build_table(news, keyword)
            


            item.done()
        except AssertionError as err:
            item.fail("BUSINESS", code="INVALID_ORDER", message=str(err))
        except KeyError as err:
            item.fail("APPLICATION", code="MISSING_FIELD", message=str(err))

def count_keyword(row, column, keyword):
    return row[column].count(keyword)

def contains_money(row, column):
    return bool(re.match('\$?(\d{1,3}[\,\.]?)+(dollars|USD)?', row[column]))
 
def build_table(news, keyword):
    df = pd.DataFrame([one_news.model_dump() for one_news in news])

    # Calculate count fields
    df['count_of_keyword_in_title'] = df.apply(lambda row: count_keyword(row, column='title', keyword=keyword), axis=1)
    df['count_of_keyword_in_description'] = df.apply(lambda row: count_keyword(row, column='description', keyword=keyword), axis=1)
    
    # Calculate money fields
    df['title_contains_money'] =  df.apply(lambda row: contains_money(row, column='title'), axis=1)
    df['description_contains_money'] =  df.apply(lambda row: contains_money(row, column='description'), axis=1)

    return df
