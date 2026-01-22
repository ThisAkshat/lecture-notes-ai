import sys
sys.path.append('.')
from summarize import summarize_text, generate_quiz

# Test text
lecture_text = """
Machine learning is a branch of artificial intelligence. 
It focuses on building systems that learn from data. 
There are three main types: supervised learning, unsupervised learning, and reinforcement learning.
Supervised learning uses labeled data to train models.
Unsupervised learning finds patterns in unlabeled data.
Reinforcement learning uses rewards and punishments to train agents.
"""

print("Testing summarization...")
summary = summarize_text(lecture_text)
print("Summary:", summary)

print("\nTesting quiz generation...")
quiz = generate_quiz(lecture_text)
for q in quiz:
    print(q["question"])
    print("Answer:", q["answer"])
    print()
