import pandas as pd
import numpy as np

def rdpm_recommender_condensed(quiz,FIPS_d, rel_d, sd_d, ter_d, wth_d, acs_d, hth_d, fbi_d, pol_d, tax_d):

    # remove Alaska, Puerto Rico, and DC
    FIPS_d = FIPS_d[(FIPS_d['State']!='Alaska') & (FIPS_d['State']!='Puerto Rico') &
                (FIPS_d['State']!= 'District Of Columbia')]

    # include only counties that are commonly included in all datasets
    FIPS_d = FIPS_d.filter(items = fbi_d.index.unique(), axis=0) # crime
    FIPS_d = FIPS_d.filter(items = ter_d.index.unique(), axis=0) # terrain
    FIPS_d = FIPS_d.filter(items = rel_d.index.unique(), axis=0) # religion
    FIPS_d = FIPS_d.filter(items = hth_d.index.unique(), axis=0) # health

    # add 'Scores' column with 0 penalty points to each dataset to accumulate penalty points by topic
    dfs = [FIPS_d, rel_d, sd_d, ter_d, wth_d, acs_d, hth_d, fbi_d, pol_d, tax_d]

    for df in dfs:
        df['Scores'] = 0 # create empty Scores column for all data

    # create empty importance list for all data
    dfs_str = ['FIPS_d', 'rel_d', 'sd_d', 'ter_d', 'wth_d', 'acs_d', 'hth_d', 'fbi_d', 'pol_d', 'tax_d']

    for df in dfs_str:
        exec(df+'_imp = []')

    # create grader function (0 penality if at least/most)
    def grader(df, response_row, actual):
        
        imp_score = quiz.iloc[response_row,3] # importance score of this question
        
        if quiz.iloc[response_row,1] == "At least":
            score_series = df[actual].apply(lambda x: max(quiz.iloc[response_row,2] - x, 0)**2 * imp_score)
        elif quiz.iloc[response_row,1] == "At most:":
            score_series = df[actual].apply(lambda x: max(x - quiz.iloc[response_row,2], 0)**2 * imp_score)
        else: 
            score_series = abs(quiz.iloc[response_row,2] - df[actual])**2 * imp_score
        
        return score_series, imp_score

    # create function that uses the most recent year in the dataset for questionnaire comparison
    def most_recent(df):
        df_all = df.copy()
        df = df.reset_index()
        df_recent = df.copy()
        df_recent = df_recent.groupby(['FIPS'])['Year'].max() # get most recent data per county
        df_recent = df_recent.reset_index()
        df_recent = pd.DataFrame(df_recent, columns=['FIPS','Year']) # make df of each FIPS and most recent year
        df = pd.merge(df_recent, df, left_on=['FIPS','Year'], right_on=['FIPS','Year'], how='left') # filter df to match
        df = df.set_index('FIPS')
        return df_all, df

    # Rel) blanks in this dataset are equal to zero
    rel_d = rel_d.fillna(0)

    # Rel-1) I prefer the % of the population adhering to any religion to be:
    score, imp_score = grader(rel_d, 47, 'All Religious Adherence Rate D') 
    rel_d['Scores'] += score 

    # Rel-2) I prefer there to be a significant presence of this religious group:
    if quiz.iloc[48,2] != 0:
        rel2_response = rel_d.loc[:,str(quiz.iloc[48,2])]
        rel_d['Scores'] += (((100 - rel2_response)/25)**2) * quiz.iloc[48,3]

    # add rel scores to FIPS_d score total
    FIPS_d['Scores'] = FIPS_d['Scores'].add(rel_d['Scores'], fill_value=0)

    # SD) first questions
    sd_cats = ['SchoolDigger Number of Stars Elementary', 'SchoolDigger Number of Stars Middle', 
            'SchoolDigger Number of Stars High', 'Student/Teacher Ratio D', 'Number All Students D']

    start_loc = 35 # start_loc is is the starting row for the questionnaire answer sheet
    for sd_cat in sd_cats:
        score, imp_score = grader(sd_d, start_loc + sd_cats.index(sd_cat), sd_cat)
        sd_d['Scores'] += score

    # SD-6) For racial distribution, I prefer there to be AT LEAST this percentage of each race:
    races = ['% Asian students', '% Black students', '% Hawaiian Native/Pacific Islander students', '% Hispanic students',
           '% American Indian/Alaska Native students', '% students with Two or More Races', '% White students']

    for race in races:
        sd_d['Scores'] += sd_d[race].apply(lambda x: max(((quiz.iloc[races.index(race)+40,2] - x)/25)**2,0) * quiz.iloc[46,3])

    # SD) get lowest penalty score district for each county, reset series to dataframe, reset index
    sd_d_grouped = sd_d.groupby(['County','State'])['Scores'].min().to_frame().reset_index() # get district with lowest penalty

    # SD) add grouped SD data to FIPS Scores through join
    FIPS_d = FIPS_d.reset_index()
    sd_d_scores = sd_d_grouped[['County','State','Scores']].rename({'Scores':'sd_Scores'}, axis='columns')
    FIPS_d = pd.merge(FIPS_d, sd_d_scores, left_on=['County','State'], right_on=['County','State'], how='left')
    FIPS_d['sd_Scores'] = FIPS_d['sd_Scores'].fillna(FIPS_d['sd_Scores'].mean()) # give mean penalty to non-matching districts
    FIPS_d['Scores'] += FIPS_d['sd_Scores'] # add SD points to cumulative points
    del FIPS_d['sd_Scores']
    FIPS_d = FIPS_d.set_index('FIPS')

    # test against only the most recent completed year but keep entirity for time series analysis
    ter_d_all, ter_d = most_recent(ter_d)

    # Ter) test against only the most recent completed year but keep entirity for time series analysis
    ter_d_all = ter_d.copy()
    ter_d = ter_d_all[ter_d['Year']==2011]

    # Ter-1) For terrain, I prefer there to be AT LEAST this percentage of each terrain:
    terrains = ['Big city', 'Farmland', 'Forests', 'Houses with lots of land', 'Open fields', 'Open water', 
                'Perennial ice/snow', 'Rock/Sand/Clay', 'Suburbia', 'Wetlands']

    for terrain in terrains:
        ter_d['Scores'] += ter_d[terrain].apply(
            lambda x: max(((quiz.iloc[terrains.index(terrain)+14,2] - x)/25)**2,0) * quiz.iloc[terrains.index(terrain)+14,3])

    # Ter) add ter scores to FIPS_d score total
    FIPS_d['Scores'] = FIPS_d['Scores'].add(ter_d['Scores'], fill_value=0)

    # Wth) first questions
    wth_cats = ['Winter Avg temp (F) D', 'Summer Avg temp (F) D', 'Avg Yearly Rainfall (in) D', 'Avg Yearly Snowfall (in) D',
            'Avg Hours Sunshine Daily D', 'Avg Clear Days D', 'Avg Days with Snow D']

    start_loc = 28
    for wth_cat in wth_cats:
        score, imp_score = grader(wth_d, start_loc + wth_cats.index(wth_cat), wth_cat)
        wth_d['Scores'] += score

    # Wth) add state Wth data to FIPS Scores through join
    FIPS_d = FIPS_d.reset_index()
    wth_d_scores = wth_d[['State','Scores']].rename({'Scores':'wth_Scores'}, axis='columns')
    FIPS_d = pd.merge(FIPS_d, wth_d_scores, left_on='State', right_on='State', how='left')
    FIPS_d['Scores'] += FIPS_d['wth_Scores']
    del FIPS_d['wth_Scores']
    FIPS_d = FIPS_d.set_index('FIPS')

    # ACS) first questions
    acs_cats = ['% Pop Density D', '% Children Under 10 D', '% Children 10 and Older D', '% Couples that are Same-Sex D',
            '% Population Over 25 with at Least a Bachelor Degree D', 
            '% Civilian Population 18 Years and Over that is a Veteran D',
            '% Foreign Born D']

    start_loc = 0
    for acs_cat in acs_cats:
        score, imp_score = grader(acs_d, start_loc + acs_cats.index(acs_cat), acs_cat)
        acs_d['Scores'] += score

    # ACS-8) For racial distribution, I prefer the percentage of each race to be AT LEAST:
    races = ['% Asian', '% Black', '% Hawaiian or Pacific Islander', '% Hispanic', '% Native American', 
            '% Two or More Races', '% White', '% Other Race']

    for race in races:
        acs_d['Scores'] += acs_d[race].apply(lambda x: max(((quiz.iloc[races.index(race)+7,2] - x)/25)**2,0) * quiz.iloc[14,3])

    # Acs) last questions
    acs_cats = ['Median Household Income D', 'Median Gross Rent D', 'Average Commute to Work D']

    start_loc = 15
    for acs_cat in acs_cats:
        score, imp_score = grader(acs_d, start_loc + acs_cats.index(acs_cat), acs_cat)
        acs_d['Scores'] += score

    # ACS) add acs scores to FIPS_d score total
    FIPS_d['Scores'] = FIPS_d['Scores'].add(acs_d['Scores'], fill_value=0)

    # test against only the most recent completed year but keep entirity for time series analysis
    hth_d_all, hth_d = most_recent(hth_d)


    # Hth) all questions
    hth_cats = ['Primary Care Physicians Per 100,000 Population D',
    'Mental Health Providers Per 100,000 Population D',
    'Dentists Per 100,000 Population D',
    'Percent Adults With Limited Access To Doctor Due To Costs D',
    'Percent Persons With Limited Access To Healthy Foods D',
    'Percent Physically Inactive Persons D',
    'Percent Obese Persons Adults D',
    'Percent Adults That Report Fair Or Poor Health D',
    'Percent Current Adult Smokers D',
    'Percent Drinking Adults D',
    'STI Rate Per 100,000 Population D',
    'Child Mortality Rate Per 100,000 Population D',
    'Teen Births Rate Per 1,000 Population D',
    'Infant Mortality Rate Per 1,000 Live Births D',
    'Percent Low Birthweight Births (<2.5Kg) D']

    start_loc = 49
    for hth_cat in hth_cats:
        score, imp_score = grader(hth_d, start_loc + hth_cats.index(hth_cat), hth_cat)
        hth_d['Scores'] += score

    # Hth) add hth scores to FIPS_d score total
    FIPS_d['Scores'] = FIPS_d['Scores'].add(hth_d['Scores'], fill_value=0)

    # test against only the most recent completed year but keep entirity for time series analysis
    fbi_d_all, fbi_d = most_recent(fbi_d)


    # FBI) all questions
    fbi_cats = ['Violent Crimes Rate D','Property Crimes Rate D']

    start_loc = 64
    for fbi_cat in fbi_cats:
        score, imp_score = grader(fbi_d, start_loc + fbi_cats.index(fbi_cat), fbi_cat)
        fbi_d['Scores'] += score

    # Fbi) add fbi scores to FIPS_d score total
    FIPS_d['Scores'] = FIPS_d['Scores'].add(fbi_d['Scores'], fill_value=0)

    # Pol) blanks in this dataset are equal to zero
    pol_d = pol_d.fillna(0)

    # test against only the most recent completed year but keep entirity for time series analysis
    pol_d_all, pol_d = most_recent(pol_d)

    # Pol) I prefer there to be a significant presence of this political group:
    if quiz.iloc[66,2] != 0:
        pol_response = pol_d.loc[:,str(quiz.iloc[66,2])]
        pol_d['Scores'] += (((100 - pol_response)/25)**2) * quiz.iloc[66,3]

    # Pol) add pol scores to FIPS_d score total
    FIPS_d['Scores'] = FIPS_d['Scores'].add(pol_d['Scores'], fill_value=0)

    # Tax) all questions
    tax_cats = ['State and Mean Local Sales Tax D','Income Tax (Lowest Bracket) D',
                'Income Tax (Highest Bracket) D', 'Median Property Tax D']

    start_loc = 67
    for tax_cat in tax_cats:
        score, imp_score = grader(tax_d, start_loc + tax_cats.index(tax_cat), tax_cat)
        tax_d['Scores'] += score

    # Tax) add state tax data to FIPS Scores through join
    tax_d_scores = tax_d[['State','Scores']].rename({'Scores':'tax_Scores'}, axis='columns')

    FIPS_d = FIPS_d.reset_index()
    FIPS_d = pd.merge(FIPS_d, tax_d_scores, left_on=['State'], right_on=['State'], how='left')
    FIPS_d['Scores'] += FIPS_d['tax_Scores']
    del FIPS_d['tax_Scores']
    FIPS_d = FIPS_d.set_index('FIPS')

    # sort values and remove unneeded rows
    FIPS_d.sort_values(by='Scores', inplace=True)
    FIPS_d = FIPS_d.round({'Scores':2})

    return FIPS_d.reset_index(drop=True)

