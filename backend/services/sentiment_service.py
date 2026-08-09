from textblob import TextBlob
from typing import Dict, Any, List

class SentimentService:
    def __init__(self):
        pass

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyzes polarity and subjectivity of a given text, and classifies it."""
        if not text or not text.strip():
            return {
                "text": "",
                "polarity": 0.0,
                "subjectivity": 0.0,
                "label": "Neutral",
                "intensity": "Neutral",
                "sentences": []
            }

        blob = TextBlob(text)
        overall_polarity = blob.sentiment.polarity
        overall_subjectivity = blob.sentiment.subjectivity

        # Classify the sentiment label
        if overall_polarity > 0.5:
            label = "Positive"
            intensity = "Strongly Positive"
        elif overall_polarity > 0.05:
            label = "Positive"
            intensity = "Mildly Positive"
        elif overall_polarity < -0.5:
            label = "Negative"
            intensity = "Strongly Negative"
        elif overall_polarity < -0.05:
            label = "Negative"
            intensity = "Mildly Negative"
        else:
            label = "Neutral"
            intensity = "Neutral"

        # Sentence-by-sentence analysis
        sentences_analysis = []
        for sentence in blob.sentences:
            s_polarity = sentence.sentiment.polarity
            s_subjectivity = sentence.sentiment.subjectivity
            
            if s_polarity > 0.05:
                s_label = "Positive"
            elif s_polarity < -0.05:
                s_label = "Negative"
            else:
                s_label = "Neutral"

            sentences_analysis.append({
                "text": str(sentence),
                "polarity": float(s_polarity),
                "subjectivity": float(s_subjectivity),
                "label": s_label
            })

        return {
            "text": text,
            "polarity": float(overall_polarity),
            "subjectivity": float(overall_subjectivity),
            "label": label,
            "intensity": intensity,
            "sentences": sentences_analysis
        }

    def batch_analyze(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Performs sentiment analysis on multiple texts."""
        results = []
        for text in texts:
            analysis = self.analyze_sentiment(text)
            results.append({
                "text": text,
                "polarity": analysis["polarity"],
                "subjectivity": analysis["subjectivity"],
                "label": analysis["label"]
            })
        return results
