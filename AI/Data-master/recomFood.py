import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from underthesea import word_tokenize
import numpy as np
import torch
import re
from collections import Counter

# Try to import KeyBERT, fall back to simple extraction if it fails
try:
    from keybert import KeyBERT
    KEYBERT_AVAILABLE = True
    print("✅ KeyBERT loaded successfully")
except ImportError as e:
    KEYBERT_AVAILABLE = False
    print(f"⚠️ KeyBERT not available. Using fallback keyword extraction")

# Load data
print("📂 Loading data...")
restaurants_df = pd.read_csv(r"C:\python\Projects\TOURISM\AI\Data-master\restaurants_100_improved.csv")
menus_df = pd.read_csv(r"C:\python\Projects\TOURISM\AI\Data-master\menus_100_improved.csv")

# Merge restaurant and menu data
print("🔗 Merging restaurant and menu data...")
# Create a mapping from restaurant_id to restaurant info
restaurant_info = restaurants_df.set_index('restaurant_id')[['name', 'city', 'cuisine', 'price_range', 'rating', 'tags']].to_dict('index')

# Add restaurant info to menu items
menus_df['restaurant_name'] = menus_df['restaurant_id'].map(lambda x: restaurant_info.get(x, {}).get('name', 'Unknown'))
menus_df['city'] = menus_df['restaurant_id'].map(lambda x: restaurant_info.get(x, {}).get('city', 'Unknown'))
menus_df['cuisine'] = menus_df['restaurant_id'].map(lambda x: restaurant_info.get(x, {}).get('cuisine', 'Unknown'))
menus_df['restaurant_rating'] = menus_df['restaurant_id'].map(lambda x: restaurant_info.get(x, {}).get('rating', 0))
menus_df['restaurant_tags'] = menus_df['restaurant_id'].map(lambda x: restaurant_info.get(x, {}).get('tags', ''))
menus_df['price_range'] = menus_df['restaurant_id'].map(lambda x: restaurant_info.get(x, {}).get('price_range', '₫₫'))

# Clean data
for col in ['dish_name', 'category', 'description', 'tags', 'city', 'cuisine', 'restaurant_name', 'restaurant_tags']:
    if col in menus_df.columns:
        menus_df[col] = menus_df[col].fillna("").astype(str)

menus_df['price_vnd'] = pd.to_numeric(menus_df['price_vnd'], errors='coerce').fillna(0)
menus_df['restaurant_rating'] = pd.to_numeric(menus_df['restaurant_rating'], errors='coerce').fillna(0)

# Initialize models
print("🤖 Loading AI models...")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"   Using device: {device}")

embed_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device=device)

# Initialize KeyBERT if available
if KEYBERT_AVAILABLE:
    try:
        kw_model = KeyBERT(model=embed_model)
        print("✅ KeyBERT initialized")
    except Exception as e:
        print(f"⚠️ KeyBERT initialization failed: {e}")
        KEYBERT_AVAILABLE = False

# Vietnamese stop words
stop_words_vi = [
    'của', 'và', 'các', 'có', 'được', 'cho', 'là', 'với', 
    'để', 'trong', 'không', 'một', 'này', 'những', 'đã', 
    'như', 'bởi', 'từ', 'hoặc', 'đến', 'khi', 'cũng', 'nhưng',
    'thì', 'nào', 'đây', 'rất', 'sẽ', 'vào', 'ra', 'ở', 'về'
]

# Food keywords for better matching
food_keywords = {
    'phở': ['phở', 'pho'],
    'bún': ['bún', 'bun'],
    'cơm': ['cơm', 'com', 'rice', 'cơm tấm'],
    'bánh mì': ['bánh mì', 'banh mi'],
    'nem': ['nem', 'chả giò', 'spring roll'],
    'gỏi': ['gỏi', 'salad', 'goi cuon'],
    'sushi': ['sushi', 'sashimi'],
    'ramen': ['ramen', 'mì nhật'],
    'bbq': ['bbq', 'nướng', 'grilled', 'bulgogi'],
    'curry': ['curry', 'cà ri'],
    'pasta': ['pasta', 'mỳ ý', 'spaghetti'],
    'pizza': ['pizza'],
    'burger': ['burger', 'hamburger'],
    'steak': ['steak', 'bít tết'],
    'chay': ['chay', 'vegetarian', 'vegan'],
    'hải sản': ['hải sản', 'seafood', 'tôm', 'cua', 'cá'],
    'gà': ['gà', 'chicken'],
    'bò': ['bò', 'beef'],
    'heo': ['heo', 'pork', 'lợn'],
    'tráng miệng': ['tráng miệng', 'dessert', 'ngọt', 'chè', 'kem'],
    'đồ uống': ['đồ uống', 'drink', 'nước', 'trà', 'cà phê']
}

