import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import SearchQuery, Book, Notification

def find_similar_resources():
    missed_queries = SearchQuery.objects.all()
    books = Book.objects.all()

    if not missed_queries.exists() or not books.exists():
        return

    vectorizer = TfidfVectorizer()

    # Kitoblar va qidiruv so‘rovlarining matnini yig‘ish
    book_texts = [f"{b.name} {b.about} {b.key_words}" for b in books]
    missed_queries_texts = [q.query for q in missed_queries]

    all_texts = book_texts + missed_queries_texts

    tfidf_matrix = vectorizer.fit_transform(all_texts)

    book_vectors = tfidf_matrix[:len(book_texts)]
    missed_vectors = tfidf_matrix[len(book_texts):]

    book_sim_matrix = cosine_similarity(missed_vectors, book_vectors)

    # O‘xshash natijalarni qayta ishlash
    new_notifications = []
    for i, missed_query in enumerate(missed_queries):
        for j, book in enumerate(books):
            if book_sim_matrix[i][j] > 0.6:  # 60% o‘xshashlik
                new_notifications.append(Notification(
                    user=missed_query.user,
                    message=f"📚 Yangi kitob qo‘shildi: {book.name}"
                ))

    # Bildirishnomalarni optimallashtirib bazaga qo‘shish
    Notification.objects.bulk_create(new_notifications)
