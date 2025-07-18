import json
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# Example JSON data
json_data = '''
[
    {"productId": "123", "name": "T-Shirt", "price": 19.99, "ratingCount": 45, "availableSizes": ["S", "M", "L"]},
    {"productId": "456", "name": "Jeans", "price": 49.99, "ratingCount": 120, "availableSizes": ["M", "L", "XL"]},
    {"productId": "789", "name": "Sneakers", "price": 89.99, "ratingCount": 89, "availableSizes": ["S", "L"]}
]
'''

# Load JSON data
data = json.loads(json_data)

# Convert JSON to DataFrame
df = pd.DataFrame(data)

# Define product-related keywords
product_keywords = ['ratingCount', 'availableSizes', 'productId', 'price', 'salePrice']

# Function to extract product-related keywords
def extract_keywords(row, keywords):
    extracted = {}
    for key, value in row.items():
        if key in keywords:
            extracted[key] = value
    return extracted

# Apply the function to each row
df['extracted_keywords'] = df.apply(lambda row: extract_keywords(row, product_keywords), axis=1)

# Display the extracted keywords
print(df['extracted_keywords'])

# Optional: Train a simple model to predict keywords (example)
# Here we use a simple text-based model to predict if a field is a product-related keyword
# This is just an illustrative example and may not be practical for all cases

# Create a dataset for training
X = df.to_string(index=False)  # Convert DataFrame to string for simplicity
y = [1 if any(keyword in X for keyword in product_keywords) else 0 for _ in range(len(df))]

# Vectorize the text data
X = df['extracted_keywords'].apply(lambda x: ' '.join(x.values())).tolist()
vectorizer = CountVectorizer()
X_vec = vectorizer.fit_transform(X)

# Train a simple Naive Bayes classifier
model = MultinomialNB()
model.fit(X_vec, y)

# Predict product-related keywords
df['is_product_keyword'] = model.predict(X_vec)

# Display the results
print(df[['extracted_keywords', 'is_product_keyword']])