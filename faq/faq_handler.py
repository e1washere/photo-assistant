"""
FAQ Handler

Manages frequently asked questions and their answers, providing
intelligent responses based on user queries and photo analysis.
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import torch


class FAQHandler:
    """Handles FAQ operations and intelligent question matching."""
    
    def __init__(self, faq_file: Optional[str] = None):
        """
        Initialize FAQ handler.
        
        Args:
            faq_file: Path to FAQ JSON file. If None, uses default location.
        """
        if faq_file is None:
            faq_file = str(Path(__file__).parent.parent / "data" / "faq.json")
        
        self.faq_file = Path(faq_file)
        self.faq_data = self._load_faq_data()
        
        # Initialize sentence transformer model
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self._initialize_embeddings()
        except Exception as e:
            print(f"Warning: Could not initialize sentence transformer model: {e}")
            self.model = None
    
    def _load_faq_data(self) -> Dict[str, Any]:
        """
        Load FAQ data from JSON file.
        
        Returns:
            Dictionary containing FAQ data
        """
        try:
            if self.faq_file.exists():
                with open(self.faq_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._get_default_faq_data()
        except Exception as e:
            print(f"Error loading FAQ data: {e}")
            return self._get_default_faq_data()
    
    def _get_default_faq_data(self) -> Dict[str, Any]:
        """Return default FAQ data structure."""
        return {
            "categories": {
                "general": {
                    "name": "General Questions",
                    "questions": [
                        {
                            "question": "What can this photo assistant do?",
                            "answer": "This photo assistant can analyze images to detect objects, extract text, identify scenes, and answer questions about photos using AI-powered vision and language models."
                        },
                        {
                            "question": "How do I upload a photo?",
                            "answer": "You can upload photos through the web interface by clicking the upload button and selecting an image file from your device."
                        },
                        {
                            "question": "What file formats are supported?",
                            "answer": "The assistant supports common image formats including JPEG, PNG, GIF, and WebP files."
                        }
                    ]
                },
                "analysis": {
                    "name": "Photo Analysis",
                    "questions": [
                        {
                            "question": "What information can you extract from photos?",
                            "answer": "I can detect objects, recognize text (OCR), identify scenes and concepts, detect faces, and provide detailed descriptions of image content."
                        },
                        {
                            "question": "How accurate is the analysis?",
                            "answer": "The analysis uses state-of-the-art AI models with high accuracy, though results may vary depending on image quality and content complexity."
                        },
                        {
                            "question": "Can you read text in images?",
                            "answer": "Yes, I can extract and read text from images using optical character recognition (OCR) technology."
                        }
                    ]
                },
                "usage": {
                    "name": "Usage Tips",
                    "questions": [
                        {
                            "question": "How do I ask questions about my photos?",
                            "answer": "After uploading a photo, you can type questions in the chat interface. Ask about objects, colors, text, or any other aspects of the image."
                        },
                        {
                            "question": "What types of questions work best?",
                            "answer": "Specific questions work best, such as 'What objects do you see?', 'Is there text in this image?', or 'Describe the colors in this photo.'"
                        },
                        {
                            "question": "Can you compare multiple photos?",
                            "answer": "Currently, the assistant analyzes one photo at a time. You can upload different photos sequentially for comparison."
                        }
                    ]
                }
            },
            "metadata": {
                "version": "1.0",
                "last_updated": "2024-01-01",
                "total_questions": 9
            }
        }
    
    def get_all_questions(self) -> List[Dict[str, str]]:
        """
        Get all FAQ questions and answers.
        
        Returns:
            List of question-answer dictionaries
        """
        all_questions = []
        for category in self.faq_data.get("categories", {}).values():
            all_questions.extend(category.get("questions", []))
        return all_questions
    
    def search_questions(self, query: str) -> List[Dict[str, Any]]:
        """
        Search FAQ questions based on a query.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching questions with relevance scores
        """
        query_lower = query.lower()
        matches = []
        
        for category_name, category in self.faq_data.get("categories", {}).items():
            for qa in category.get("questions", []):
                question = qa["question"].lower()
                answer = qa["answer"].lower()
                
                # Calculate relevance score
                score = 0
                if query_lower in question:
                    score += 3
                if query_lower in answer:
                    score += 1
                
                if score > 0:
                    matches.append({
                        "question": qa["question"],
                        "answer": qa["answer"],
                        "category": category["name"],
                        "relevance_score": score
                    })
        
        # Sort by relevance score
        matches.sort(key=lambda x: x["relevance_score"], reverse=True)
        return matches
    
    def get_question_answer(self, question: str) -> Optional[str]:
        """
        Get answer for a specific question.
        
        Args:
            question: The question to find answer for
            
        Returns:
            Answer string if found, None otherwise
        """
        question_lower = question.lower()
        
        for category in self.faq_data.get("categories", {}).values():
            for qa in category.get("questions", []):
                if qa["question"].lower() == question_lower:
                    return qa["answer"]
        
        return None
    
    def add_question(self, category: str, question: str, answer: str) -> bool:
        """
        Add a new question to the FAQ.
        
        Args:
            category: Category name
            question: The question
            answer: The answer
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if category not in self.faq_data.get("categories", {}):
                self.faq_data["categories"][category] = {
                    "name": category.title(),
                    "questions": []
                }
            
            self.faq_data["categories"][category]["questions"].append({
                "question": question,
                "answer": answer
            })
            
            # Update metadata
            self.faq_data["metadata"]["total_questions"] += 1
            
            # Save to file
            self._save_faq_data()
            return True
            
        except Exception as e:
            print(f"Error adding question: {e}")
            return False
    
    def _save_faq_data(self) -> None:
        """Save FAQ data to JSON file."""
        try:
            # Ensure directory exists
            self.faq_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.faq_file, 'w', encoding='utf-8') as f:
                json.dump(self.faq_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving FAQ data: {e}")
    
    def get_categories(self) -> List[str]:
        """
        Get list of FAQ categories.
        
        Returns:
            List of category names
        """
        return list(self.faq_data.get("categories", {}).keys())
    
    def _initialize_embeddings(self) -> None:
        """
        Initialize embeddings for all FAQ questions.
        """
        if not self.model:
            return
        
        try:
            all_questions = self.get_all_questions()
            questions_text = [qa['question'] for qa in all_questions]
            
            # Generate embeddings for all questions
            self.question_embeddings = self.model.encode(questions_text, convert_to_tensor=True)
            self.questions_list = questions_text
            
        except Exception as e:
            print(f"Error initializing embeddings: {e}")
            self.question_embeddings = None
            self.questions_list = []
    
    def answer_question(self, question: str) -> str:
        """
        Find the most similar FAQ question and return its answer using sentence embeddings.
        
        Args:
            question: User's question to find answer for
            
        Returns:
            Answer string for the most similar question
        """
        try:
            if not self.model or self.question_embeddings is None:
                # Fallback to simple text search
                return self._fallback_answer_question(question)
            
            # Generate embedding for the input question
            question_embedding = self.model.encode([question], convert_to_tensor=True)
            
            # Calculate cosine similarities
            similarities = torch.cosine_similarity(question_embedding, self.question_embeddings)
            
            # Find the most similar question
            most_similar_idx = torch.argmax(similarities).item()
            similarity_score = similarities[most_similar_idx].item()
            
            # Get the answer for the most similar question
            all_questions = self.get_all_questions()
            if 0 <= most_similar_idx < len(all_questions):
                answer = all_questions[most_similar_idx]['answer']
                
                # If similarity is too low, provide a generic response
                if similarity_score < 0.3:
                    return "I couldn't find a specific answer to your question. Please try rephrasing or check the FAQ section for similar topics."
                
                return answer
            else:
                return self._fallback_answer_question(question)
                
        except Exception as e:
            print(f"Error finding answer with embeddings: {e}")
            return self._fallback_answer_question(question)
    
    def _fallback_answer_question(self, question: str) -> str:
        """
        Fallback method using simple text search when embeddings are not available.
        
        Args:
            question: User's question
            
        Returns:
            Answer string
        """
        question_lower = question.lower()
        best_match = None
        best_score = 0
        
        for category in self.faq_data.get("categories", {}).values():
            for qa in category.get("questions", []):
                faq_question = qa["question"].lower()
                faq_answer = qa["answer"].lower()
                
                # Calculate simple similarity score
                score = 0
                
                # Check for exact word matches
                question_words = set(question_lower.split())
                faq_words = set(faq_question.split())
                common_words = question_words.intersection(faq_words)
                
                if common_words:
                    score += len(common_words) / max(len(question_words), len(faq_words))
                
                # Check if question contains FAQ keywords
                if any(word in question_lower for word in faq_question.split()):
                    score += 0.5
                
                # Check answer content
                if any(word in question_lower for word in faq_answer.split()):
                    score += 0.3
                
                if score > best_score:
                    best_score = score
                    best_match = qa["answer"]
        
        if best_match and best_score > 0.2:
            return best_match
        else:
            return "I couldn't find a specific answer to your question. Please try rephrasing or check the FAQ section for similar topics."
    
    def get_similar_questions(self, question: str, top_k: int = 3) -> List[Tuple[str, str, float]]:
        """
        Get top-k most similar questions with their answers and similarity scores.
        
        Args:
            question: Input question
            top_k: Number of similar questions to return
            
        Returns:
            List of tuples (question, answer, similarity_score)
        """
        try:
            if not self.model or self.question_embeddings is None:
                return []
            
            # Generate embedding for the input question
            question_embedding = self.model.encode([question], convert_to_tensor=True)
            
            # Calculate cosine similarities
            similarities = torch.cosine_similarity(question_embedding, self.question_embeddings)
            
            # Get top-k similar questions
            top_indices = torch.topk(similarities, min(top_k, len(similarities))).indices
            
            all_questions = self.get_all_questions()
            results = []
            
            for idx in top_indices:
                idx_item = idx.item()
                if 0 <= idx_item < len(all_questions):
                    qa = all_questions[idx_item]
                    similarity = similarities[idx_item].item()
                    results.append((qa['question'], qa['answer'], similarity))
            
            return results
            
        except Exception as e:
            print(f"Error getting similar questions: {e}")
            return [] 