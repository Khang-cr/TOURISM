import pandas as pd
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from underthesea import word_tokenize
import numpy as np
import torch
import re

# Load data
print("📂 Loading restaurant data...")
df = pd.read_csv(r"C:\python\Projects\TOURISM\AI\Data-master\restaurants_100_improved.csv")

# Convert columns to string and handle NaN
df["tags"] = df["tags"].fillna("").astype(str)
df["city"] = df["city"].fillna("").astype(str)
df["name"] = df["name"].fillna("").astype(str)
df["cuisine"] = df["cuisine"].fillna("").astype(str)
df["rating"] = pd.to_numeric(df["rating"], errors='coerce').fillna(0)

# Initialize models
print("🤖 Loading AI models...")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"   Using device: {device}")

model = SentenceTransformer("keepitreal/vietnamese-sbert", device=device)
kw_model = KeyBERT(model=model)
embed_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device=device)

# Vietnamese stop words (expanded)
stop_words_vi = [
    'của', 'và', 'các', 'có', 'được', 'cho', 'là', 'với', 
    'để', 'trong', 'không', 'một', 'này', 'những', 'đã', 
    'như', 'bởi', 'từ', 'hoặc', 'đến', 'khi', 'cũng', 'nhưng',
    'thì', 'nào', 'đây', 'rất', 'sẽ', 'vào', 'ra', 'ở', 'về'
]

# Cuisine keywords for better matching
cuisine_keywords = {
    'Việt Nam': ['việt nam', 'phở', 'bún', 'cơm tấm', 'bánh mì', 'gỏi cuốn', 'nem', 'chả'],
    'Nhật Bản': ['nhật', 'nhật bản', 'sushi', 'ramen', 'sashimi', 'tempura', 'udon'],
    'Hàn Quốc': ['hàn', 'hàn quốc', 'korea', 'bulgogi', 'kimchi', 'bbq hàn', 'bibimbap'],
    'Thái': ['thái', 'thái lan', 'thai', 'pad thai', 'tom yum', 'cà ri thái'],
    'Trung Quốc': ['trung quốc', 'dimsum', 'dimsum', 'vịt quay', 'mì trung hoa'],
    'Âu': ['âu', 'ý', 'pháp', 'pasta', 'pizza', 'steak', 'mỳ ý'],
    'Ấn Độ': ['ấn độ', 'ấn', 'cà ri ấn', 'tandoori', 'biryani', 'naan'],
    'Mỹ': ['mỹ', 'burger', 'hamburger', 'bbq mỹ', 'steak mỹ'],
    'Địa Trung Hải': ['địa trung hải', 'kebab', 'hummus', 'falafel', 'hy lạp']
}

def preprocess_vi(text):
    """Preprocess Vietnamese text"""
    text = str(text).lower()
    text = word_tokenize(text, format="text")
    return text

def extract_city(user_input):
    """Extract city from user input with flexible matching"""
    user_lower = user_input.lower()
    
    city_keywords = {
        "Đà Nẵng": ["đà nẵng", "da nang", "đn", "danang"],
        "Hồ Chí Minh": ["hồ chí minh", "hcm", "sài gòn", "saigon", "tphcm", "tp hcm"],
        "Hà Nội": ["hà nội", "ha noi", "hn", "hanoi"],
        "Nha Trang": ["nha trang"],
        "Đà Lạt": ["đà lạt", "da lat", "dalat"],
        "Cần Thơ": ["cần thơ", "can tho"],
        "Huế": ["huế", "hue"],
        "Hải Phòng": ["hải phòng", "hai phong"],
        "Vũng Tàu": ["vũng tàu", "vung tau"],
        "Phú Quốc": ["phú quốc", "phu quoc"]
    }
    
    for city, keywords in city_keywords.items():
        if any(kw in user_lower for kw in keywords):
            return city
    return None

def extract_cuisine(user_input):
    """Extract cuisine preference from user input"""
    user_lower = user_input.lower()
    
    for cuisine, keywords in cuisine_keywords.items():
        if any(kw in user_lower for kw in keywords):
            return cuisine
    return None

