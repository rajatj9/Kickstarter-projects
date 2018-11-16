import json 
import numpy as np
import pandas as pd 
from pandas.io.json import json_normalize
import time
import sys
from datetime import datetime

# All columns from original dataset
all_columns = ['backers_count', 'blurb', 'category.color', 'category.id', 'category.name', 'category.parent_id', 
        'category.position', 'category.slug', 'category.urls.web.discover', 'converted_pledged_amount', 'country', 'created_at', 
        'creator.avatar.medium', 'creator.avatar.small', 'creator.avatar.thumb', 'creator.chosen_currency', 'creator.id', 
        'creator.is_registered', 'creator.name', 'creator.slug', 'creator.urls.api.user', 'creator.urls.web.user', 'currency', 
        'currency_symbol', 'currency_trailing_code', 'current_currency', 'deadline', 'disable_communication', 'fx_rate', 'goal', 
        'id', 'is_starrable', 'launched_at', 'location.country', 'location.displayable_name', 'location.id', 'location.is_root', 
        'location.localized_name', 'location.name', 'location.short_name', 'location.slug', 'location.state', 'location.type', 
        'location.urls.api.nearby_projects', 'location.urls.web.discover', 'location.urls.web.location', 'name', 'photo.1024x576', 
        'photo.1536x864', 'photo.ed', 'photo.full', 'photo.key', 'photo.little', 'photo.med', 'photo.small', 'photo.thumb', 
        'pledged', 'profile.background_color', 'profile.background_image_opacity', 'profile.blurb', 
        'profile.feature_image_attributes.image_urls.baseball_card', 'profile.feature_image_attributes.image_urls.default', 
        'profile.id', 'profile.link_background_color', 'profile.link_text', 'profile.link_text_color', 'profile.link_url', 
        'profile.name', 'profile.project_id', 'profile.should_show_feature_image_section', 'profile.show_feature_image', 
        'profile.state', 'profile.state_changed_at', 'profile.text_color', 'slug', 'source_url', 'spotlight', 'staff_pick', 
        'state', 'state_changed_at', 'static_usd_rate', 'urls.web.project', 'urls.web.rewards', 'usd_pledged', 'usd_type', 
        'profile.background_image_attributes.id', 'profile.background_image_attributes.image_urls.baseball_card', 
        'profile.background_image_attributes.image_urls.default', 'profile.feature_image_attributes.id']

# Columns preserved after first round of transforming data
retained_columns = ['backers_count', 'blurb', 'category.color', 'category.id', 'category.name', 'category.parent_id', 
        'category.position', 'category.slug', 'converted_pledged_amount', 'country', 'created_at', 
        'creator.chosen_currency', 'creator.id', 'creator.is_registered', 'creator.name', 'creator.slug', 'currency', 
        'currency_symbol', 'currency_trailing_code', 'current_currency', 'deadline', 'disable_communication', 'fx_rate', 'goal', 
        'id', 'is_starrable', 'launched_at', 'location.country', 'location.displayable_name', 'location.id', 'location.is_root', 
        'location.localized_name', 'location.name', 'location.short_name', 'location.slug', 'location.state', 'location.type', 
        'name', 'pledged', 'profile.background_color', 'profile.background_image_opacity', 'profile.blurb', 
        'profile.id', 'profile.link_background_color', 'profile.link_text', 'profile.link_text_color', 'profile.link_url', 
        'profile.name', 'profile.project_id', 'profile.should_show_feature_image_section', 'profile.show_feature_image', 
        'profile.state', 'profile.state_changed_at', 'profile.text_color', 'slug', 'spotlight', 'staff_pick', 
        'state', 'state_changed_at', 'static_usd_rate', 'urls.web.project', 'usd_pledged', 'usd_type']

