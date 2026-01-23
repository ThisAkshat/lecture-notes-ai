import re
import time

def summarize_text(text):
    # Try using transformers if available
    try:
        from transformers import pipeline
        try:
            summarizer = pipeline("summarization", model="t5-small")
            
            # Clean text
            text = text.strip()
            
            # Check if text is long enough to summarize
            word_count = len(text.split())
            if word_count < 50:
                return text[:300] + ("..." if len(text) > 300 else "")
            
            # For T5, prefix needed
            input_text = "summarize: " + text
            
            # Adjust max_length based on input length
            if word_count < 100:
                max_len = 50
                min_len = 20
            elif word_count < 300:
                max_len = 80
                min_len = 30
            else:
                max_len = 150
                min_len = 50
            
            summary = summarizer(input_text, 
                                max_length=max_len, 
                                min_length=min_len, 
                                do_sample=False)
            return summary[0]['summary_text']
            
        except Exception as e:
            print(f"Transformers error: {e}")
            # Fall through to rule-based
            pass
    except ImportError:
        pass
    
    # RULE-BASED FALLBACK
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    if len(sentences) <= 3:
        return text
    
    # Score sentences
    scored = []
    keywords = ['important', 'key', 'main', 'conclusion', 'summary', 
                'therefore', 'because', 'thus', 'however', 'lesson', 
                'means', 'teaches', 'learn', 'understand', 'powerful']
    
    for i, sent in enumerate(sentences):
        score = 0
        
        if i == 0:
            score += 3
        elif i == len(sentences) - 1:
            score += 2
        elif i < 3:
            score += 2
        
        for kw in keywords:
            if kw in sent.lower():
                score += 3
        
        word_count = len(sent.split())
        if 12 <= word_count <= 25:
            score += 2
        elif word_count > 30:
            score -= 1
        
        scored.append((score, sent))
    
    scored.sort(reverse=True)
    top_sentences = [sent for _, sent in scored[:3]]
    
    final_summary = []
    for sent in sentences:
        if sent in top_sentences:
            final_summary.append(sent)
    
    return " ".join(final_summary) if final_summary else text[:300] + "..."

def generate_quiz(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    lesson_keywords = ['lesson', 'teaches', 'means', 'therefore', 'because', 
                      'important', 'key', 'main', 'conclusion']
    
    quiz_sentences = []
    for sent in sentences:
        if any(kw in sent.lower() for kw in lesson_keywords):
            if len(sent.split()) > 8:
                quiz_sentences.append(sent)
    
    if len(quiz_sentences) < 3:
        long_sents = [s for s in sentences if len(s.split()) > 12]
        quiz_sentences.extend(long_sents[:5-len(quiz_sentences)])
    
    quiz = []
    for i, sent in enumerate(quiz_sentences[:5]):
        words = sent.split()
        if len(words) > 6:
            import random
            pos = min(4, len(words)-1)
            blank_word = words[pos]
            
            import string
            blank_word = blank_word.translate(str.maketrans('', '', string.punctuation))
            
            if blank_word and len(blank_word) > 3:
                question = sent.replace(words[pos], "______")
                quiz.append({
                    "question": f"Q{i+1}: {question}",
                    "answer": blank_word
                })
    
    return quiz

# Test the functions
if __name__ == "__main__":
    test_text = "Machine learning is important for AI. It helps computers learn from data. Deep learning is a subset of machine learning."
    print("Test summary:", summarize_text(test_text))
    print("Test quiz:", generate_quiz(test_text))