def extract_price_preference(user_input):
    """Extract price preference from user input"""
    user_lower = user_input.lower()
    
    cheap_keywords = ['rẻ', 'bình dân', 'sinh viên', 'tiết kiệm', 'budget', 'cheap']
    mid_keywords = ['vừa phải', 'trung bình', 'hợp lý']
    expensive_keywords = ['cao cấp', 'sang trọng', 'đắt', 'fine dining', 'luxury']
    
    if any(kw in user_lower for kw in cheap_keywords):
        return '₫'
    elif any(kw in user_lower for kw in expensive_keywords):
        return '₫₫₫'
    elif any(kw in user_lower for kw in mid_keywords):
        return '₫₫'
    return None

def extract_atmosphere_tags(user_input):
    """Extract atmosphere preferences from user input"""
    user_lower = user_input.lower()
    atmosphere_tags = []
    
    tag_keywords = {
        'romantic': ['lãng mạn', 'hẹn hò', 'couple', 'romantic'],
        'family': ['gia đình', 'family', 'đông người'],
        'view': ['view', 'cảnh đẹp', 'rooftop', 'sân thượng'],
        'quiet': ['yên tĩnh', 'quiet', 'tĩnh lặng'],
        'modern': ['hiện đại', 'modern', 'trendy'],
        'vegetarian': ['chay', 'vegetarian', 'vegan'],
        'halal': ['halal'],
        'delivery': ['delivery', 'giao hàng', 'đặt về'],
        'cheap': ['rẻ', 'bình dân', 'giá tốt']
    }
    
    for tag, keywords in tag_keywords.items():
        if any(kw in user_lower for kw in keywords):
            atmosphere_tags.append(tag)
    
    return atmosphere_tags

# Pre-compute restaurant embeddings for efficiency
print("🔄 Pre-computing restaurant embeddings...")
# Combine tags, cuisine, and name for richer embeddings
df["search_text"] = df["tags"] + " " + df["cuisine"] + " " + df["name"]
restaurant_embeddings = embed_model.encode(df["search_text"].tolist(), show_progress_bar=True)
df["embedding"] = list(restaurant_embeddings)

def calculate_weighted_score(row, similarity, rating_weight=0.2):
    """Calculate weighted score combining similarity and rating"""
    normalized_rating = row['rating'] / 5.0  # Normalize to 0-1
    final_score = (1 - rating_weight) * similarity + rating_weight * normalized_rating
    return final_score