# Selected columns from transformed data
selected_columns = ['backers_count', 'blurb', 'category.name', 'category.slug', 'converted_pledged_amount', 'country', 'created_at', 
        'creator.slug', 'currency', 'currency_trailing_code', 'current_currency', 'deadline', 'disable_communication', 'fx_rate', 'goal', 
        'id', 'is_starrable', 'launched_at', 'location.country', 'location.displayable_name', 'location.is_root', 
        'location.short_name', 'location.slug', 'location.state', 'location.type', 
        'name', 'pledged', 'spotlight', 'staff_pick', 'state', 'state_changed_at', 'static_usd_rate', 'urls.web.project', 'usd_pledged']

# Final columns we will use in data analysis
final_columns = ['parent_category', 'funding_duration_days', 'pre_funding_duration_days', 'launch_month', 'deadline_month',
        'currency', 'country', 'location.state', 'location.type', 
        'spotlight', 'staff_pick', 'is_starrable', 'creator_has_slug', 'disable_communication',
        'blurb_length', 'blurb_word_count', 'name_length', 'name_word_count', 
        'usd_goal', 'usd_pledged', 'state', 'backers_count']

#################################### Step 1: Convert from ridiculously long JSON mess into clean csv file ####################################
def json_to_csv(input_file, output_file):
    print('Transforming data')
    start = time.time()
    with open(input_file, 'r') as f:
        print(input_file, 'successfully opened.')
        # Save first line to output_file with headers to maintain dataframe structure
        first_line = f.readline()
        json_line = json.loads(first_line)
        df = json_normalize(json_line['data'])
        df = df[retained_columns]
        df.to_csv(output_file, index=False)
        df = df[0:0]
        
        # Read in remaining lines and write them to file one by one (slow, but consistent and secure in case of interrupt. Also it's better than keeping 1GB+ data in memory)
        count = 1
        batch = 100
        batch_start = start
        for line in f:
            json_line = json.loads(line)
            temp_df = json_normalize(json_line['data'])
            df = df.append(temp_df, sort=False)
            df = df[retained_columns]
            df.to_csv(output_file, index=False, header=False, mode='a')
            df = df[0:0]
            count += 1
            if(count % batch == 0):
                batch_end = time.time()
                print('Finished processing', count, 'lines. Last', batch, 'lines processed in', batch_end - batch_start, 'seconds')
                batch_start = batch_end
        print('Finished transforming file in', time.time() - start, 'seconds')
    return

#################################### Step 2: Drop columns that are mostly useless or are missing too much data ####################################
def drop_useless_columns(input_file, output_file):
    print('Dropping preselcted columns')
    start = time.time()
    df = pd.read_csv(input_file)
    print(input_file, 'successfully opened.')
    df = df[selected_columns]
    df.to_csv(output_file, index=False)
    print('Columns dropped in', time.time() - start, 'seconds')
    return

