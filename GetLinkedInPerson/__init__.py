import datetime
import logging
import requests
import json
import pandas as pd

from linkedin_api import Linkedin
import azure.functions as func

def main(mytimer: func.TimerRequest, outputBlob: func.Out[str]) -> None:
    try:
        SOURCE_COMPANY = 'United Nations Volunteers'
        utc_timestamp = datetime.datetime.utcnow().replace(
            tzinfo=datetime.timezone.utc).isoformat()
        company_urn = ''
        
        logging.info("Function Executed at %s" % utc_timestamp)
        # Authenticate using any Linkedin account credentials
        api = Linkedin(USER, PASSWORD) 
        # Get Company URN
        companyResults = api.search_companies(keywords=['United Nations Volunteers'])
        if companyResults:
            for company in companyResults:
                if company['name'] == SOURCE_COMPANY:
                    company_urn = company['urn_id']
                    break
            # Check that the company was in the search results 
            if company_urn:
                 # Search for people who worked for the company in the past
                logging.info("Searching for former employees in %s" % SOURCE_COMPANY)
                past_volunteers = api.search_people(past_companies=[company_urn])
                if past_volunteers:
                    logging.info(past_volunteers)
                    past_volunteers_df = pd.DataFrame.from_dict(past_volunteers)
                    past_volunteers_csv = past_volunteers_df.to_csv()
                    outputBlob.set(past_volunteers_csv)
                else:
                    logging.warning("No employees found with %s as past company" % SOURCE_COMPANY)
            else:
                logging.error("No company match for %s in the results" % SOURCE_COMPANY)                
        else:
            logging.error("No results found for %s" % SOURCE_COMPANY)          
    except EnvironmentError as e: 
        logging.error(e)