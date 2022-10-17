import requests
import ast
import pandas as pd
import json

def get_key(api_service):
    # Get secrets
    with open('../secrets.json') as f:
        secrets = json.load(f)

    # Get key for input API service (e.g. "us-census-bureau"):
    key = secrets[api_service]["key"]
    return key

def send_and_process_request(dataset,year,state="*"):
    # all data available at: https://api.census.gov/data.html

    # Get API Key:
    # key = get_key(api_service="us-census-bureau")

    # [acs] 2015-2019 American Community Survey: Migration Flows
    # https://api.census.gov/data/2019/acs/flows/variables.html
    if dataset=="acs":
        response = requests.get(f"https://api.census.gov/data/{year}/acs/flows?get=GEOID1,GEOID2,MOVEDNET,MOVEDNET_M,MOVEDIN,MOVEDIN_M,MOVEDOUT,MOVEDOUT_M,FULL1_NAME,FULL2_NAME,COUNTY1,COUNTY1_NAME,COUNTY2,COUNTY2_NAME,STATE1,STATE1_NAME,STATE2,STATE2_NAME&for=county:*&in=state:{state}")

    # [bds] Economic Surveys: Business Dynamics Statistics
    # https://api.census.gov/data/timeseries/bds/variables.html
    if dataset=="bds":
        response = requests.get(f"https://api.census.gov/data/timeseries/bds?get=COUNTY,STATE,EAGE,NAME,NAICS_LABEL,YEAR,FIRM,ESTAB,EMP,EMPSZES,ESTABS_ENTRY,ESTABS_EXIT,NET_JOB_CREATION,INDGROUP,SECTOR,SUBSECTOR&for=county:*&in=state:{state}&time={year}&NAICS=00")

    # [cbp] Economic Surveys: Business Patterns: County Business Patterns
    # https://api.census.gov/data/2020/cbp/variables.html
    if dataset=="cbp":
        response = requests.get(f"https://api.census.gov/data/{year}/cbp?get=COUNTY,NAME,NAICS2017_LABEL,ESTAB,PAYANN,EMP,EMPSZES,ESTAB,INDGROUP,SECTOR,SUBSECTOR,STATE&for=county:*&in=state:{state}&NAICS2017=*&LFO=*&EMPSZES=*")

    # [cps] Current Population Survey: School Enrollment Supplement
    #  https://api.census.gov/data/2021/cps/school/oct/variables.html
    if dataset=="cps":
        # Note: for cps data, should run state-by-state, because data is too large. States correspond to numbers (e.g.: 01, 02...50)
        response = requests.get(f"https://api.census.gov/data/{year}/cps/school/oct?get=HEFAMINC,PWSUPWGT,PESEX,PEGRADE,PECHGRDE,PEHGCOMP,PECYC,PEEDUCA,PEGED,PEMARITL,PEMLR,GTCO,GESTFIPS&for=county:*&in=state:{state}&PESCHFT=1")

    # [sahie] Time Series Small Area Health Insurance Estimates: Small Area Health Insurance Estimates
    # https://api.census.gov/data/timeseries/healthins/sahie/variables.html
    if dataset=="sahie":
        response = requests.get(f"https://api.census.gov/data/timeseries/healthins/sahie?get=COUNTY,STATE,NIC_PT,NUI_PT,NAME,IPRCAT,IPR_DESC,PCTIC_PT,PCTUI_PT&for=county:*&in=state:{state}&time={year}")
    
    # [saipe] Time Series Small Area Income and Poverty Estimates: State and County
    # https://api.census.gov/data/timeseries/poverty/saipe/variables.html
    if dataset=="saipe":
        response = requests.get(f"https://api.census.gov/data/timeseries/poverty/saipe?get=COUNTY,STATE,SAEPOVALL_PT,SAEPOVRTALL_PT,SAEMHI_PT,NAME&for=county:*&in=state:{state}&time={year}")

    return response

def process_response(response):
    # Process response data into a dataframe:
    try:
        resp_lst = response.json()
        headers = resp_lst.pop(0)
        df = pd.DataFrame(resp_lst, columns=headers)
        return df
        
    except:
        print("no data found")