def recommend_restaurants(user_input, city_filter=None, cuisine_filter=None, 
                         price_filter=None, top_n=5, use_rating=True):
    """Recommend restaurants based on user input with multiple filters"""
    
    if not user_input.strip():
        print("⚠️ Please enter what you want to eat!")
        return pd.DataFrame()
    
    tokenized_text = word_tokenize(user_input, format="text")
    # Extract keywords
    try:
        keywords = kw_model.extract_keywords(
            tokenized_text,
            keyphrase_ngram_range=(1,4),
            stop_words=stop_words_vi,
            top_n=10,
            use_mmr=True,
            nr_candidates=50,
            diversity=0.7
        )
        user_keywords = [kw[0] for kw in keywords]
        print(f"🔑 Extracted keywords: {user_keywords}")
        
        if not user_keywords:
            print("⚠️ No keywords extracted. Using original input.")
            user_keywords = [user_input]
    except Exception as e:
        print(f"⚠️ Keyword extraction failed: {e}. Using original input.")
        user_keywords = [user_input]
    
    # Extract atmosphere tags and add to search
    atmosphere_tags = extract_atmosphere_tags(user_input)
    if atmosphere_tags:
        print(f"🏷️ Detected preferences: {', '.join(atmosphere_tags)}")
        user_keywords.extend(atmosphere_tags)
    
    # Encode user query
    search_query = " ".join(user_keywords)
    user_vec = embed_model.encode(search_query)
    
    # Calculate similarities efficiently
    similarities = cosine_similarity([user_vec], list(df["embedding"]))[0]
    
    # Start with full dataframe
    filtered_df = df.copy()
    
    # Filter by city if specified
    if city_filter:
        filtered_df = filtered_df[filtered_df["city"].str.contains(city_filter, case=False, na=False)]
        print(f"📍 Filtering by city: {city_filter}")
    
    # Filter by cuisine if specified
    if cuisine_filter:
        filtered_df = filtered_df[filtered_df["cuisine"].str.contains(cuisine_filter, case=False, na=False)]
        print(f"🍽️ Filtering by cuisine: {cuisine_filter}")
    
    # Filter by price range if specified
    if price_filter:
        filtered_df = filtered_df[filtered_df["price_range"] == price_filter]
        print(f"💰 Filtering by price: {price_filter}")
    
    # Check if we have results
    if filtered_df.empty:
        print(f"⚠️ No restaurants found with the specified filters.")
        print("💡 Try broadening your search criteria.")
        return pd.DataFrame()
    
    # Get similarities for filtered restaurants
    filtered_indices = filtered_df.index
    filtered_similarities = similarities[filtered_indices]
    
    # Calculate weighted scores
    if use_rating:
        filtered_df = filtered_df.copy()
        filtered_df["similarity"] = filtered_similarities
        filtered_df["final_score"] = filtered_df.apply(
            lambda row: calculate_weighted_score(row, row["similarity"]), axis=1
        )
        sort_column = "final_score"
    else:
        filtered_df = filtered_df.copy()
        filtered_df["similarity"] = filtered_similarities
        filtered_df["final_score"] = filtered_similarities
        sort_column = "final_score"
    
    # Get top recommendations
    recommendations = filtered_df.sort_values(by=sort_column, ascending=False).head(top_n)
    
    # Display results
    print(f"\n🏆 Top {len(recommendations)} recommended restaurants:")
    print("=" * 80)
    for idx, (_, row) in enumerate(recommendations.iterrows(), 1):
        # Truncate tags for display
        tags_display = row['tags'][:80] + "..." if len(row['tags']) > 80 else row['tags']
        print(f"\n{idx}. 🍽️ {row['name']}")
        print(f"   📍 {row['city']} | 🍴 {row['cuisine']} | 💵 {row['price_range']}")
        print(f"   ⭐ {row['rating']:.1f} | 🎯 Match: {row['similarity']:.3f}")
        print(f"   🏷️ {tags_display}")
    
    print("=" * 80)
    
    return recommendations[["name", "city", "cuisine", "price_range", "tags", "rating", "similarity", "final_score"]]

def interactive_search():
    """Interactive restaurant search with smart filters"""
    print("\n" + "="*80)
    print("🍜 VIETNAMESE RESTAURANT RECOMMENDATION SYSTEM")
    print("="*80)
    
    user_input = input("\n🗣️ Bạn muốn ăn gì hôm nay? (What do you want to eat today?): ").strip()
    
    if not user_input:
        print("⚠️ Please enter something!")
        return
    
    # Auto-extract filters from user input
    city = extract_city(user_input)
    cuisine = extract_cuisine(user_input)
    price = extract_price_preference(user_input)
    
    # Display detected filters
    print("\n🔍 Analyzing your request...")
    if city:
        print(f"✅ Detected city: {city}")
    if cuisine:
        print(f"✅ Detected cuisine: {cuisine}")
    if price:
        print(f"✅ Detected price range: {price}")
    
    # Get recommendations
    results = recommend_restaurants(
        user_input, 
        city_filter=city, 
        cuisine_filter=cuisine,
        price_filter=price,
        top_n=5
    )
    
    # Option to see more or refine search
    if not results.empty:
        print("\n💬 Options:")
        print("  1. See more recommendations (type 'more')")
        print("  2. Filter by city (type city name)")
        print("  3. New search (type 'new')")
        print("  4. Exit (type 'exit')")
        
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == 'more':
            recommend_restaurants(
                user_input, 
                city_filter=city, 
                cuisine_filter=cuisine,
                price_filter=price,
                top_n=10
            )
        elif choice == 'new':
            interactive_search()
        elif choice in ['đà nẵng', 'hà nội', 'hồ chí minh', 'nha trang', 'đà lạt']:
            recommend_restaurants(
                user_input, 
                city_filter=choice.title(),
                cuisine_filter=cuisine,
                price_filter=price,
                top_n=5
            )
        elif choice != 'exit':
            print("Invalid option. Exiting...")

if __name__ == "__main__":
    interactive_search()