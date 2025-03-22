import groq
import json
from typing import Tuple
from .utils import evaluate_answer_with_feedback
import random

class GroqAssessment:
    def __init__(self):
        self.client = groq.Client(api_key="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")

    def generate_question(self, topics=["science", "history", "general knowledge"]) -> Tuple[str, str]:
        prompt = (
            "Generate an easy programming-related academic question and its detailed answer. "
            "Ensure the response is a valid JSON object with exactly two keys: 'question' and 'answer'. "
            "Example format:\n\n"
            '{\n  "question": "What is a variable in Python?",\n  "answer": "A variable in Python is a named storage for data." \n}'
        )

        try:
            completion = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": "You are an educational assessment expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            raw_response = completion.choices[0].message.content.strip()  
            print(f"Raw response: {raw_response}")  # Debugging

            # Fix: Ensure JSON formatting is clean before parsing
            cleaned_response = raw_response.replace("\n", " ").replace("\r", "")

            response = json.loads(cleaned_response)
            return response["question"], response["answer"]

        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {str(e)}\nResponse received: {raw_response}")
            return (
                "What is a variable in Python?", 
                "A variable in Python is a named storage for data."
            )
        except Exception as e:
            print(f"Error generating question: {str(e)}")
            return (
                "What is a variable in Python?", 
                "A variable in Python is a named storage for data."
            )

    def evaluate_answer(self, model_answer: str, student_answer: str) -> Tuple[float, str]:
        print("---------", student_answer)
        
        # Check if student_answer is blank
        if not student_answer.strip():
            # Default score and feedback for blank answer
            return 0.0, "No answer provided. Please ensure your answer is complete."
        
        prompt = (
            "Evaluate the student's answer compared to the model answer. "
            "Provide JSON output with:\n"
            '- "score":0-100,\n'
            '- "detailed_feedback" (string),\n'
            '- "missed_concepts" (list of strings).\n\n'
            "Example:\n"
            '{\n  "score": 80,\n  "detailed_feedback": "Good answer, but missing details on scope.",\n  "missed_concepts": ["variable scope"] \n}'
            f"\n\nModel Answer: {model_answer}\nStudent Answer: {student_answer}"
        )
        print("prompt", prompt)
        
        try:
            completion = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": "You are an expert educational assessor."},
                    {"role": "user", "content": prompt}
                ], 
                temperature=0.3
            )

            raw_response = completion.choices[0].message.content.strip()
            print(f"Raw evaluation response: {raw_response}")  # Debugging

            cleaned_response = raw_response.replace("\n", " ").replace("\r", "")

            evaluation = json.loads(cleaned_response)
            print('eee', evaluation)
            
            # Handle missing or malformed responses gracefully
            if "score" not in evaluation:
                print("Score missing in evaluation response.")
                return 0.0, "Evaluation failed. Please try again."
            
            feedback = f"\nFeedback:\n{evaluation['detailed_feedback']}"

            if evaluation.get("missed_concepts"):
                feedback += "\n\nKey concepts to include:\n"
                feedback += ", ".join(evaluation["missed_concepts"])

            return float(evaluation["score"]), feedback

        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {str(e)}\nResponse received: {raw_response}")
            # Return default score and feedback in case of JSON decode error
            return 0.0, "An error occurred during evaluation. Please try again."
        
        except Exception as e:
            print(f"Error in Groq evaluation: {str(e)}")
            # Return default score and feedback for other errors
            return 0.0, "An error occurred during evaluation. Please try again."
