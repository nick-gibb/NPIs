import requests
import json
import pickle
import pandas as pd

# The script won't work without API key!
# DEEPL_API_KEY =


df_c = pd.read_csv("https://raw.githubusercontent.com/jajsmith/COVID19NonPharmaceuticalInterventions/master/npi_canada.csv",
                   parse_dates=['start_date', 'end_date']).drop(columns='Unnamed: 0')
# If the region field is blank, it applies to all Canada
df_c["region"].fillna('All', inplace=True)
# Should not have null values in intervention category (?)
df_c.intervention_category.fillna('Unclassified', inplace=True)

# For Tableau input, make each intervention category a column
new_cols = df_c.intervention_category.unique().tolist()
df_can = df_c.reindex(list(df_c)+new_cols, axis=1)
# Initial value of zero for interventions; later we update with proper stringency value (if not zero)
df_can.fillna({col: 0 for col in new_cols}, inplace=True)

# Six columns hold stringency scores
stringincy_cols = ['oxford_closure_code', 'oxford_public_info_code',
                   'oxford_travel_code', 'oxford_geographic_target_code',
                   'oxford_testing_code', 'oxford_tracing_code']

for index, row in df_can.iterrows():
    intervention = row['intervention_category']  # Each row has intervention
    # Get the sum score for that intervention
    stringency_score = row[stringincy_cols].sum()
    # Update column associated with intervention with stringency score
    df_can.iloc[index, df_can.columns.get_loc(intervention)] = stringency_score

# The API can only handle up to 50 text strings at a time
# Make requests one at a time and store response in translations array
translations = []
for index, row in df_can.iterrows():
    source_title = row['source_title']
    r = requests.post('https://api.deepl.com/v2/translate',
                      data={'auth_key': DEEPL_API_KEY, 'target_lang': 'FR', 'text': source_title})
    translations.append(json.loads(r.content)['translations'][0])

# Update dataframe with fetched translations
translated_texts = [i['text'] for i in translations]
df_can['source_title_fr'] = translated_texts

# Save csv and dump translations to pickle
df_can.to_csv('with_translations_and_more_cols.csv')
with open('src_title_fr', 'wb') as pickle_file:
    pickle.dump(translations, pickle_file)
