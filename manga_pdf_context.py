
import os
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")
from openai import OpenAI

from PIL import Image
import matplotlib.pyplot as plt
import base64


import json
from pdf2image import convert_from_path
import io
from tqdm import tqdm
from typing import Dict, List, Set

class MangaAnalyzer:
    def __init__(self):
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI()
        self.characters = {}  # Store character information
        self.plot_points = []  # Store major plot points
        self.current_context = ""  # Maintain running context
        
    def encode_image_from_pil(self, pil_image):
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def analyze_page_with_context(self, page_image, page_num: int) -> dict:
        base64_image = self.encode_image_from_pil(page_image)
        
        # Create a context-aware prompt
        prompt = f"""This is page {page_num} of a manga. Based on the previous context:
{self.current_context}

Analyze this page and provide:
1. What's happening in this scene
2. Any characters present (new or existing)
3. Any important plot developments
4. Any character relationships or development
5. The emotional tone of the scene

Provide the analysis in a structured way."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    },
                ],
            )
            
            # Get the initial analysis
            initial_analysis = response.choices[0].message.content

            # Now ask for structured data about characters and plot
            structured_prompt = f"""Based on this analysis: {initial_analysis}

Please provide a structured response in the following format:
1. List any characters mentioned and their current state/actions
2. Any new character relationships or developments
3. Key plot points from this page
4. How this connects to the previous context

Format the response to be easily parsed as structured data."""

            structured_response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": structured_prompt,
                    },
                ],
            )

            # Update the running context with new information
            self.update_context(structured_response.choices[0].message.content)
            
            return {
                "page_number": page_num,
                "raw_analysis": initial_analysis,
                "structured_analysis": structured_response.choices[0].message.content,
                "characters_present": self.extract_characters(structured_response.choices[0].message.content),
                "plot_developments": self.extract_plot_points(structured_response.choices[0].message.content)
            }
            
        except Exception as e:
            print(f"Error processing page {page_num}: {str(e)}")
            return {
                "page_number": page_num,
                "error": str(e)
            }

    def update_context(self, new_analysis: str):
        # Keep a running summary of the last few important events
        # Limit context to prevent token overflow
        context_summary = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": f"Current context: {self.current_context}\n\nNew information: {new_analysis}\n\nProvide a brief (2-3 sentences) summary of the most important current context for the story, including key character states and ongoing plot points."
                }
            ]
        )
        
        self.current_context = context_summary.completion_message.content.text

    def extract_characters(self, analysis: str) -> List[Dict]:
        # Extract character information from the analysis
        character_prompt = f"Based on this analysis: {analysis}\n\nList all characters mentioned and their current state/actions in a structured format."
        
        character_response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": character_prompt
                }
            ]
        )
        
        # Update character dictionary with new information
        return character_response.choices[0].message.content

    def extract_plot_points(self, analysis: str) -> List[str]:
        # Extract key plot points from the analysis
        plot_prompt = f"Based on this analysis: {analysis}\n\nList the key plot developments in bullet points."
        
        plot_response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": plot_prompt
                }
            ]
        )
        
        return plot_response.choices[0].message.content

    def analyze_manga_pdf(self, pdf_path: str, output_json_path: str):
        print("Converting PDF to images...")
        pages = convert_from_path(pdf_path)
        
        manga_analysis = {
            "title": os.path.basename(pdf_path),
            "total_pages": len(pages),
            "pages": [],
            "characters": {},
            "plot_summary": [],
            "character_relationships": [],
            "story_arcs": []
        }
        
        print("Analyzing pages...")
        for page_num, page in enumerate(tqdm(pages), 1):
            page_analysis = self.analyze_page_with_context(page, page_num)
            manga_analysis["pages"].append(page_analysis)
            
            # Every 10 pages (or at the end), generate a summary
            if page_num % 10 == 0 or page_num == len(pages):
                summary_prompt = f"""Based on the current context:
{self.current_context}

Provide:
1. A summary of the current story arc
2. Updated character relationships
3. Major plot developments so far
4. Predictions or open plot threads"""

                summary = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": summary_prompt
                        }
                    ]
                )
                
                manga_analysis["story_arcs"].append({
                    "pages": f"{max(1, page_num-9)}-{page_num}",
                    "summary": summary.completion_message.content.text
                })
        
        # Generate final comprehensive analysis
        final_analysis = self.generate_final_analysis(manga_analysis)
        manga_analysis.update(final_analysis)
        
        print(f"Saving results to {output_json_path}")
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(manga_analysis, f, indent=2, ensure_ascii=False)
        
        print("Analysis complete!")

    def generate_final_analysis(self, manga_analysis: Dict) -> Dict:
        final_prompt = f"""Based on the complete story context:
{self.current_context}

Provide a comprehensive analysis including:
1. Main plot summary
2. Character development arcs
3. Major themes and motifs
4. Key relationships and their evolution
5. Significant plot twists or revelations"""

        final_response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": final_prompt
                }
            ]
        )
        
        return {
            "final_analysis": final_response.choices[0].message.content,
            "themes": self.extract_themes(final_response.choices[0].message.content),
            "character_arcs": self.extract_character_arcs(final_response.choices[0].message.content)
        }

    def extract_themes(self, analysis: str) -> List[str]:
        theme_prompt = f"Based on this analysis: {analysis}\n\nList the main themes and motifs of the story."
        
        theme_response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": theme_prompt
                }
            ]
        )
        
        return theme_response.choices[0].message.content

    def extract_character_arcs(self, analysis: str) -> Dict:
        arc_prompt = f"Based on this analysis: {analysis}\n\nDescribe the development arc for each main character."
        
        arc_response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": arc_prompt
                }
            ]
        )
        
        return arc_response.choices[0].message.content

if __name__ == "__main__":
    pdf_path = "avatar_test.pdf"
    output_json_path = "manga_analysis.json"
    
    analyzer = MangaAnalyzer()
    analyzer.analyze_manga_pdf(pdf_path, output_json_path)
