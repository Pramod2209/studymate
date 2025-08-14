import os
import json
import re
import requests
import time
from typing import List, Dict, Any, Optional
from requests.adapters import HTTPAdapter, Retry

class AIServices:
    def __init__(self):
        # Using IBM Granite 3.1 2B model via Hugging Face Inference API
        self.model_name = "ibm-granite/granite-3.1-2b-instruct"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        if not self.api_key:
            raise ValueError("Hugging Face API key not found. Please set HUGGINGFACE_API_KEY in your environment variables.")
            
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Configure retry strategy
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        
        print("Initialized AI Services with IBM Granite 3.1 2B model")
    
    def _make_api_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method to make API requests with error handling"""
        try:
            response = self.session.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" | Status: {e.response.status_code} | Response: {e.response.text}"
            raise Exception(error_msg)

    def _generate_response(self, prompt: str, content: str, max_length: int = 500) -> str:
        """Generate response using IBM Granite model via API or fallback to rule-based processing"""
        try:
            # Try Hugging Face API first
            payload = {
                "inputs": f"<|system|>\nYou are a helpful AI assistant specialized in analyzing academic documents.\n\n{prompt}\n<|assistant|>\n",
                "parameters": {
                    "max_new_tokens": max_length,
                    "temperature": 0.3,
                    "return_full_text": False
                }
            }
            
            response = self._make_api_request(payload)
            return response[0]['generated_text'].strip()
            
        except Exception as e:
            print(f"API error, using fallback: {e}")
            return self._fallback_processing(prompt, content)
            
    def _fallback_processing(self, prompt: str, content: str) -> str:
        """Enhanced fallback processing that actually analyzes content"""
        prompt_text = prompt.lower()
        
        if not content or not content.strip():
            return "I couldn't find any content to analyze. Please make sure the PDF was uploaded correctly."
        
        # Clean content for analysis
        clean_content = content.strip()[:5000]  # Limit to first 5000 chars for processing
        
        if "summarize" in prompt_text:
            # Fallback for summarization
            return self.summarize_content(clean_content, "Brief", "Simple")
        elif "translate to" in prompt_text:
            # Fallback for translation
            return f"I encountered an issue trying to translate. Please try again."
        elif "answer the question" in prompt_text:
            # Fallback for Q&A: try to find relevant snippets
            question_start = prompt_text.find("'") + 1
            question_end = prompt_text.find("'", question_start)
            question = prompt_text[question_start:question_end]
            return self._find_relevant_content(clean_content, question)
        else:
            # Default fallback: extract key topics
            return self.extract_key_topics(clean_content)

    def _find_relevant_content(self, content: str, question: str) -> str:
        """
        Find relevant content for the question using improved text matching
        """
        # Split into paragraphs first for better context
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Clean and tokenize question
        question_lower = question.lower()
        question_keywords = set(re.findall(r'\b\w{4,}\b', question_lower))  # Only words with 4+ chars
        
        # Remove common words that don't add meaning
        stopwords = {'what', 'when', 'where', 'why', 'how', 'the', 'and', 'your', 'this', 'that', 'with', 'from', 'they', 'have', 'been', 'were', 'will', 'would', 'could', 'should'}
        question_keywords = {w for w in question_keywords if w not in stopwords}
        
        if not question_keywords:
            return ""
            
        # Score each paragraph based on keyword matches
        scored_paragraphs = []
        for para in paragraphs:
            para_lower = para.lower()
            para_words = set(re.findall(r'\b\w+\b', para_lower))
            
            # Calculate overlap score
            overlap = len(question_keywords.intersection(para_words))
            if overlap > 0 and len(para) > 50:  # Only include meaningful paragraphs
                # Add some weight if the paragraph contains question words
                score = overlap + (0.5 if any(word in para_lower for word in ['because', 'therefore', 'thus', 'hence']) else 0)
                scored_paragraphs.append((para, score))
        
        # Sort by score and take top 2-3 most relevant paragraphs
        scored_paragraphs.sort(key=lambda x: x[1], reverse=True)
        relevant_paras = [p[0] for p in scored_paragraphs[:3] if p[1] > 0]
        
        if not relevant_paras:
            return ""
            
        # Format the response
        if len(relevant_paras) == 1:
            return f"Here's a relevant section that might help answer your question:\n\n{relevant_paras[0]}"
        else:
            return "Here are some relevant sections that might help answer your question:\n\n" + "\n\n".join(f"[{i+1}] {para}" for i, para in enumerate(relevant_paras))
    
    def _create_content_summary(self, content: str) -> str:
        """Create a meaningful summary from content"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if not sentences:
            return "The document appears to be empty or contains no readable text."
        
        # Take key sentences from beginning, middle, and end
        key_sentences = []
        if len(sentences) >= 1:
            key_sentences.append(sentences[0])  # First sentence
        if len(sentences) >= 3:
            key_sentences.append(sentences[len(sentences)//2])  # Middle sentence
        if len(sentences) >= 2:
            key_sentences.append(sentences[-1])  # Last sentence
        
        summary = '. '.join(key_sentences)
        return f"Based on the document content:\n\n{summary}."
    
    def _extract_content_topics(self, content: str) -> str:
        """Extract topics from content using keyword analysis"""
        # Simple keyword extraction
        words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]{4,}\b', content)
        word_freq = {}
        
        # Count word frequencies
        for word in words:
            word_lower = word.lower()
            if word_lower not in ['this', 'that', 'with', 'from', 'they', 'have', 'been', 'were', 'will', 'would', 'could', 'should']:
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        
        # Get top keywords
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        if not top_words:
            return "Could not identify specific topics from the content."
        
        topics = [word for word, freq in top_words if freq > 1]
        return f"Key topics identified in the document:\n\n• " + "\n• ".join(topics[:8])
    
    def _answer_from_content(self, content: str, prompt: str) -> str:
        """Answer questions based on content analysis"""
        # Extract the question from the prompt
        question_match = re.search(r'question[:\s]+(.*?)(?:\n|$)', prompt, re.IGNORECASE)
        question = question_match.group(1).strip() if question_match else ""
        
        if not question:
            return "I couldn't identify the specific question. Please rephrase your question."
        
        # Simple content matching
        question_words = set(re.findall(r'\b\w{3,}\b', question.lower()))
        content_lower = content.lower()
        
        # Find sentences that contain question keywords
        sentences = re.split(r'[.!?]+', content)
        relevant_sentences = []
        
        for sentence in sentences:
            sentence_words = set(re.findall(r'\b\w{3,}\b', sentence.lower()))
            overlap = len(question_words.intersection(sentence_words))
            if overlap > 0 and len(sentence.strip()) > 20:
                relevant_sentences.append((sentence.strip(), overlap))
        
        # Sort by relevance and take top sentences
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        
        if relevant_sentences:
            top_sentences = [s[0] for s in relevant_sentences[:3]]
            return f"Based on the document content, here's what I found:\n\n" + "\n\n".join(top_sentences)
        else:
            # If no direct matches, provide a general response based on content
            return f"I couldn't find specific information about '{question}' in the document. The document appears to discuss: {self._create_content_summary(content)}"
    
    def _generate_content_questions(self, content: str) -> str:
        """Generate questions from content"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
        
        if not sentences:
            return "Could not generate questions from the available content."
        
        questions = []
        for i, sentence in enumerate(sentences[:5]):
            questions.append(f"Q{i+1}: What does the document say about the topic mentioned in: '{sentence[:100]}...'?")
        
        return "Generated questions based on the content:\n\n" + "\n\n".join(questions)
    
    def summarize_content(self, content: str, length: str = "Medium", style: str = "Academic") -> str:
        """
        Generate summary of PDF content
        """
        length_instructions = {
            "Brief": "in 2-3 sentences",
            "Medium": "in 1-2 paragraphs", 
            "Detailed": "in 3-4 comprehensive paragraphs"
        }
        
        style_instructions = {
            "Academic": "using formal academic language",
            "Simple": "using simple, easy-to-understand language", 
            "Bullet Points": "as a structured list of key points"
        }
        
        prompt = f"""
        Summarize the following academic content {length_instructions[length]} {style_instructions[style]}.
        
        Focus on:
        - Main thesis or argument
        - Key findings or conclusions
        - Important concepts or methodologies
        - Practical applications or implications
        
        Content:
        {content[:6000]}
        """
        
        try:
            response = self._generate_response(prompt, content, max_length=800)
            
            # If using fallback, create a more detailed summary
            if "This appears to be a request for summarization" in response:
                return self._create_text_summary(content, length, style)
            
            return response
            
        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")
    
    def _create_text_summary(self, content: str, length: str, style: str) -> str:
        """Create a basic text summary using simple text processing"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Take first few sentences and last few based on length
        if length == "Brief":
            selected_sentences = sentences[:2] + sentences[-1:]
        elif length == "Medium":
            selected_sentences = sentences[:3] + sentences[-2:]
        else:  # Detailed
            selected_sentences = sentences[:5] + sentences[-3:]
        
        summary = '. '.join(selected_sentences[:8])  # Limit total sentences
        
        if style == "Bullet Points":
            points = summary.split('. ')
            return '\n'.join([f"• {point.strip()}." for point in points if point.strip()])
        
        return summary + "."
    
    def translate(self, content: str, target_language: str) -> str:
        """Translate content to the target language using a dedicated prompt."""
        if not content or not content.strip():
            return "Error: Cannot translate empty content."

        prompt = f"""Translate the following academic text into {target_language}. Provide ONLY the translated text, without any additional comments, headers, or explanations. The translation should be accurate, fluent, and maintain the original tone and style of the academic text.

    **Text to Translate:**
    {content}
    """

        try:
            translated_text = self._generate_response(prompt, content, max_length=4096)
            # Relax the validation to be more forgiving for concise languages
            if not translated_text or len(translated_text) < 10:
                return self._fallback_processing(f"translate to {target_language}", content)
            return translated_text
        except Exception as e:
            return self._fallback_processing(f"translate to {target_language}", content)

    def extract_key_points(self, content: str) -> str:
        """
        Extract key points from content
        """
        prompt = f"""
        Extract the most important key points from the following academic content.
        Present them as a numbered list, focusing on:
        - Main arguments or findings
        - Critical concepts
        - Important data or statistics
        - Conclusions or implications
        
        Content:
        {content[:8000]}
        """
        
        try:
            response = self._generate_response(prompt, content, max_length=600)
            
            # If using fallback, create basic key points
            if "This is a topic extraction request" in response:
                return self._extract_basic_key_points(content)
            
            return response
            
        except Exception as e:
            raise Exception(f"Failed to extract key points: {str(e)}")
    
    def _extract_basic_key_points(self, content: str) -> str:
        """Extract key points using basic text analysis"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
        
        # Take important sentences (beginning and scattered throughout)
        key_sentences = []
        total_sentences = len(sentences)
        
        if total_sentences > 0:
            key_sentences.append(sentences[0])  # First sentence
        if total_sentences > 2:
            key_sentences.append(sentences[total_sentences // 3])  # One third through
        if total_sentences > 4:
            key_sentences.append(sentences[2 * total_sentences // 3])  # Two thirds through
        if total_sentences > 1:
            key_sentences.append(sentences[-1])  # Last sentence
        
        # Format as numbered list
        key_points = []
        for i, sentence in enumerate(key_sentences, 1):
            key_points.append(f"{i}. {sentence}")
        
        return '\n'.join(key_points)
    
    def extract_topics(self, content: str, num_topics: int = 8, topic_type: str = "Main Themes") -> List[Dict[str, Any]]:
        """
        Extract topics from PDF content
        """
        type_instructions = {
            "Main Themes": "broad thematic areas and overarching concepts",
            "Key Concepts": "specific important concepts and definitions", 
            "Technical Terms": "technical terminology and specialized vocabulary",
            "Study Points": "important points for studying and exam preparation"
        }
        
        prompt = f"""
        Analyze the following academic content and identify {num_topics} {type_instructions[topic_type]}.
        
        For each topic, provide:
        1. A clear title (max 8 words)
        2. A detailed description (2-3 sentences)
        3. 3-4 key points related to this topic
        4. Relevance score (High/Medium/Low)
        
        Format each topic clearly with title, description, key points, and relevance.
        
        Content:
        {content[:6000]}
        """
        
        try:
            response = self._generate_response(prompt, content, max_length=1200)
            
            # If using fallback, create structured topics from content
            if "This is a topic extraction request" in response:
                return self._extract_topics_from_text(content, num_topics, topic_type)
            
            # Parse the response into structured format
            return self._parse_topics_response(response, num_topics)
                
        except Exception as e:
            # Fallback to simple text processing
            return self._extract_topics_from_text(content, num_topics, topic_type)
    
    def _extract_topics_from_text(self, content: str, num_topics: int, topic_type: str) -> List[Dict[str, Any]]:
        """Extract topics using basic text analysis"""
        # Split content into sentences and paragraphs
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
        
        topics = []
        sentences_per_topic = max(1, len(sentences) // num_topics)
        
        for i in range(min(num_topics, len(sentences) // sentences_per_topic)):
            start_idx = i * sentences_per_topic
            topic_sentences = sentences[start_idx:start_idx + sentences_per_topic]
            
            if topic_sentences:
                # Use first sentence as title (first few words)
                title_words = topic_sentences[0].split()[:6]
                title = ' '.join(title_words) + "..."
                
                # Create description from first sentence
                description = topic_sentences[0][:200] + "..." if len(topic_sentences[0]) > 200 else topic_sentences[0]
                
                # Create key points from other sentences
                key_points = []
                for sentence in topic_sentences[1:4]:
                    if sentence.strip():
                        point = sentence[:100] + "..." if len(sentence) > 100 else sentence
                        key_points.append(point)
                
                topics.append({
                    "title": title,
                    "description": description,
                    "key_points": key_points if key_points else [description],
                    "relevance": "Medium"
                })
        
        return topics[:num_topics]
    
    def _parse_topics_response(self, response: str, num_topics: int) -> List[Dict[str, Any]]:
        """Parse topics from AI response"""
        topics = []
        
        # Try to parse structured response
        sections = re.split(r'\d+\.|Topic \d+:', response)
        
        for i, section in enumerate(sections[1:num_topics+1]):
            if section.strip():
                lines = [line.strip() for line in section.strip().split('\n') if line.strip()]
                if lines:
                    title = lines[0][:50]
                    description = ' '.join(lines[1:3]) if len(lines) > 1 else lines[0]
                    key_points = lines[1:4] if len(lines) > 3 else lines[1:] if len(lines) > 1 else [description]
                    
                    topics.append({
                        "title": title,
                        "description": description,
                        "key_points": key_points,
                        "relevance": "Medium"
                    })
        
        return topics[:num_topics]
    
    def answer_question(self, content: str, question: str) -> str:
        """
        Answer questions about the PDF content with improved question handling
        """
        # Pre-process the question to understand its type
        question_lower = question.lower()
        
        # Create a more specific prompt based on question type
        if any(word in question_lower for word in ["what is", "what are", "define", "explain"]):
            instruction = "Provide a clear and concise explanation or definition based on the content."
        elif any(word in question_lower for word in ["how", "why"]):
            instruction = "Explain the process or reasoning in detail, providing context from the content."
        elif any(word in question_lower for word in ["problem statement", "research gap"]):
            instruction = "Identify and clearly state the main problem statement or research gap discussed in the content."
        else:
            instruction = "Provide a comprehensive answer based on the content."
        
        prompt = f"""
        You are an AI assistant analyzing academic content. Please answer the following question:
        
        Question: {question}
        
        {instruction}
        
        Guidelines:
        - Base your answer strictly on the provided content
        - If the answer isn't in the content, clearly state that
        - Include relevant details, examples, or quotes from the content
        - Be specific and avoid vague or generic responses
        - Maintain an academic tone
        
        Content:
        {content[:6000]}
        
        Answer the question directly and concisely:
        """
        
        try:
            response = self._generate_response(prompt, content, max_length=1000)
            
            # If we got a fallback response, try to find relevant content
            if "This is a question-answering request" in response:
                relevant_content = self._find_relevant_content(content, question)
                if relevant_content:
                    return relevant_content
                return "I couldn't find specific information about your question in the provided content. Please try rephrasing your question or check if the topic is covered in the document."
            
            # Clean up the response
            response = response.strip()
            if response.startswith('"') and response.endswith('"'):
                response = response[1:-1]
            
            return response
            
        except Exception as e:
            print(f"Error in answer_question: {str(e)}")
            return self._find_relevant_content(content, question) or "I encountered an error while processing your question. Please try again."
    
    def generate_test(self, content: str, question_count: int = 10, question_type: str = "Multiple Choice", difficulty: str = "Medium") -> List[Dict[str, Any]]:
        """
        Generate test questions based on PDF content
        """
        difficulty_instructions = {
            "Easy": "basic recall and understanding questions",
            "Medium": "application and analysis questions",
            "Hard": "synthesis and evaluation questions",
            "Mixed": "a mix of easy, medium, and hard questions"
        }
        
        type_instructions = {
            "Multiple Choice": "multiple choice questions with 4 options each",
            "Short Answer": "short answer questions requiring 2-3 sentence responses",
            "Essay": "essay questions requiring detailed analysis",
            "Mixed": "a mix of multiple choice, short answer, and essay questions"
        }
        
        prompt = f"""
        Generate {question_count} {type_instructions[question_type]} based on the following academic content.
        Make them {difficulty_instructions[difficulty]}.
        
        For multiple choice questions, provide:
        - Question text
        - 4 options (A, B, C, D)  
        - Correct answer
        - Brief explanation
        
        For other question types, provide:
        - Question text
        - Sample answer or key points
        - Explanation of what makes a good answer
        
        Content:
        {content[:5000]}
        """
        
        try:
            response = self._generate_response(prompt, content, max_length=1500)
            
            # If using fallback, generate basic questions
            if "This is a test generation request" in response:
                return self._generate_basic_questions(content, question_count, question_type, difficulty)
            
            # Parse response into structured questions
            return self._parse_questions_response(response, question_count, question_type)
                
        except Exception as e:
            # Fallback to basic question generation
            return self._generate_basic_questions(content, question_count, question_type, difficulty)
    
    def _generate_basic_questions(self, content: str, question_count: int, question_type: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate basic questions using text analysis"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
        
        questions = []
        sentences_per_question = max(1, len(sentences) // question_count)
        
        question_templates = [
            "What is {}?",
            "Explain {}.",
            "How does {} work?",
            "What are the key aspects of {}?",
            "Describe the importance of {}."
        ]
        
        for i in range(min(question_count, len(sentences))):
            sentence = sentences[i]
            
            # Extract key phrases (simple approach)
            words = sentence.split()
            if len(words) > 10:
                # Take middle portion as key concept
                key_concept = ' '.join(words[3:8])
                
                template = question_templates[i % len(question_templates)]
                question_text = template.format(key_concept)
                
                questions.append({
                    "question": question_text,
                    "type": question_type.lower().replace(" ", "_"),
                    "explanation": f"This question is based on: {sentence[:150]}...",
                    "sample_answer": sentence
                })
        
        return questions[:question_count]
    
    def _parse_questions_response(self, response: str, question_count: int, question_type: str) -> List[Dict[str, Any]]:
        """Parse questions from AI response"""
        questions = []
        
        # Split by question numbers or markers
        sections = re.split(r'\d+\.|Question \d+:', response)
        
        for i, section in enumerate(sections[1:question_count+1]):
            if section.strip():
                lines = [line.strip() for line in section.strip().split('\n') if line.strip()]
                if lines:
                    question_text = lines[0]
                    explanation = ' '.join(lines[1:3]) if len(lines) > 1 else "No explanation provided"
                    
                    questions.append({
                        "question": question_text,
                        "type": question_type.lower().replace(" ", "_"),
                        "explanation": explanation
                    })
        
        return questions[:question_count]