def random_quiz_generator(quiz,quiz_answers):
    possible_religions = list(quiz_answers["Religions"].dropna().unique())
    possible_politics = list(quiz_answers["Pol"].dropna().unique())

    curr_quiz = pd.DataFrame()
    curr_quiz["Question"] = quiz["Question"]

    # Random values in "Measurement":
    curr_quiz["Measurement"] = np.random.choice(["At least","Equal to","At most"], curr_quiz.shape[0])
    # hard-coded:
    curr_quiz.loc[curr_quiz["Question"].isin(["Acs-8)","Ter-1)","SD-6)","Rel-2","Pol-1"]), ["Measurement"]] = np.nan

    # Random values in "Response":
    curr_quiz["Response"] = np.random.randint(0, 6, curr_quiz.shape[0])
    curr_quiz.loc[curr_quiz["Question"].isin(["Rel-2)"]), ["Response"]] = np.random.choice(possible_religions)
    curr_quiz.iloc[7:15,2] = list(np.random.dirichlet(np.ones(8),size=1)[0]*100) #random values summing to 100 for acs-8
    curr_quiz.iloc[18:28,2] = list(np.random.dirichlet(np.ones(10),size=1)[0]*100) #random values summing to 100 for ter-1
    curr_quiz.iloc[40:47,2] = list(np.random.dirichlet(np.ones(7),size=1)[0]*100) #random values summing to 100 for acs-8
    curr_quiz.loc[curr_quiz["Question"].isin(["Pol-1)"]), ["Response"]] = np.random.choice(possible_politics)

    # Random values in "Importance":
    curr_quiz["Importance"] = np.random.randint(0, 11, curr_quiz.shape[0])

    return curr_quiz