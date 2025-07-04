import json
from typing import Dict, List, Any, Optional

class PromptEngine:
    """
    Enhanced prompt engineering for LLaMA model with few-shot examples
    and structured output formatting
    """
    
    def __init__(self):
        self.few_shot_examples = self._load_few_shot_examples()
        self.output_formats = self._load_output_formats()
    
    def _load_few_shot_examples(self) -> Dict[str, List[Dict[str, str]]]:
        """Load few-shot examples for different types of travel planning"""
        return {
            "itinerary": [
                {
                    "input": "Plan a 3-day trip to Tokyo under $1500 focused on Culture, Food",
                    "output": """{"itinerary": {"Day 1": ["Visit Senso-ji Temple in Asakusa", "Explore Tsukiji Outer Market for fresh sushi", "Evening at Tokyo Skytree for city views"], "Day 2": ["Morning at Meiji Shrine", "Shibuya Crossing and shopping district", "Traditional tea ceremony experience"], "Day 3": ["Visit Imperial Palace East Gardens", "Explore Akihabara electronics district", "Farewell dinner at local izakaya"]}}"""
                },
                {
                    "input": "Plan a 5-day trip to Paris under $2000 focused on Art, History",
                    "output": """{"itinerary": {"Day 1": ["Louvre Museum (morning)", "Walk along Champs-Élysées", "Arc de Triomphe visit"], "Day 2": ["Notre-Dame Cathedral", "Sainte-Chapelle", "Seine River cruise"], "Day 3": ["Musée d'Orsay", "Eiffel Tower (evening)", "Montmartre and Sacré-Cœur"], "Day 4": ["Palace of Versailles day trip", "Evening at Latin Quarter"], "Day 5": ["Pompidou Centre", "Shopping at Le Marais", "Farewell dinner at traditional bistro"]}}"""
                }
            ],
            "budget_analysis": [
                {
                    "input": "Analyze budget for 7-day trip to Bangkok with $1200 budget",
                    "output": """{"budget_breakdown": {"accommodation": {"estimated": 350, "range": "300-400"}, "food": {"estimated": 280, "range": "250-320"}, "transportation": {"estimated": 120, "range": "100-150"}, "activities": {"estimated": 200, "range": "180-250"}, "miscellaneous": {"estimated": 50, "range": "30-80"}}, "total_estimated": 1000, "budget_status": "comfortable", "savings_potential": 200}"""
                }
            ],
            "travel_tips": [
                {
                    "input": "Provide travel tips for first-time visitor to Istanbul",
                    "output": """{"tips": {"cultural": ["Dress modestly when visiting mosques", "Learn basic Turkish greetings"], "practical": ["Get Istanbulkart for public transport", "Bargain at Grand Bazaar"], "safety": ["Be aware of pickpockets in crowded areas", "Use official taxi stands"], "food": ["Try traditional Turkish breakfast", "Visit local tea houses"]}}"""
                }
            ]
        }
    
    def _load_output_formats(self) -> Dict[str, str]:
        """Load output format templates"""
        return {
            "itinerary": """Return ONLY valid JSON in this exact format (no explanations):
{"itinerary": {"Day 1": ["activity1", "activity2", "activity3"], "Day 2": ["activity1", "activity2", "activity3"]}}

Each day should have 2-4 activities that are realistic for the given budget and interests.""",
            
            "budget_analysis": """Return ONLY valid JSON in this exact format (no explanations):
{"budget_breakdown": {"accommodation": {"estimated": number, "range": "min-max"}, "food": {"estimated": number, "range": "min-max"}, "transportation": {"estimated": number, "range": "min-max"}, "activities": {"estimated": number, "range": "min-max"}, "miscellaneous": {"estimated": number, "range": "min-max"}}, "total_estimated": number, "budget_status": "comfortable/tight/luxury", "savings_potential": number}""",
            
            "travel_tips": """Return ONLY valid JSON in this exact format (no explanations):
{"tips": {"cultural": ["tip1", "tip2"], "practical": ["tip1", "tip2"], "safety": ["tip1", "tip2"], "food": ["tip1", "tip2"]}}"""
        }
    
    def build_itinerary_prompt(self, destination: str, days: int, budget: int, 
                              preferences: str, traveler_profile: Dict[str, Any] = None) -> str:
        """Build enhanced itinerary prompt with few-shot examples and profile context"""
        
        # Base prompt
        prompt = f"""You are an expert AI travel planner with deep knowledge of destinations worldwide.

{self.output_formats['itinerary']}

FEW-SHOT EXAMPLES:
"""
        
        # Add few-shot examples
        for example in self.few_shot_examples["itinerary"]:
            prompt += f"""
Input: {example['input']}
Output: {example['output']}
"""
        
        # Add current request
        prompt += f"""
Now plan a {days}-day trip to {destination} under ${budget} focused on {preferences}.
"""
        
        # Add traveler profile context if available
        if traveler_profile:
            profile_context = self._build_profile_context(traveler_profile)
            prompt += f"\nTRAVELER PROFILE CONTEXT:\n{profile_context}\n"
        
        # Add specific instructions
        prompt += f"""
IMPORTANT GUIDELINES:
- Activities should be realistic for the budget of ${budget}
- Focus on the specified interests: {preferences}
- Include a mix of free and paid activities
- Consider local culture and customs
- Activities should be achievable within each day
- Include meal suggestions where appropriate
- Consider transportation between activities

Return the itinerary in the exact JSON format specified above."""
        
        return prompt
    
    def build_budget_analysis_prompt(self, destination: str, days: int, budget: int,
                                   traveler_profile: Dict[str, Any] = None) -> str:
        """Build budget analysis prompt"""
        
        prompt = f"""You are an expert travel budget analyst.

{self.output_formats['budget_analysis']}

FEW-SHOT EXAMPLES:
"""
        
        for example in self.few_shot_examples["budget_analysis"]:
            prompt += f"""
Input: {example['input']}
Output: {example['output']}
"""
        
        prompt += f"""
Now analyze the budget for a {days}-day trip to {destination} with ${budget} total budget.
"""
        
        if traveler_profile:
            profile_context = self._build_profile_context(traveler_profile)
            prompt += f"\nTRAVELER PROFILE CONTEXT:\n{profile_context}\n"
        
        prompt += f"""
Consider:
- Local cost of living in {destination}
- Seasonal variations in prices
- Traveler's budget preferences
- Quality vs cost trade-offs
- Emergency fund recommendations

Return the budget analysis in the exact JSON format specified above."""
        
        return prompt
    
    def build_travel_tips_prompt(self, destination: str, traveler_profile: Dict[str, Any] = None) -> str:
        """Build travel tips prompt"""
        
        prompt = f"""You are an expert travel advisor with local knowledge of {destination}.

{self.output_formats['travel_tips']}

FEW-SHOT EXAMPLES:
"""
        
        for example in self.few_shot_examples["travel_tips"]:
            prompt += f"""
Input: {example['input']}
Output: {example['output']}
"""
        
        prompt += f"""
Now provide comprehensive travel tips for visiting {destination}.
"""
        
        if traveler_profile:
            profile_context = self._build_profile_context(traveler_profile)
            prompt += f"\nTRAVELER PROFILE CONTEXT:\n{profile_context}\n"
        
        prompt += f"""
Focus on:
- Cultural etiquette and customs
- Practical travel advice
- Safety considerations
- Local food and dining tips
- Transportation tips
- Money-saving advice

Return the travel tips in the exact JSON format specified above."""
        
        return prompt
    
    def _build_profile_context(self, profile: Dict[str, Any]) -> str:
        """Build context string from traveler profile"""
        context_parts = []
        
        if 'budget' in profile:
            context_parts.append(f"Budget preference: {profile['budget']}")
        
        if 'interests' in profile:
            interests = profile['interests']
            if isinstance(interests, list):
                context_parts.append(f"Interests: {', '.join(interests)}")
            else:
                context_parts.append(f"Interests: {interests}")
        
        if 'nationality' in profile:
            context_parts.append(f"Nationality: {profile['nationality']}")
        
        if 'previous_trips' in profile:
            trips = profile['previous_trips']
            if isinstance(trips, list) and trips:
                destinations = [trip.get('destination', 'Unknown') for trip in trips]
                context_parts.append(f"Previous destinations: {', '.join(destinations)}")
        
        return "; ".join(context_parts) if context_parts else "No specific profile data available"
    
    def build_comprehensive_prompt(self, destination: str, days: int, budget: int,
                                 preferences: str, traveler_profile: Dict[str, Any] = None) -> str:
        """Build a comprehensive prompt that includes itinerary, budget analysis, and tips"""
        
        prompt = f"""You are an expert AI travel planner. Create a comprehensive travel plan for {destination}.

Return ONLY valid JSON in this exact format (no explanations):
{{
    "itinerary": {{
        "Day 1": ["activity1", "activity2", "activity3"],
        "Day 2": ["activity1", "activity2", "activity3"]
    }},
    "budget_analysis": {{
        "accommodation": {{"estimated": number, "range": "min-max"}},
        "food": {{"estimated": number, "range": "min-max"}},
        "transportation": {{"estimated": number, "range": "min-max"}},
        "activities": {{"estimated": number, "range": "min-max"}},
        "miscellaneous": {{"estimated": number, "range": "min-max"}}
    }},
    "travel_tips": {{
        "cultural": ["tip1", "tip2"],
        "practical": ["tip1", "tip2"],
        "safety": ["tip1", "tip2"],
        "food": ["tip1", "tip2"]
    }},
    "personalized_recommendations": {{
        "based_on_interests": ["rec1", "rec2"],
        "budget_optimization": ["rec1", "rec2"],
        "hidden_gems": ["rec1", "rec2"]
    }}
}}

FEW-SHOT EXAMPLE:
Input: Plan a 3-day trip to Tokyo under $1500 focused on Culture, Food
Output: {{
    "itinerary": {{
        "Day 1": ["Visit Senso-ji Temple in Asakusa", "Explore Tsukiji Outer Market", "Evening at Tokyo Skytree"],
        "Day 2": ["Morning at Meiji Shrine", "Shibuya Crossing", "Traditional tea ceremony"],
        "Day 3": ["Imperial Palace East Gardens", "Akihabara electronics district", "Farewell dinner at izakaya"]
    }},
    "budget_analysis": {{
        "accommodation": {{"estimated": 300, "range": "250-350"}},
        "food": {{"estimated": 200, "range": "180-250"}},
        "transportation": {{"estimated": 80, "range": "60-100"}},
        "activities": {{"estimated": 150, "range": "120-180"}},
        "miscellaneous": {{"estimated": 50, "range": "30-70"}}
    }},
    "travel_tips": {{
        "cultural": ["Remove shoes when entering temples", "Learn basic Japanese greetings"],
        "practical": ["Get a Pasmo/Suica card", "Use Google Maps for navigation"],
        "safety": ["Tokyo is very safe", "Keep valuables secure"],
        "food": ["Try conveyor belt sushi", "Visit local ramen shops"]
    }},
    "personalized_recommendations": {{
        "based_on_interests": ["Visit traditional tea houses", "Try authentic sushi at Tsukiji"],
        "budget_optimization": ["Use convenience store meals", "Walk between nearby attractions"],
        "hidden_gems": ["Explore Yanaka Ginza", "Visit Kappabashi kitchen street"]
    }}
}}

Now create a comprehensive {days}-day travel plan for {destination} under ${budget} focused on {preferences}.
"""
        
        if traveler_profile:
            profile_context = self._build_profile_context(traveler_profile)
            prompt += f"\nTRAVELER PROFILE CONTEXT:\n{profile_context}\n"
        
        prompt += f"""
IMPORTANT GUIDELINES:
- Activities should be realistic for the budget of ${budget}
- Focus on the specified interests: {preferences}
- Include a mix of free and paid activities
- Consider local culture and customs
- Provide accurate budget estimates
- Include practical and cultural travel tips
- Offer personalized recommendations based on interests
- Consider seasonal factors and local events

Return the complete travel plan in the exact JSON format specified above."""
        
        return prompt

# Global instance for the application
prompt_engine = PromptEngine() 