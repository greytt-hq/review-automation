import csv
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


try:
    from tqdm import tqdm
except ImportError:
    def tqdm(x, **kwargs): return x

# Keyword-based sentence classification
def classify_sentence(sentence):
    sentence = sentence.lower()
    words = sentence.split()
    result = set()

    def contains_all(word_list):
        return all(word in sentence for word in word_list)

    if any(word in words for word in ['stairs', 'steps', 'climbing']):
        result.add("2a_1")
    if any(word in words for word in ['ramp', 'incline']):
        result.add("2b_1")
    if ('dark' in words or 'poor lighting' in sentence) and ('room' in words or 'lobby' in words):
        result.add("2d")
    if 'shower' in words:
        result.add("2e_1")
    if 'bathtub' in words and ('safe' in words or 'climb-in shower' in sentence):
        result.update(["2f_1", "2f_2"])
    if 'toilet' in words and 'rails' in words:
        result.add("2f_4")
    if 'elevators' in words or 'elevator' in words:
        result.add("2g_1")
    if 'escalator' in words or 'escalators' in words:
        result.add("2h_1")
    if 'transport' in words and 'options' in words:
        result.add("3a_1")
    if 'buggy' in words or 'buggies' in words:
        result.add("3b")
    if 'shuttle' in words:
        result.add("3c")
    if 'conveniences' in words or 'convenience' in words:
        result.add("3d_1")
    if 'central' in words and 'location' in words:
        result.add("3d_2")
    if 'medical' in words:
        result.add("3e_1")
    if 'taxi' in words:
        result.add("3f")
    if 'doctor' in words:
        result.add("3g")
    if ('quiet' in words or 'noise' in words or 'noisy' in words) and 'room' in words:
        result.add("4a")
    if 'atm' in words:
        result.add("4b")
    if 'language' in words and 'spoken' in words:
        result.add("4c_1")
    if 'flexible' in words and ('check-in' in words or 'check-out' in words):
        result.add("4d")
    if 'pillow' in words:
        result.add("4e")
    if 'air conditioning' in sentence:
        result.add("4f")
    if 'power points' in sentence or 'power outlets' in sentence:
        result.add("4g")
    if 'valet parking' in sentence:
        result.add("4h")
    if any(phrase in sentence for phrase in ['concierge', 'luggage handling', 'luggage storage']):
        result.add("4i")
    if 'parking' in words and 'valet parking' not in sentence:
        result.add("4j")
    if 'vegetarian' in words:
        result.add("5a_1")
    if 'vegan' in words:
        result.add("5a_2")
    if 'halal' in words:
        result.add("5a_3")
    if 'low' in words and 'sodium' in words:
        result.add("5a_4")
    if 'diabetic' in words:
        result.add("5a_5")
    if 'low' in words and 'spice' in words:
        result.add("5a_6")
    if ('customize' in words or 'flexible' in words) and 'food' in words:
        result.add("5a_7")
    if 'coffee maker' in sentence or 'tea maker' in sentence:
        result.add("5b")
    if 'near' in words and any(word in words for word in ['restaurants', 'cafe', 'eateries']):
        result.add("5c_1")
    if ('anti-skid' in words or 'non-slip' in words) and 'floor' in words:
        result.add("6a")
    if 'spa' in words or 'wellness' in words:
        result.add("6b_1")
    if any(word in words for word in ['yoga', 'meditation', 'pilates']):
        result.add("6c_1")
    if 'gym' in words:
        result.add("6d_1")
    if 'adult friendly' in sentence or ('quiet' in words and ('pool' in words or 'hotel' in words)):
        result.add("6e")
    if any(word in words for word in ['elderly', 'senior', 'older']):
        result.add("7a")

    return list(result)

# Process a batch of reviews
def process_batch(batch_sentences, batch_review_data, writer, tokenizer, model, device):
    inputs = tokenizer(batch_sentences, return_tensors="pt", truncation=True, max_length=512, padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
    scores = torch.softmax(outputs.logits, dim=1).cpu().numpy()

    labels_batch = [classify_sentence(sentence) for sentence in batch_sentences]

    for sentence, review_data, labels, score in zip(batch_sentences, batch_review_data, labels_batch, scores):
        if labels:
            weighted_sentiment = sum(score[i] * (i + 1) for i in range(5))
            for label in labels:
                writer.writerow({
                    "Hotel Name": review_data['Hotel Name'],
                    "Rating": review_data['Rating'],
                    "Review": review_data['Review'],
                    "sentence": sentence.strip(),
                    "sentiment_score_1": round(score[0], 4),
                    "sentiment_score_2": round(score[1], 4),
                    "sentiment_score_3": round(score[2], 4),
                    "sentiment_score_4": round(score[3], 4),
                    "sentiment_score_5": round(score[4], 4),
                    "weighted_sentiment": round(weighted_sentiment, 4),
                    "classification_label": label
                })

# Main public function to run after scraping
def run_sentiment_analysis(input_file, output_file, batch_size=16):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
    model = AutoModelForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment").to(device)

    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=[
            "Hotel Name", "Rating", "Review", "sentence",
            "sentiment_score_1", "sentiment_score_2", "sentiment_score_3",
            "sentiment_score_4", "sentiment_score_5", "weighted_sentiment",
            "classification_label"
        ])
        writer.writeheader()

        batch_sentences = []
        batch_review_data = []

        for row in tqdm(reader, desc="Processing reviews"):
            review = row["review"]
            hotel = row["hotel_name"]
            rating = row["rating"]
            sentences = re.split(r'[.!?]', review)
            for sentence in sentences:
                if sentence.strip():
                    batch_sentences.append(sentence.strip())
                    batch_review_data.append({
                        "Hotel Name": hotel,
                        "Rating": rating,
                        "Review": review
                    })

                if len(batch_sentences) >= batch_size:
                    process_batch(batch_sentences, batch_review_data, writer, tokenizer, model, device)
                    batch_sentences, batch_review_data = [], []

        # Final leftover batch
        if batch_sentences:
            process_batch(batch_sentences, batch_review_data, writer, tokenizer, model, device)

        print(f"✅ Sentiment analysis done! Output saved to: {output_file}")