def simple_keyword_extraction(text, stop_words, top_n=10):
    """Fallback keyword extraction without KeyBERT"""
    text = text.lower()
    try:
        tokens = word_tokenize(text, format="text").split()
    except:
        tokens = text.split()
    
    tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    word_freq = Counter(tokens)
    keywords = [word for word, _ in word_freq.most_common(top_n)]
    return keywords

def extract_city(user_input):
    """Extract city from user input"""
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

def extract_price_preference(user_input):
    """Extract price preference from user input"""
    user_lower = user_input.lower()
    
    cheap_keywords = ['rẻ', 'bình dân', 'sinh viên', 'tiết kiệm', 'budget', 'cheap', 'dưới 100k', 'dưới 100']
    mid_keywords = ['vừa phải', 'trung bình', 'hợp lý', '100k-200k']
    expensive_keywords = ['cao cấp', 'sang trọng', 'đắt', 'fine dining', 'luxury', 'trên 200k']
    
    if any(kw in user_lower for kw in cheap_keywords):
        return 'cheap'  # < 100k
    elif any(kw in user_lower for kw in expensive_keywords):
        return 'expensive'  # > 200k
    elif any(kw in user_lower for kw in mid_keywords):
        return 'mid'  # 100k-200k
    return None

def extract_category(user_input):
    """Extract food category from user input"""
    user_lower = user_input.lower()
    
    if any(kw in user_lower for kw in ['khai vị', 'appetizer', 'starter', 'gỏi', 'nem']):
        return 'Khai vị'
    elif any(kw in user_lower for kw in ['món chính', 'main', 'main course', 'bữa chính']):
        return 'Món chính'
    elif any(kw in user_lower for kw in ['tráng miệng', 'dessert', 'ngọt', 'chè', 'bánh ngọt']):
        return 'Tráng miệng'
    elif any(kw in user_lower for kw in ['đồ uống', 'drink', 'nước', 'uống', 'trà', 'cà phê']):
        return 'Đồ uống'
    return None

# Pre-compute food embeddings
print("📊 Pre-computing food embeddings...")
menus_df["search_text"] = (
    menus_df["dish_name"] + " " + 
    menus_df["description"] + " " + 
    menus_df["tags"] + " " + 
    menus_df["category"] + " " +
    menus_df["cuisine"] + " " +
    menus_df["restaurant_tags"]
)
food_embeddings = embed_model.encode(menus_df["search_text"].tolist(), show_progress_bar=True)
menus_df["embedding"] = list(food_embeddings)

print(f"✅ Loaded {len(menus_df)} dishes from {restaurants_df['name'].nunique()} restaurants")

def recommend_food(user_input, city_filter=None, price_filter=None, category_filter=None, top_n=10):
    """Recommend food dishes based on user input"""
    
    if not user_input.strip():
        print("⚠️ Please tell me what you want to eat!")
        return pd.DataFrame()
    
    # Extract keywords
    try:
        if KEYBERT_AVAILABLE:
            tokenized_text = word_tokenize(user_input, format="text")
            keywords = kw_model.extract_keywords(
                tokenized_text,
                keyphrase_ngram_range=(1, 3),
                stop_words=stop_words_vi,
                top_n=10,
                use_mmr=True,
                diversity=0.7
            )
            user_keywords = [kw[0] for kw in keywords]
            print(f"🔑 Keywords (KeyBERT): {user_keywords}")
        else:
            user_keywords = simple_keyword_extraction(user_input, stop_words_vi, top_n=10)
            print(f"🔑 Keywords (Simple): {user_keywords}")
        
        if not user_keywords:
            user_keywords = [user_input]
    except Exception as e:
        print(f"⚠️ Keyword extraction failed: {e}")
        user_keywords = [user_input]
    
    # Encode user query
    search_query = " ".join(user_keywords)
    user_vec = embed_model.encode(search_query)
    
    # Calculate similarities
    similarities = cosine_similarity([user_vec], list(menus_df["embedding"]))[0]
    
    # Start with full dataframe
    filtered_df = menus_df.copy()
    
    # Filter by city
    if city_filter:
        filtered_df = filtered_df[filtered_df["city"].str.contains(city_filter, case=False, na=False)]
        print(f"📍 Filtering by city: {city_filter}")
    
    # Filter by price
    if price_filter:
        if price_filter == 'cheap':
            filtered_df = filtered_df[filtered_df["price_vnd"] < 100000]
            print(f"💰 Filtering by price: < 100,000 VNĐ")
        elif price_filter == 'mid':
            filtered_df = filtered_df[(filtered_df["price_vnd"] >= 100000) & (filtered_df["price_vnd"] <= 200000)]
            print(f"💰 Filtering by price: 100,000 - 200,000 VNĐ")
        elif price_filter == 'expensive':
            filtered_df = filtered_df[filtered_df["price_vnd"] > 200000]
            print(f"💰 Filtering by price: > 200,000 VNĐ")
    
    # Filter by category
    if category_filter:
        filtered_df = filtered_df[filtered_df["category"].str.contains(category_filter, case=False, na=False)]
        print(f"🍽️ Filtering by category: {category_filter}")
    
    # Check if we have results
    if filtered_df.empty:
        print(f"⚠️ No dishes found with the specified filters.")
        print("💡 Try broadening your search criteria.")
        return pd.DataFrame()
    
    # Get similarities for filtered items
    filtered_indices = filtered_df.index
    filtered_similarities = similarities[filtered_indices]
    
    # Add similarity scores
    filtered_df = filtered_df.copy()
    filtered_df["similarity"] = filtered_similarities
    
    # Calculate final score (70% similarity + 30% restaurant rating)
    filtered_df["final_score"] = (
        0.7 * filtered_df["similarity"] + 
        0.3 * (filtered_df["restaurant_rating"] / 5.0)
    )
    
    # Get top recommendations
    recommendations = filtered_df.sort_values(by="final_score", ascending=False).head(top_n)
    
    # Display results
    print(f"\n🏆 Top {len(recommendations)} recommended dishes:")
    print("=" * 90)
    
    for idx, (_, row) in enumerate(recommendations.iterrows(), 1):
        print(f"\n{idx}. 🍽️ {row['dish_name']} - {int(row['price_vnd']):,} VNĐ")
        print(f"   🏪 {row['restaurant_name']} ({row['city']})")
        print(f"   🍴 {row['cuisine']} | 📂 {row['category']}")
        print(f"   ⭐ Restaurant: {row['restaurant_rating']:.1f} | 🎯 Match: {row['similarity']:.3f}")
        print(f"   📝 {row['description']}")
        print(f"   🏷️ {row['tags']}")
    
    print("=" * 90)
    
    return recommendations[[
        "dish_name", "restaurant_name", "city", "cuisine", "category",
        "price_vnd", "description", "restaurant_rating", "similarity", "final_score"
    ]]

