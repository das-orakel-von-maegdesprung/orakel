from rank_bm25 import BM25Okapi

class BM25Search:
    def __init__(self, corpus):
        """
        corpus: List of raw text strings (documents)
        """
        self.corpus = corpus
        self.tokenized_corpus = [doc.lower().split() for doc in corpus]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def get_top_n(self, query: str, n: int = 3):
        tokenized_query = query.lower().split()
        return self.bm25.get_top_n(tokenized_query, self.corpus, n=n)

    def get_scores(self, query: str):
        tokenized_query = query.lower().split()
        return self.bm25.get_scores(tokenized_query)
