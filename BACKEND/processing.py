from utils import standardize_price, standardize_tags, calculate_haversine_distance
from config import W_DISTANCE,W_RATING,W_TAGS
import numpy as np
import pandas as pd


# Input -> Clean Data -> Filter Distance -> Filter Budget -> Filter Tags -> Rank -> Output
def process_recommendations(df, user_lat, user_lon, max_dist, max_budget, user_tags):
    # fake GPS, sau nay goi API
    max_dist = float(max_dist)
    max_budget = float(max_budget)
    df = df.copy()
    df['latitude'] = np.linspace(10.76, 10.77, len(df)) # fake
    df['longitude'] = np.linspace(106.68, 106.70, len(df)) # fake

    df['tags_standard'] = standardize_tags(df['tags'])
    df['avg_price'] = standardize_price(df['price_range'])

    df['rating'] = df['rating'].fillna(0)

    # tinh khoang cach va loc theo vi tri
    df['distance_km'] = df.apply(
        lambda row: calculate_haversine_distance(user_lat,user_lon, row['latitude'], row['longitude']), axis=1
    )

    # loc theo khoang cach va gia
    df_filtered = df[(df['distance_km'] <= max_dist) & (df['avg_price'] <= max_budget)].copy()
    
    # loc theo tags
    if user_tags:
        user_tags_list = [tag.strip() for tag in user_tags.split(',')]  # "spicy, seafood" -> ['spicy', 'seafood']
        
        def calculate_tag_score(restaurant_tags, required_tags):
            matched = sum(1 for tag in required_tags if tag in restaurant_tags)
            return matched / len(required_tags)
        
        df_filtered['tag_score'] = df_filtered['tags_standard'].apply(
            lambda x: calculate_tag_score(x, user_tags_list)
        )
        
        # Loc chi nhung nha hang co it nhat 1 tag
        df_filtered = df_filtered[df_filtered['tag_score'] > 0].copy()
    else:
        df_filtered['tag_score'] = 0

    if df_filtered.empty:
        return pd.DataFrame() # df rong

    df_filtered['rating_normalized'] = df_filtered['rating'] / 5.0
    max_dist_value = df_filtered['distance_km'].max()

    # Chuan hoa va dao nguoc khoang cach
    df_filtered['distance_score'] = 1 - (df_filtered['distance_km']/(max_dist_value+0.01))
    
    # Tinh diem
    df_filtered['priority_score'] = (W_RATING * df_filtered['rating_normalized']) + (W_DISTANCE * df_filtered['distance_score']) + W_TAGS * df_filtered['tag_score']

    # Tim ra top 3
    TOP3_REC = df_filtered.sort_values('priority_score', ascending = False).head(3)

    return TOP3_REC[['restaurant_id', 'name', 'rating', 'distance_km', 'avg_price', 'priority_score', 'tag_score','tags']]