#################################### Step 3: Create derived columns ####################################
def generate_new_columns(input_file, output_file):
    print('Creating new columns')
    begin = time.time()

    df = pd.read_csv(input_file)
    print(input_file, 'successfully opened.')

    # Create column for blurb length and blurb word count
    print('Adding columns for blurb length and word count...')
    start = time.time()
    df['blurb_length'] = df['blurb'].str.len()
    df['blurb_word_count'] = df.apply(lambda row: 0 if pd.isnull(row['blurb']) else len(row['blurb'].split()), axis=1)
    end = time.time()
    print('Added columns blurb_length and blurb_word_count in', end - start, 'seconds')

    # Create column for project name length and project word count
    print('Adding columns for project name length and word count...')
    start = time.time()
    df['name_length'] = df['name'].str.len()
    df['name_word_count'] = df.apply(lambda row: 0 if pd.isnull(row['name']) else len(row['name'].split()), axis=1)
    end = time.time()
    print('Added columns name_length and name_word_count in', end - start, 'seconds')

    # Create column for if creator has a slug (url identifier)
    print('Adding boolean column for whether the creator has a slug...')
    start = time.time()
    df['creator_has_slug'] = np.where(df['creator.slug'].str.len() > 0, True, False)
    end = time.time()
    print('Added column creator_has_slug in', end - start, 'seconds')

    # Create column for funding duration in days, rounded down to nearest whole day
    print('Adding columns for funding duration and duration between project creation and launch...')
    start = time.time()
    df['funding_duration_days'] = df.apply(lambda row: (datetime.utcfromtimestamp(round(row['deadline'])) - datetime.utcfromtimestamp(round(row['launched_at']))).days, axis=1)
    df['pre_funding_duration_days'] = df.apply(lambda row: (datetime.utcfromtimestamp(round(row['launched_at'])) - datetime.utcfromtimestamp(round(row['created_at']))).days, axis=1)
    end = time.time()
    print('Added columns funding_duration_days and pre_funding_duration_days in', end - start, 'seconds')

    # Create column for funding launch month
    print('Adding columns for launch and deadline month...')
    start = time.time()
    df['launch_month'] = df.apply(lambda row: datetime.utcfromtimestamp(row['created_at']).month, axis=1)
    df['deadline_month'] = df.apply(lambda row: datetime.utcfromtimestamp(row['deadline']).month, axis=1)
    end = time.time()
    print('Added columns launch_month, deadline_month in', end - start, 'seconds')

    # Concert all times from Unix Epoch Time to human readable format (created_at, deadline, launched_at, state_changed_at)
    print('Converting all datetime columns from unix epoch time to human readable time...')
    start = time.time()
    df['created_at'] = df.apply(lambda row: datetime.utcfromtimestamp(row['created_at']).strftime('%Y-%m-%d %H:%M:%S'), axis=1)
    df['deadline'] = df.apply(lambda row: datetime.utcfromtimestamp(row['deadline']).strftime('%Y-%m-%d %H:%M:%S'), axis=1)
    df['launched_at'] = df.apply(lambda row: datetime.utcfromtimestamp(row['launched_at']).strftime('%Y-%m-%d %H:%M:%S'), axis=1)
    df['state_changed_at'] = df.apply(lambda row: datetime.utcfromtimestamp(row['state_changed_at']).strftime('%Y-%m-%d %H:%M:%S'), axis=1)
    end = time.time()
    print('Converted columns created_at, deadline, launched_at, state_changed_at in', end - start, 'seconds')

    # Create column for parent category name from category slug
    print('Adding column for parent category derived from category.slug...')
    start = time.time()
    df['parent_category'] = df.apply(lambda row: row['category.slug'].split('/')[0], axis=1)
    end = time.time()
    print('Added column parent_category in', end - start, 'seconds')

    # Create column for converted goal and pledge
    print('Adding columns for converted pledged and goal...')
    start = time.time()
    df['usd_goal'] = df.apply(lambda row: row['fx_rate'] * row['goal'], axis=1)
    df['usd_pledged'] = df.apply(lambda row: row['fx_rate'] * row['pledged'], axis=1)
    end = time.time()
    print('Added column usd_goal, usd_pledged in', end - start, 'seconds')

    df.to_csv(output_file, index=False)
    print('Created columns in', time.time() - begin, 'seconds')

    return

#################################### Step 4: Drop all remaining unneeded columns and remove rows with missing data ####################################
def final_column(input_file, output_file):
    print('Dropping finals columns')
    start = time.time()
    df = pd.read_csv(input_file)
    print(df.head)
    print(input_file, 'successfully opened.')
    df = df[final_columns]
    df.dropna(inplace=True)
    print(df.head)
    df.to_csv(output_file, index=False)
    print('Columns dropped in', time.time() - start, 'seconds')
    return

if __name__ == "__main__":
    raw_data = 'kickstarter_data_raw.json'
    transformed_data = 'kickstarter_data_transformed.csv'
    pruned_data = 'kickstarter_data_pruned.csv'
    derived_data = 'kickstarter_data_derived.csv'
    final_data = 'kickstarter_data_final.csv'

    if len(sys.argv) == 2:
        if sys.argv[1] == '1':
            json_to_csv(raw_data, transformed_data)
        elif sys.argv[1] == '2':
            drop_useless_columns(transformed_data, pruned_data)
        elif sys.argv[1] == '3':
            generate_new_columns(pruned_data, derived_data)
        elif sys.argv[1] == '4':
            final_column(derived_data, final_data)
    else:
        print('You must pass in [1, 2, 3, 4] as an arg')