def interactive_food_search():
    """Interactive food search system"""
    print("\n" + "="*90)
    print("🍜 VIETNAMESE FOOD RECOMMENDATION SYSTEM")
    print("="*90)
    print("\nTips: You can search by:")
    print("  • Dish name (e.g., 'phở', 'sushi', 'pizza')")
    print("  • Taste/Style (e.g., 'cay', 'ngọt', 'chua', 'spicy')")
    print("  • City (e.g., 'Hà Nội', 'Sài Gòn', 'Đà Nẵng')")
    print("  • Price (e.g., 'rẻ', 'budget', 'cao cấp')")
    print("  • Category (e.g., 'món chính', 'tráng miệng', 'đồ uống')")
    
    user_input = input("\n🗣️ Bạn muốn ăn gì hôm nay? (What do you want to eat?): ").strip()
    
    if not user_input:
        print("⚠️ Please enter something!")
        return
    
    # Auto-extract filters
    city = extract_city(user_input)
    price = extract_price_preference(user_input)
    category = extract_category(user_input)
    
    # Display detected filters
    print("\n🔍 Analyzing your request...")
    if city:
        print(f"✅ Detected city: {city}")
    if price:
        print(f"✅ Detected price preference: {price}")
    if category:
        print(f"✅ Detected category: {category}")
    
    # Get recommendations
    results = recommend_food(
        user_input,
        city_filter=city,
        price_filter=price,
        category_filter=category,
        top_n=10
    )
    
    # Options
    if not results.empty:
        print("\n💬 Options:")
        print("  1. New search (type 'new')")
        print("  2. Filter by city (type city name)")
        print("  3. Show cheaper options (type 'cheap')")
        print("  4. Show more expensive options (type 'expensive')")
        print("  5. Exit (type 'exit')")
        
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == 'new':
            interactive_food_search()
        elif choice == 'cheap':
            recommend_food(user_input, city_filter=city, price_filter='cheap', category_filter=category, top_n=10)
        elif choice == 'expensive':
            recommend_food(user_input, city_filter=city, price_filter='expensive', category_filter=category, top_n=10)
        elif choice in ['đà nẵng', 'hà nội', 'hồ chí minh', 'sài gòn', 'nha trang']:
            city_map = {
                'sài gòn': 'Hồ Chí Minh',
                'hồ chí minh': 'Hồ Chí Minh',
                'hà nội': 'Hà Nội',
                'đà nẵng': 'Đà Nẵng',
                'nha trang': 'Nha Trang'
            }
            recommend_food(user_input, city_filter=city_map.get(choice, choice.title()), price_filter=price, category_filter=category, top_n=10)
        elif choice == 'exit':
            print("Thanks for using the system! 👋")

if __name__ == "__main__":
    interactive_food_search()