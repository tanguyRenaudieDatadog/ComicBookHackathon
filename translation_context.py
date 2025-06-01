"""
Multimodal Translation Context Manager

This module uses Llama4's vision capabilities to understand both visual and textual context
for more accurate and contextually aware comic book translations.
"""

import json
import base64
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from llama_api_client import LlamaAPIClient

@dataclass
class CharacterInfo:
    """Information about a character detected in the comic"""
    name: str
    visual_description: str
    speech_patterns: List[str]
    relationships: Dict[str, str]
    emotions_shown: List[str]
    first_appearance_page: int

@dataclass
class PageContext:
    """Enhanced context for each page"""
    page_number: int
    location: str
    mood: str
    visual_elements: List[str]
    time_context: str
    characters_present: List[str]
    scene_description: str
    genre: str
    panel_layout: str
    key_events: List[str]

@dataclass
class BubbleContext:
    """Simplified context for each speech bubble"""
    bubble_id: int
    original_text: str
    translated_text: Optional[str]
    speaker: Optional[str]
    emotion: str
    page_number: int = 1

class MultimodalTranslationContext:
    """
    Advanced context manager using Llama4's multimodal capabilities
    to understand visual and textual context per page in comic books
    """
    
    def __init__(self, client: LlamaAPIClient):
        self.client = client
        self.characters: Dict[str, CharacterInfo] = {}
        self.page_contexts: List[PageContext] = []
        self.bubble_contexts: List[BubbleContext] = []
        self.story_arc: str = ""
        self.genre: str = ""
        self.current_page = 1
        self.current_page_context: Optional[PageContext] = None
        
    def analyze_page_context(self, image_path: str, page_number: int = None) -> PageContext:
        """
        Analyze the entire page to understand visual context, characters, and setting
        """
        if page_number:
            self.current_page = page_number
            
        base64_image = self._encode_image(image_path)
        
        prompt = """Analyze this comic book page comprehensively and provide analysis in JSON format:

{
    "overall_scene": {
        "location": "detailed description of where this takes place",
        "mood": "overall emotional tone/atmosphere (tense, cheerful, mysterious, etc.)",
        "time_context": "time of day, historical period, season, etc.",
        "scene_description": "what's happening in this scene overall"
    },
    "characters_analysis": [
        {
            "name": "character name if identifiable, or description like 'blonde woman', 'tall man'",
            "visual_description": "detailed physical appearance, clothing, distinctive features",
            "position": "where they are positioned in the scene",
            "emotion": "their apparent emotional state",
            "actions": "what they appear to be doing"
        }
    ],
    "story_elements": {
        "genre": "apparent genre (action, romance, comedy, drama, sci-fi, fantasy, etc.)",
        "tension_level": "low/medium/high",
        "key_visual_elements": ["important objects, symbols, background details"],
        "key_events": ["major actions or events happening on this page"]
    },
    "panel_structure": {
        "layout": "description of how panels are arranged",
        "reading_flow": "natural reading order and flow",
        "speech_bubble_count": "approximate number of speech bubbles visible"
    },
    "dialogue_context": {
        "conversation_type": "casual chat, argument, exposition, action dialogue, etc.",
        "relationships_shown": "apparent relationships between characters",
        "formality_level": "casual, formal, technical, emotional, etc."
    }
}

Analyze the image carefully and provide detailed, useful information for translation context. Focus on understanding who is speaking to whom and the overall situation."""

        try:
            response = self.client.chat.completions.create(
                model="Llama-4-Maverick-17B-128E-Instruct-FP8",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ]
            )
            
            analysis_text = response.completion_message.content.text.strip()
            
            # Try to parse as JSON, fallback to text analysis if needed
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response from text
                analysis = self._parse_text_analysis(analysis_text)
            
            # Create PageContext from analysis
            page_context = self._create_page_context_from_analysis(analysis, page_number or self.current_page)
            
            # Update our context with this analysis
            self._update_context_from_page_analysis(analysis, page_context)
            
            # Store current page context
            self.current_page_context = page_context
            self.page_contexts.append(page_context)
            
            return page_context
            
        except Exception as e:
            print(f"Error analyzing page context: {e}")
            # Return default page context
            default_context = PageContext(
                page_number=page_number or self.current_page,
                location="unknown",
                mood="neutral",
                visual_elements=[],
                time_context="unknown",
                characters_present=[],
                scene_description="",
                genre="unknown",
                panel_layout="standard",
                key_events=[]
            )
            self.current_page_context = default_context
            self.page_contexts.append(default_context)
            return default_context
    
    def identify_speaker_for_bubble(self, bubble_info: Dict, original_text: str = "") -> Tuple[str, str]:
        """
        Identify the most likely speaker for a bubble based on page context
        """
        if not self.current_page_context:
            return "unknown", "neutral"
        
        # Simple heuristic based on bubble position and page context
        bubble_x = bubble_info.get('center_x', 0)
        bubble_y = bubble_info.get('center_y', 0)
        
        # If we have character positions from page analysis, try to match
        if len(self.current_page_context.characters_present) == 1:
            return self.current_page_context.characters_present[0], "neutral"
        elif len(self.current_page_context.characters_present) == 2:
            # Simple left/right heuristic for two characters
            if bubble_x < 0.5:  # Assuming normalized coordinates, adjust as needed
                return self.current_page_context.characters_present[0], "neutral"
            else:
                return self.current_page_context.characters_present[1], "neutral"
        
        # Fallback to first character if multiple
        if self.current_page_context.characters_present:
            return self.current_page_context.characters_present[0], "neutral"
        
        return "unknown", "neutral"
    
    def add_bubble_to_context(self, bubble_id: int, original_text: str, translated_text: str = None, 
                            bubble_info: Dict = None):
        """
        Add a bubble with its context to our knowledge base
        """
        # Identify speaker based on page context
        speaker, emotion = self.identify_speaker_for_bubble(bubble_info or {}, original_text)
        
        bubble_context = BubbleContext(
            bubble_id=bubble_id,
            original_text=original_text,
            translated_text=translated_text,
            speaker=speaker,
            emotion=emotion,
            page_number=self.current_page
        )
        
        self.bubble_contexts.append(bubble_context)
        
        # Update character information if we have a speaker
        if speaker and speaker != "unknown":
            self._update_character_info(bubble_context)
    
    def get_enhanced_translation_prompt(self, text_to_translate: str, bubble_info: Dict = None,
                                      max_context_bubbles: int = 8, source_lang: str = "English", 
                                      target_lang: str = "Russian") -> str:
        """
        Generate a comprehensive, context-aware prompt for translation using page-level context
        """
        prompt_parts = []
        
        # Story and genre context
        if self.genre:
            prompt_parts.append(f"Comic Genre: {self.genre}")
        
        # Current page context
        if self.current_page_context:
            prompt_parts.append(f"\nCurrent Page Context:")
            prompt_parts.append(f"- Location: {self.current_page_context.location}")
            prompt_parts.append(f"- Scene: {self.current_page_context.scene_description}")
            prompt_parts.append(f"- Mood/Atmosphere: {self.current_page_context.mood}")
            prompt_parts.append(f"- Time context: {self.current_page_context.time_context}")
            
            if self.current_page_context.characters_present:
                prompt_parts.append(f"- Characters present: {', '.join(self.current_page_context.characters_present)}")
            
            if self.current_page_context.key_events:
                prompt_parts.append(f"- Key events: {', '.join(self.current_page_context.key_events)}")
        
        # Character context
        if self.characters:
            prompt_parts.append(f"\nKnown Characters:")
            for name, char_info in self.characters.items():
                prompt_parts.append(f"- {name}: {char_info.visual_description}")
                if char_info.speech_patterns:
                    prompt_parts.append(f"  Speech style: {', '.join(char_info.speech_patterns[:3])}")
        
        # Recent dialogue history
        recent_bubbles = self.bubble_contexts[-max_context_bubbles:]
        if recent_bubbles:
            prompt_parts.append(f"\nRecent dialogue context:")
            for bubble in recent_bubbles:
                if bubble.original_text:
                    speaker_info = f" ({bubble.speaker})" if bubble.speaker and bubble.speaker != "unknown" else ""
                    prompt_parts.append(f"- {bubble.original_text}{speaker_info}")
                    if bubble.translated_text:
                        prompt_parts.append(f"  → {bubble.translated_text}")
        
        # Identify likely speaker for current bubble
        speaker, emotion = self.identify_speaker_for_bubble(bubble_info or {}, text_to_translate)
        
        # Translation instruction
        prompt_parts.append(f"\n{'='*50}")
        prompt_parts.append(f"Now translate this {source_lang} text to {target_lang}:")
        prompt_parts.append(f"Text: \"{text_to_translate}\"")
        
        if speaker != "unknown":
            prompt_parts.append(f"\nLikely speaker: {speaker}")
        
        prompt_parts.append(f"\nConsider:")
        prompt_parts.append(f"- The current scene and mood: {self.current_page_context.mood if self.current_page_context else 'unknown'}")
        prompt_parts.append(f"- The context and situation")
        prompt_parts.append(f"- Consistency with previous character dialogue")
        prompt_parts.append(f"- Comic book dialogue style appropriate for {target_lang}")
        prompt_parts.append(f"\nReturn ONLY the translated text, no explanations.")
        
        return "\n".join(prompt_parts)
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as img:
            return base64.b64encode(img.read()).decode('utf-8')
    
    def _create_page_context_from_analysis(self, analysis: Dict, page_number: int) -> PageContext:
        """Create PageContext object from analysis data"""
        overall_scene = analysis.get("overall_scene", {})
        story_elements = analysis.get("story_elements", {})
        panel_structure = analysis.get("panel_structure", {})
        characters = analysis.get("characters_analysis", [])
        
        return PageContext(
            page_number=page_number,
            location=overall_scene.get("location", ""),
            mood=overall_scene.get("mood", ""),
            visual_elements=story_elements.get("key_visual_elements", []),
            time_context=overall_scene.get("time_context", ""),
            characters_present=[char.get("name", f"character_{i}") for i, char in enumerate(characters)],
            scene_description=overall_scene.get("scene_description", ""),
            genre=story_elements.get("genre", ""),
            panel_layout=panel_structure.get("layout", ""),
            key_events=story_elements.get("key_events", [])
        )
    
    def _update_context_from_page_analysis(self, analysis: Dict, page_context: PageContext):
        """Update our context based on page analysis"""
        # Update genre information
        if page_context.genre and not self.genre:
            self.genre = page_context.genre
        
        # Update character information
        characters = analysis.get("characters_analysis", [])
        for char_data in characters:
            char_name = char_data.get("name", "")
            if char_name and char_name not in self.characters:
                self.characters[char_name] = CharacterInfo(
                    name=char_name,
                    visual_description=char_data.get("visual_description", ""),
                    speech_patterns=[],
                    relationships={},
                    emotions_shown=[char_data.get("emotion", "")],
                    first_appearance_page=self.current_page
                )
    
    def _update_character_info(self, bubble_context: BubbleContext):
        """Update character information based on new dialogue"""
        speaker = bubble_context.speaker
        if speaker not in self.characters:
            self.characters[speaker] = CharacterInfo(
                name=speaker,
                visual_description="",
                speech_patterns=[],
                relationships={},
                emotions_shown=[],
                first_appearance_page=bubble_context.page_number
            )
        
        # Add speech pattern analysis
        char_info = self.characters[speaker]
        if bubble_context.original_text:
            # Simple speech pattern analysis
            text = bubble_context.original_text
            if "!" in text:
                char_info.speech_patterns.append("exclamatory")
            if "?" in text:
                char_info.speech_patterns.append("questioning")
            if len(text.split()) > 20:
                char_info.speech_patterns.append("verbose")
            if text.isupper():
                char_info.speech_patterns.append("shouting")
        
        # Add emotion
        if bubble_context.emotion:
            char_info.emotions_shown.append(bubble_context.emotion)
    
    def _parse_text_analysis(self, text: str) -> Dict:
        """Fallback parser for when JSON parsing fails"""
        return {
            "overall_scene": {"location": "unknown", "mood": "neutral", "scene_description": ""},
            "characters_analysis": [],
            "story_elements": {"genre": "unknown", "key_events": []},
            "panel_structure": {"layout": "standard"}
        }
    
    def save_context(self, filepath: str):
        """Save the rich context to JSON"""
        context_data = {
            "characters": {name: asdict(char) for name, char in self.characters.items()},
            "page_contexts": [asdict(page) for page in self.page_contexts],
            "bubble_contexts": [asdict(bubble) for bubble in self.bubble_contexts],
            "story_arc": self.story_arc,
            "genre": self.genre,
            "current_page": self.current_page
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(context_data, f, ensure_ascii=False, indent=2)
    
    def load_context(self, filepath: str):
        """Load context from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Reconstruct characters
        self.characters = {}
        for name, char_data in data.get("characters", {}).items():
            self.characters[name] = CharacterInfo(**char_data)
        
        # Reconstruct page contexts
        self.page_contexts = [PageContext(**page_data) for page_data in data.get("page_contexts", [])]
        
        # Reconstruct bubble contexts
        self.bubble_contexts = [BubbleContext(**bubble_data) for bubble_data in data.get("bubble_contexts", [])]
        
        self.story_arc = data.get("story_arc", "")
        self.genre = data.get("genre", "")
        self.current_page = data.get("current_page", 1)
        
        # Set current page context to the latest one
        if self.page_contexts:
            self.current_page_context = self.page_contexts[-1]