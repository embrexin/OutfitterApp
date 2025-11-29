import random
from typing import List, Dict, Tuple

class OutfitSuggester:
    """
    Generates outfit suggestions based on weather and clothing inventory
    """

    def __init__(self, clothing_data: List[Dict], temperature: float, weather: str):
        """
        Initialize suggester

        Args:
            clothing_data: List of clothing items from clothing.json
            temperature: Temperature in Fahrenheit
            weather: Weather condition (e.g., "Sunny ☀️", "Rainy 🌧️")
        """
        self.clothing = clothing_data
        self.temperature = temperature
        self.weather = weather.lower()

        # Temperature-based clothing rules
        self.temp_rules = {
            'very_cold': {'max': 32, 'required': ['outerwear', 'long sleeve'], 'avoid': ['summer']},
            'cold': {'min': 33, 'max': 50, 'required': ['outerwear'], 'avoid': ['summer']},
            'cool': {'min': 51, 'max': 65, 'required': [], 'avoid': []},
            'mild': {'min': 66, 'max': 75, 'required': [], 'avoid': []},
            'warm': {'min': 76, 'max': 85, 'required': [], 'avoid': ['outerwear', 'long sleeve']},
            'hot': {'min': 86, 'required': [], 'avoid': ['outerwear', 'long sleeve', 'pants']}
        }

    def get_temp_category(self) -> str:
        """Determine which temperature category we're in"""
        for category, bounds in self.temp_rules.items():
            min_temp = bounds.get('min', float('-inf'))
            max_temp = bounds.get('max', float('inf'))
            if min_temp <= self.temperature <= max_temp:
                return category
        return 'mild'

    def score_item(self, item: Dict, temp_category: str) -> float:
        """
        Score how suitable an item is for current conditions

        Returns:
            float: Score (higher is better, negative means unsuitable)
        """
        score = 0.0
        tags = item.get('tags', [])
        label = item.get('label', '').lower()

        # Handle label variations
        if 't-shirt' in label:
            label = 't-shirt'

        # Base score
        score += 1.0

        # Penalize recently worn items heavily
        if 'recently worn' in tags:
            score -= 10.0

        # Bonus for saved items (user favorites)
        if 'saved' in tags:
            score += 3.0

        # Temperature appropriateness based on label
        rules = self.temp_rules[temp_category]

        # Temperature-specific label scoring (most important)
        if temp_category in ['very_cold', 'cold']:  # 32-50°F
            if label in ['jacket', 'coat', 'hoodie', 'sweater']:
                score += 3.0
            elif label in ['shirt', 'blouse']:
                score += 1.0
            elif label in ['pants', 'jeans', 'sweatpants']:
                score += 2.0
            elif label in ['shorts', 'skirt', 'dress', 't-shirt']:
                score -= 2.0

        elif temp_category == 'cool':  # 51-65°F
            if label in ['jacket', 'sweater', 'cardigan', 'hoodie']:
                score += 2.0
            elif label in ['shirt', 't-shirt', 'blouse']:
                score += 1.5
            elif label in ['pants', 'jeans']:
                score += 1.5

        elif temp_category == 'mild':  # 66-75°F
            if label in ['t-shirt', 'shirt', 'blouse']:
                score += 2.0
            elif label in ['pants', 'jeans', 'skirt']:
                score += 1.5
            elif label in ['dress']:
                score += 2.0
            elif label in ['jacket', 'coat']:
                score -= 1.0

        elif temp_category in ['warm', 'hot']:  # 76°F+
            if label in ['t-shirt', 'tank top']:
                score += 2.0
            elif label in ['shorts', 'skirt', 'dress']:
                score += 2.0
            elif label in ['jacket', 'coat', 'sweater', 'hoodie']:
                score -= 3.0

        # Check tags for additional scoring
        for required_tag in rules.get('required', []):
            if required_tag in tags:
                score += 2.0

        for avoid_tag in rules.get('avoid', []):
            if avoid_tag in tags:
                score -= 2.0

        # Weather-specific scoring
        if 'rainy' in self.weather or 'snowy' in self.weather:
            if 'outerwear' in tags or label in ['jacket', 'coat', 'hoodie']:
                score += 2.0
            if label in ['dress', 'skirt'] and 'snowy' in self.weather:
                score -= 2.0

        return score

    def categorize_items(self) -> Dict[str, List[Dict]]:
        """Categorize clothing items by type"""
        categories = {
            'tops': [],
            'bottoms': [],
            'outerwear': [],
            'complete': []  # dresses, suits
        }

        for item in self.clothing:
            label = item.get('label', '').lower()

            # Handle variations in naming
            if 't-shirt' in label:
                label = 't-shirt'

            if label in ['dress', 'suit']:
                categories['complete'].append(item)
            elif label in ['jacket', 'coat', 'hoodie', 'sweater', 'cardigan', 'blazer']:
                categories['outerwear'].append(item)
            elif label in ['t-shirt', 'shirt', 'blouse', 'tank top', 'tshirt']:
                categories['tops'].append(item)
            elif label in ['pants', 'jeans', 'shorts', 'skirt', 'sweatpants']:
                categories['bottoms'].append(item)

        return categories

    def suggest_outfit(self) -> Tuple[List[Dict], List[str]]:
        """
        Generate the best outfit suggestion

        Returns:
            Tuple of (outfit_items, reasoning)
        """
        temp_category = self.get_temp_category()
        categories = self.categorize_items()
        outfit = []
        reasoning = []

        # Add temperature reasoning
        if temp_category == 'very_cold':
            reasoning.append(f"It's freezing at {int(self.temperature)}°F - Bundle up!")
        elif temp_category == 'cold':
            reasoning.append(f"Cold at {int(self.temperature)}°F - Stay warm with layers")
        elif temp_category == 'cool':
            reasoning.append(f"Cool at {int(self.temperature)}°F - Light layers recommended")
        elif temp_category == 'warm':
            reasoning.append(f"Warm at {int(self.temperature)}°F - Keep it light")
        elif temp_category == 'hot':
            reasoning.append(f"Hot at {int(self.temperature)}°F - Stay cool!")

        # Add weather reasoning
        if 'rainy' in self.weather:
            reasoning.append("Don't forget a jacket for the rain")
        elif 'snowy' in self.weather:
            reasoning.append("Bundle up for the snow")
        elif 'sunny' in self.weather:
            reasoning.append("Perfect sunny weather")

        # Try complete outfit first (dress/suit) for mild+ weather
        if temp_category in ['mild', 'warm', 'hot'] and categories['complete']:
            scored_complete = [(item, self.score_item(item, temp_category))
                             for item in categories['complete']]
            scored_complete.sort(key=lambda x: x[1], reverse=True)

            if scored_complete and scored_complete[0][1] > 0:  # If score is positive
                outfit.append(scored_complete[0][0])

                # Add light outerwear for cool weather
                if temp_category == 'mild' and categories['outerwear']:
                    scored_outer = [(item, self.score_item(item, temp_category))
                                  for item in categories['outerwear']
                                  if item.get('label', '').lower() in ['cardigan', 'blazer', 'jacket']]
                    if scored_outer:
                        scored_outer.sort(key=lambda x: x[1], reverse=True)
                        if scored_outer and scored_outer[0][1] > 0:
                            outfit.append(scored_outer[0][0])

                return outfit, reasoning

        # Build layered outfit
        # 1. Select top
        if categories['tops']:
            scored_tops = [(item, self.score_item(item, temp_category))
                          for item in categories['tops']]
            scored_tops.sort(key=lambda x: x[1], reverse=True)
            if scored_tops and scored_tops[0][1] > 0:
                outfit.append(scored_tops[0][0])

        # 2. Select bottom
        if categories['bottoms']:
            scored_bottoms = [(item, self.score_item(item, temp_category))
                            for item in categories['bottoms']]
            scored_bottoms.sort(key=lambda x: x[1], reverse=True)
            if scored_bottoms and scored_bottoms[0][1] > 0:
                outfit.append(scored_bottoms[0][0])

        # 3. Add outerwear if needed (cold weather or rainy)
        if (temp_category in ['very_cold', 'cold', 'cool'] or
            'rainy' in self.weather or 'snowy' in self.weather):
            if categories['outerwear']:
                scored_outer = [(item, self.score_item(item, temp_category))
                              for item in categories['outerwear']]
                scored_outer.sort(key=lambda x: x[1], reverse=True)
                if scored_outer and scored_outer[0][1] > 0:
                    outfit.append(scored_outer[0][0])

        # If no outfit could be generated, create a default one
        if not outfit:
            reasoning.append("Could not find a perfect match, but here's a suggestion.")
            if categories['tops']:
                outfit.append(random.choice(categories['tops']))
            if categories['bottoms']:
                outfit.append(random.choice(categories['bottoms']))

        # Add user preference note if applicable
        saved_items = [item for item in outfit if 'saved' in item.get('tags', [])]
        if saved_items:
            reasoning.append("Including your favorite items")

        return outfit, reasoning


def suggest_outfit_for_api(clothing_data: List[Dict], weather_data: Tuple[float, str]) -> Dict:
    """
    Main function to call from Flask API

    Args:
        clothing_data: List from clothing.json
        weather_data: Tuple of (temperature, weather_condition)

    Returns:
        Dict with outfit items and reasoning
    """
    if weather_data is None:
        # Default to a mild temperature if weather is unavailable
        temperature, weather = 65, "Unknown 🌍"
    else:
        temperature, weather = weather_data

    suggester = OutfitSuggester(clothing_data, temperature, weather)
    outfit, reasoning = suggester.suggest_outfit()

    return {
        'items': [
            {
                'id': item['id'],
                'label': item['label'],
                'src': item['src'],
                'image': item.get('image'),
                'alt': item.get('alt', item['label'].lower())
            }
            for item in outfit
        ],
        'reasoning': ', '.join(reasoning),
        'temperature': int(temperature),
        'weather': weather
    }
