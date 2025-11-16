#!/usr/bin/env python3
"""
Text Matching Module
Finds matching text segments in database using semantic similarity.
Returns timestamp information for matched segments.
"""

from typing import List, Dict, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import hashlib


class TextMatcher:
    """
    Matches text segments using semantic similarity.
    Supports both TF-IDF (fast) and sentence embeddings (accurate).
    """
    
    def __init__(self, use_semantic_embeddings: bool = True):
        """
        Initialize text matcher.
        
        Args:
            use_semantic_embeddings: If True, uses sentence-transformers (slower but more accurate)
                                    If False, uses TF-IDF (faster but less accurate)
        """
        self.use_semantic = use_semantic_embeddings
        
        if self.use_semantic:
            print("Loading semantic text model (sentence-transformers)...")
            print("(This will download ~100MB on first run)")
            # Use a lightweight but effective model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✓ Model loaded\n")
        else:
            self.model = None
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not text1 or not text2:
            return 0.0
        
        if self.use_semantic:
            # Use sentence embeddings
            embeddings = self.model.encode([text1, text2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(similarity)
        else:
            # Use TF-IDF
            try:
                vectorizer = TfidfVectorizer()
                tfidf = vectorizer.fit_transform([text1, text2])
                similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
                return float(similarity)
            except:
                return 0.0
    
    def find_matching_segments(
        self,
        query_text: str,
        database_segments: List[Dict],
        threshold: float = 0.75,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Find matching segments in database for a query text.
        
        Args:
            query_text: Text to search for
            database_segments: List of segments with 'text' and 'timestamp' fields
            threshold: Minimum similarity threshold (0.0 to 1.0)
            top_k: Return top K matches
            
        Returns:
            List of matches sorted by similarity:
            [
                {
                    'segment': <original_segment_dict>,
                    'similarity': 0.95,
                    'timestamp': 120.0
                },
                ...
            ]
        """
        if not query_text:
            return []
        
        matches = []
        
        for segment in database_segments:
            if not segment.get('text'):
                continue
            
            similarity = self.calculate_similarity(query_text, segment['text'])
            
            if similarity >= threshold:
                matches.append({
                    'segment': segment,
                    'similarity': similarity,
                    'timestamp': segment.get('timestamp', 0.0),
                    'text': segment['text']
                })
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Return top K
        return matches[:top_k]
    
    def find_best_match_in_database(
        self,
        query_segments: List[Dict],
        database: Dict[str, List[Dict]],
        threshold: float = 0.75,
        min_consecutive_matches: int = 2
    ) -> Dict:
        """
        Find best matching video and timestamp range in database.
        
        Args:
            query_segments: List of transcript segments from user's video
            database: Dict mapping video_id -> list of transcript segments
            threshold: Minimum similarity threshold
            min_consecutive_matches: Minimum number of consecutive matching segments
            
        Returns:
            {
                'video_id': 'video_123',
                'matches': [
                    {
                        'query_timestamp': 0.0,
                        'db_timestamp': 120.0,
                        'similarity': 0.95,
                        'query_text': '...',
                        'db_text': '...'
                    },
                    ...
                ],
                'start_timestamp': 120.0,
                'end_timestamp': 180.0,
                'avg_similarity': 0.92,
                'confidence': 'high'  # high/medium/low
            }
            or None if no match found
        """
        best_match = None
        best_score = 0
        
        for video_id, db_segments in database.items():
            # For each segment in query video
            for i, query_seg in enumerate(query_segments):
                if not query_seg.get('text'):
                    continue
                
                # Find matching segments in this video
                matches = self.find_matching_segments(
                    query_seg['text'],
                    db_segments,
                    threshold=threshold,
                    top_k=10
                )
                
                if not matches:
                    continue
                
                # Try to build consecutive match sequence
                for match in matches:
                    sequence = self._build_match_sequence(
                        query_segments[i:],
                        db_segments,
                        match['timestamp'],
                        threshold
                    )
                    
                    if len(sequence) >= min_consecutive_matches:
                        avg_sim = np.mean([m['similarity'] for m in sequence])
                        score = avg_sim * len(sequence)  # Weighted by length
                        
                        if score > best_score:
                            best_score = score
                            best_match = {
                                'video_id': video_id,
                                'matches': sequence,
                                'start_timestamp': sequence[0]['db_timestamp'],
                                'end_timestamp': sequence[-1]['db_timestamp'] + sequence[-1].get('duration', 30),
                                'avg_similarity': avg_sim,
                                'num_matches': len(sequence)
                            }
        
        if best_match:
            # Determine confidence level
            if best_match['avg_similarity'] >= 0.85 and best_match['num_matches'] >= 3:
                best_match['confidence'] = 'high'
            elif best_match['avg_similarity'] >= 0.75 and best_match['num_matches'] >= 2:
                best_match['confidence'] = 'medium'
            else:
                best_match['confidence'] = 'low'
        
        return best_match
    
    def _build_match_sequence(
        self,
        query_segments: List[Dict],
        db_segments: List[Dict],
        start_db_timestamp: float,
        threshold: float
    ) -> List[Dict]:
        """
        Build a sequence of consecutive matches starting from a timestamp.
        
        Returns:
            List of match dictionaries
        """
        sequence = []
        
        # Find starting segment in database
        db_idx = None
        for i, seg in enumerate(db_segments):
            if seg.get('timestamp') == start_db_timestamp:
                db_idx = i
                break
        
        if db_idx is None:
            return []
        
        # Try to match consecutive segments
        for query_idx, query_seg in enumerate(query_segments):
            if db_idx + query_idx >= len(db_segments):
                break
            
            db_seg = db_segments[db_idx + query_idx]
            
            if not query_seg.get('text') or not db_seg.get('text'):
                break
            
            similarity = self.calculate_similarity(query_seg['text'], db_seg['text'])
            
            if similarity < threshold:
                break
            
            sequence.append({
                'query_timestamp': query_seg.get('timestamp', 0.0),
                'db_timestamp': db_seg.get('timestamp', 0.0),
                'similarity': similarity,
                'query_text': query_seg['text'],
                'db_text': db_seg['text'],
                'duration': db_seg.get('duration', 30)
            })
        
        return sequence


def format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


if __name__ == "__main__":
    # Quick test
    matcher = TextMatcher(use_semantic_embeddings=True)
    
    text1 = "The Federal Reserve has decided to maintain interest rates at their current level."
    text2 = "The Fed decided to keep interest rates unchanged for now."
    text3 = "The weather today is sunny and warm."
    
    sim1 = matcher.calculate_similarity(text1, text2)
    sim2 = matcher.calculate_similarity(text1, text3)
    
    print(f"Similarity (same topic): {sim1:.2%}")
    print(f"Similarity (different topic): {sim2:.2%}")

