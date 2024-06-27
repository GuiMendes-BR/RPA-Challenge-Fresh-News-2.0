from robocorp import workitems
from robocorp.tasks import task
from robocorp import log
from RPA.Browser.Selenium import Selenium

import pandas as pd
import re
import shutil
from pathlib import Path

from pages import ApNewsPage
from config import config

@task
def consumer():
    """Process all the produced input Work Items."""

    log.info("Starting Execution!")
    selenium = Selenium()

    log.info("Opening ApNews...")
    ap_news = ApNewsPage(selenium)

    # ap_news.open()

    for item in workitems.inputs:
        try:
            log.info(f"Reading payload {item.payload}...")
            keyword = item.payload["keyword"]
            category = item.payload["category"]
            months_to_extract = item.payload["months_to_extract"]

            ap_news.search_keyword(keyword)
            if category != "":
                ap_news.search_category(category)
            ap_news.sort_by('Newest') 
            news = ap_news.scrape_news(months_to_extract)
            table = build_table(news, keyword)
            table.to_excel(f"{config['artifactsDir']}/News for {keyword}.xlsx")
            zip_pictures(keyword)


            item.done()
        except AssertionError as err:
            item.fail("BUSINESS", code="INVALID_ORDER", message=str(err))
        except KeyError as err:
            item.fail("APPLICATION", code="MISSING_FIELD", message=str(err))
        except NotImplementedError as err:
            item.fail("BUSINESS", code="NOT_IMPLEMENTED", message=str(err))
        except SystemError as err:
            item.fail("APPLICATION", code="SYSTEM_ERROR", message=str(err))
        except Exception as err:
            item.fail("APPLICATION", code="UNKNOWN_ERROR", message=str(err))

def count_keyword(row, column, keyword):
    """Returns the count of keywords in specified column"""
    return row[column].count(keyword)

def contains_money(row, column):
    """Returns a boolean informing wether specifed column contains a monetary value
    such as $11.1 | $111,111.11 | 11 dollars | 11 USD"""
    return bool(
        re.search('\$(\d{1,3}[\,\.]?)+', row[column]) or
        re.search('\d+\sdollars|USD', row[column])
    )
 
def build_table(news, keyword):
    """Builds a table based on the news list and adds four columns:
    - count_of_keyword_in_title
    - count_of_keyword_in_description
    - title_contains_money
    - description_contains_money
    """
    df = pd.DataFrame([one_news.model_dump() for one_news in news])

    # Calculate count fields
    df['count_of_keyword_in_title'] = df.apply(lambda row: count_keyword(row, column='title', keyword=keyword), axis=1)
    df['count_of_keyword_in_description'] = df.apply(lambda row: count_keyword(row, column='description', keyword=keyword), axis=1)
    
    # Calculate money fields
    df['title_contains_money'] =  df.apply(lambda row: contains_money(row, column='title'), axis=1)
    df['description_contains_money'] =  df.apply(lambda row: contains_money(row, column='description'), axis=1)

    return df

def zip_pictures(keyword):
    """Zips the pictures to a single file and the deletes the pictures folder"""
    pictures_dir = config['picturesDir']
    artifacts_dir = config['artifactsDir']
    if (Path.cwd() / pictures_dir).exists():
        shutil.make_archive(f'{artifacts_dir}/Pictures for {keyword}', 'zip', pictures_dir)
        shutil.rmtree(pictures_dir)