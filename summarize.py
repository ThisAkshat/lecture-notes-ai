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

def generate_quiz(text, min_questions=10, max_questions=15):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    if len(sentences) < min_questions:
        # Agar kam sentences hai toh paragraph break karo
        paragraphs = re.split(r'\n\s*\n', text)
        sentences = []
        for para in paragraphs:
            para_sents = re.split(r'(?<=[.!?])\s+', para)
            sentences.extend(para_sents)
    
    # Better keyword matching
    quiz_keywords = [
        'is', 'are', 'was', 'were', 'has', 'have', 'had',
        'means', 'defines', 'describes', 'explains', 'shows',
        'important', 'key', 'main', 'primary', 'essential',
        'because', 'therefore', 'thus', 'hence', 'consequently',
        'however', 'although', 'while', 'whereas',
        'example', 'instance', 'specifically',
        'first', 'second', 'third', 'finally',
        'lesson', 'teaches', 'learn', 'understand', 'concept',
        'advantage', 'disadvantage', 'benefit', 'limitation',
        'compare', 'contrast', 'difference', 'similarity'
    ]
    
    # Score each sentence for quiz potential
    scored_sentences = []
    for i, sent in enumerate(sentences):
        score = 0
        
        # Length based scoring
        words = sent.split()
        word_count = len(words)
        
        if 8 <= word_count <= 25:  # Ideal length for questions
            score += 5
        elif word_count > 25:  # Too long, but might be informative
            score += 2
        else:  # Too short
            score -= 3
        
        # Keyword matching
        sent_lower = sent.lower()
        for kw in quiz_keywords:
            if kw in sent_lower:
                score += 2
        
        # Position in text (introduction/conclusion are important)
        if i < 3:  # First few sentences
            score += 3
        if i > len(sentences) - 4:  # Last few sentences
            score += 2
        
        # Contains definitions or explanations
        if ' means ' in sent_lower or ' is ' in sent_lower or ' are ' in sent_lower:
            score += 3
        
        # Contains numbers or lists
        if any(word.isdigit() for word in words):
            score += 2
        
        scored_sentences.append((score, sent, words))
    
    # Sort by score and take top sentences
    scored_sentences.sort(reverse=True, key=lambda x: x[0])
    
    # Select sentences for quiz (try to get min_questions)
    selected_sentences = []
    for score, sent, words in scored_sentences:
        if len(words) >= 6:  # Minimum words for a meaningful blank
            selected_sentences.append((sent, words))
        if len(selected_sentences) >= max_questions:
            break
    
    # If still not enough, add more sentences
    if len(selected_sentences) < min_questions:
        for score, sent, words in scored_sentences:
            if (sent, words) not in selected_sentences and len(words) >= 5:
                selected_sentences.append((sent, words))
            if len(selected_sentences) >= min_questions:
                break
    
    # Generate quiz questions
    quiz = []
    used_blanks = set()  # To avoid duplicate blanks
    
    for i, (sent, words) in enumerate(selected_sentences[:max_questions]):
        if len(words) < 5:
            continue
        
        import random
        import string
        
        # Try to find a good word to blank (not too short, not too common)
        candidate_positions = []
        
        for pos in range(len(words)):
            word = words[pos]
            clean_word = word.translate(str.maketrans('', '', string.punctuation))
            
            # Skip if word is too short or common
            if len(clean_word) < 4:
                continue
            
            # Skip common words
            common_words = {'the', 'and', 'but', 'for', 'are', 'was', 'were', 'this', 'that', 'with'}
            if clean_word.lower() in common_words:
                continue
            
            # Score this position
            position_score = 0
            
            # Prefer nouns/verbs (simple heuristic)
            if len(clean_word) > 5:  # Longer words often more meaningful
                position_score += 2
            
            # Avoid first and last word
            if pos > 0 and pos < len(words) - 1:
                position_score += 1
            
            # Prefer words that appear important
            if clean_word[0].isupper() and pos > 0:  # Proper nouns (not at start)
                position_score += 3
            
            candidate_positions.append((position_score, pos, clean_word))
        
        if candidate_positions:
            # Pick the best position
            candidate_positions.sort(reverse=True, key=lambda x: x[0])
            best_score, best_pos, best_word = candidate_positions[0]
            
            # Avoid using same blank word multiple times
            if best_word.lower() not in used_blanks:
                used_blanks.add(best_word.lower())
                
                # Create question with blank
                question_parts = words.copy()
                question_parts[best_pos] = "______"
                question = " ".join(question_parts)
                
                quiz.append({
                    "question": question,
                    "answer": best_word
                })
    
    # If still not enough questions, create simpler ones
    if len(quiz) < min_questions and len(sentences) > 0:
        simple_count = min_questions - len(quiz)
        for i in range(min(simple_count, len(sentences))):
            sent = sentences[i]
            words = sent.split()
            
            if len(words) >= 6:
                # Simple approach: blank a middle word
                pos = len(words) // 2
                word = words[pos]
                clean_word = word.translate(str.maketrans('', '', string.punctuation))
                
                if len(clean_word) >= 3:
                    question_parts = words.copy()
                    question_parts[pos] = "______"
                    question = " ".join(question_parts)
                    
                    quiz.append({
                        "question": question,
                        "answer": clean_word
                    })
    
    return quiz[:max_questions]  # Return at most max_questions
# Test the functions
if __name__ == "__main__":
    test_text = """Machine learning is a branch of artificial intelligence that focuses on building systems that learn from data. 
    There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning.
    Supervised learning uses labeled data to train models for prediction or classification tasks.
    Unsupervised learning finds patterns and structures in unlabeled data without specific guidance.
    Reinforcement learning uses rewards and punishments to train agents through interaction with an environment.
    Deep learning is a subset of machine learning that uses neural networks with multiple layers.
    Neural networks are inspired by the structure and function of the human brain.
    Training a model requires a large dataset and computational resources.
    Overfitting occurs when a model learns the training data too well but fails to generalize to new data.
    Regularization techniques help prevent overfitting in machine learning models."""
    
    print("Test summary:", summarize_text(test_text))
    
    quiz = generate_quiz(test_text, min_questions=10, max_questions=15)
    print(f"\nGenerated {len(quiz)} quiz questions:")
    for i, q in enumerate(quiz):
        print(f"Q{i+1}: {q['question']}")
        print(f"Answer: {q['answer']}\n")