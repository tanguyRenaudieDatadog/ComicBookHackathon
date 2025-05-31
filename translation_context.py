"""
Translation Context Manager

This module manages the accumulating context for comic book translations.
As each bubble is translated, its content is added to the context,
allowing subsequent translations to be more accurate and consistent.
"""

class TranslationContext:
    def __init__(self):
        """Initialize empty context"""
        self.context_window = []
        self.character_names = set()
        self.locations = set()
        self.story_summary = ""
        
    def add_bubble_to_context(self, bubble_id, original_text, translated_text=None):
        """Add a bubble's text to the context"""
        context_entry = {
            'bubble_id': bubble_id,
            'original': original_text,
            'translated': translated_text
        }
        self.context_window.append(context_entry)
        
        # Extract character names (simple heuristic: capitalized words)
        words = original_text.split()
        for word in words:
            # Check if it's a proper noun (capitalized, not at sentence start)
            if word.strip('.,!?"').isupper() or (len(word) > 1 and word[0].isupper() and word not in ['I', 'The', 'A', 'An']):
                potential_name = word.strip('.,!?"')
                if len(potential_name) > 2:  # Avoid short words
                    self.character_names.add(potential_name)
    
    def get_context_prompt(self, max_previous_bubbles=10):
        """Generate a context prompt for the translation model"""
        if not self.context_window:
            return ""
        
        # Get the last N bubbles for context
        recent_context = self.context_window[-max_previous_bubbles:]
        
        context_parts = []
        
        # Add character information if available
        if self.character_names:
            context_parts.append(f"Characters mentioned: {', '.join(sorted(self.character_names))}")
        
        # Add previous dialogue
        if recent_context:
            context_parts.append("\nPrevious dialogue in the comic:")
            for entry in recent_context:
                context_parts.append(f"Bubble {entry['bubble_id']}: {entry['original']}")
                if entry['translated']:
                    context_parts.append(f"(Translated: {entry['translated']})")
        
        return "\n".join(context_parts)
    
    def get_full_context(self):
        """Get the complete context for reference"""
        return {
            'total_bubbles': len(self.context_window),
            'characters': list(self.character_names),
            'dialogue_history': self.context_window,
            'summary': self.story_summary
        }
    
    def save_context(self, filepath):
        """Save context to a JSON file"""
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.get_full_context(), f, ensure_ascii=False, indent=2)
    
    def load_context(self, filepath):
        """Load context from a JSON file"""
        import json
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.context_window = data.get('dialogue_history', [])
            self.character_names = set(data.get('characters', []))
            self.story_summary = data.get('summary', '')
    
    def generate_summary(self):
        """Generate a brief summary of the story so far"""
        if len(self.context_window) < 3:
            return ""
        
        # Simple summary based on dialogue
        dialogues = [entry['original'] for entry in self.context_window]
        
        # This could be enhanced with AI summarization
        summary_parts = []
        if self.character_names:
            summary_parts.append(f"Characters: {', '.join(sorted(self.character_names))}")
        
        summary_parts.append(f"Total dialogue exchanges: {len(self.context_window)}")
        
        # Key dialogue points (first and last few)
        if len(dialogues) > 5:
            summary_parts.append("Key moments:")
            summary_parts.append(f"Opening: {dialogues[0][:100]}...")
            summary_parts.append(f"Recent: {dialogues[-1][:100]}...")
        
        self.story_summary = "\n".join(summary_parts)
        return self.story_summary 