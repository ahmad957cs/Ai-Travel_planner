import networkx as nx
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

class TravelerProfile:
    """
    Graph-based traveler profile system using NetworkX
    Nodes represent different aspects of a traveler's profile
    Edges represent relationships between different profile aspects
    """
    
    def __init__(self):
        self.graph = nx.Graph()
        self.profiles = {}  # Store multiple profiles by user_id
        
    def create_profile(self, user_id: str = None) -> str:
        """Create a new traveler profile"""
        if user_id is None:
            user_id = str(uuid.uuid4())
        
        # Initialize profile with basic nodes
        profile_data = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'nodes': {},
            'edges': []
        }
        
        self.profiles[user_id] = profile_data
        return user_id
    
    def add_node(self, user_id: str, node_type: str, node_data: Dict[str, Any]) -> str:
        """Add a node to the traveler profile"""
        if user_id not in self.profiles:
            self.create_profile(user_id)
        
        node_id = f"{user_id}_{node_type}_{uuid.uuid4().hex[:8]}"
        
        node_info = {
            'id': node_id,
            'type': node_type,
            'data': node_data,
            'created_at': datetime.now().isoformat()
        }
        
        self.profiles[user_id]['nodes'][node_id] = node_info
        self.profiles[user_id]['last_updated'] = datetime.now().isoformat()
        
        return node_id
    
    def add_edge(self, user_id: str, source_node: str, target_node: str, relationship: str = "related"):
        """Add an edge between two nodes"""
        if user_id not in self.profiles:
            return False
        
        edge_info = {
            'source': source_node,
            'target': target_node,
            'relationship': relationship,
            'created_at': datetime.now().isoformat()
        }
        
        self.profiles[user_id]['edges'].append(edge_info)
        self.profiles[user_id]['last_updated'] = datetime.now().isoformat()
        
        return True
    
    def update_budget_profile(self, user_id: str, budget_range: str, preferred_currency: str = "USD") -> str:
        """Add or update budget profile node"""
        budget_data = {
            'budget_range': budget_range,
            'currency': preferred_currency,
            'last_updated': datetime.now().isoformat()
        }
        
        # Find existing budget node or create new one
        existing_budget = None
        for node_id, node_info in self.profiles.get(user_id, {}).get('nodes', {}).items():
            if node_info['type'] == 'budget':
                existing_budget = node_id
                break
        
        if existing_budget:
            self.profiles[user_id]['nodes'][existing_budget]['data'].update(budget_data)
            return existing_budget
        else:
            return self.add_node(user_id, 'budget', budget_data)
    
    def update_interests_profile(self, user_id: str, interests: List[str]) -> str:
        """Add or update interests profile node"""
        interests_data = {
            'interests': interests,
            'count': len(interests),
            'last_updated': datetime.now().isoformat()
        }
        
        # Find existing interests node or create new one
        existing_interests = None
        for node_id, node_info in self.profiles.get(user_id, {}).get('nodes', {}).items():
            if node_info['type'] == 'interests':
                existing_interests = node_id
                break
        
        if existing_interests:
            self.profiles[user_id]['nodes'][existing_interests]['data'].update(interests_data)
            return existing_interests
        else:
            return self.add_node(user_id, 'interests', interests_data)
    
    def add_previous_trip(self, user_id: str, destination: str, trip_data: Dict[str, Any]) -> str:
        """Add a previous trip to the profile"""
        trip_data.update({
            'destination': destination,
            'trip_date': trip_data.get('trip_date', datetime.now().isoformat())
        })
        
        trip_node_id = self.add_node(user_id, 'previous_trip', trip_data)
        
        # Connect to interests if they exist
        interests_node = self.get_node_by_type(user_id, 'interests')
        if interests_node:
            self.add_edge(user_id, trip_node_id, interests_node, "influenced_by")
        
        return trip_node_id
    
    def update_visa_profile(self, user_id: str, nationality: str, visa_requirements: Dict[str, Any]) -> str:
        """Add or update visa profile node"""
        visa_data = {
            'nationality': nationality,
            'visa_requirements': visa_requirements,
            'last_updated': datetime.now().isoformat()
        }
        
        # Find existing visa node or create new one
        existing_visa = None
        for node_id, node_info in self.profiles.get(user_id, {}).get('nodes', {}).items():
            if node_info['type'] == 'visa':
                existing_visa = node_id
                break
        
        if existing_visa:
            self.profiles[user_id]['nodes'][existing_visa]['data'].update(visa_data)
            return existing_visa
        else:
            return self.add_node(user_id, 'visa', visa_data)
    
    def add_travel_preferences(self, user_id: str, preferences: Dict[str, Any]) -> str:
        """Add travel preferences node"""
        preferences_data = {
            'preferences': preferences,
            'last_updated': datetime.now().isoformat()
        }
        
        return self.add_node(user_id, 'travel_preferences', preferences_data)
    
    def get_node_by_type(self, user_id: str, node_type: str) -> Optional[str]:
        """Get the first node of a specific type"""
        for node_id, node_info in self.profiles.get(user_id, {}).get('nodes', {}).items():
            if node_info['type'] == node_type:
                return node_id
        return None
    
    def get_profile_summary(self, user_id: str) -> Dict[str, Any]:
        """Get a summary of the traveler profile"""
        if user_id not in self.profiles:
            return {}
        
        profile = self.profiles[user_id]
        summary = {
            'user_id': user_id,
            'created_at': profile['created_at'],
            'last_updated': profile['last_updated'],
            'node_count': len(profile['nodes']),
            'edge_count': len(profile['edges']),
            'node_types': {},
            'profile_data': {}
        }
        
        # Count node types and collect data
        for node_id, node_info in profile['nodes'].items():
            node_type = node_info['type']
            if node_type not in summary['node_types']:
                summary['node_types'][node_type] = 0
            summary['node_types'][node_type] += 1
            
            # Collect key data for summary
            if node_type == 'budget':
                summary['profile_data']['budget'] = node_info['data'].get('budget_range')
            elif node_type == 'interests':
                summary['profile_data']['interests'] = node_info['data'].get('interests', [])
            elif node_type == 'visa':
                summary['profile_data']['nationality'] = node_info['data'].get('nationality')
        
        return summary
    
    def get_recommendations(self, user_id: str, destination: str) -> Dict[str, Any]:
        """Generate personalized recommendations based on profile"""
        if user_id not in self.profiles:
            return {}
        
        profile = self.profiles[user_id]
        recommendations = {
            'budget_considerations': [],
            'interest_based_suggestions': [],
            'visa_requirements': [],
            'previous_trip_insights': []
        }
        
        # Analyze budget profile
        budget_node = self.get_node_by_type(user_id, 'budget')
        if budget_node:
            budget_data = profile['nodes'][budget_node]['data']
            recommendations['budget_considerations'].append(
                f"Based on your budget range: {budget_data.get('budget_range')}"
            )
        
        # Analyze interests
        interests_node = self.get_node_by_type(user_id, 'interests')
        if interests_node:
            interests = profile['nodes'][interests_node]['data'].get('interests', [])
            recommendations['interest_based_suggestions'] = [
                f"Focus on {interest.lower()} activities in {destination}" 
                for interest in interests[:3]  # Top 3 interests
            ]
        
        # Analyze visa requirements
        visa_node = self.get_node_by_type(user_id, 'visa')
        if visa_node:
            visa_data = profile['nodes'][visa_node]['data']
            recommendations['visa_requirements'].append(
                f"Check visa requirements for {visa_data.get('nationality')} citizens visiting {destination}"
            )
        
        # Analyze previous trips
        previous_trips = [
            node_info for node_info in profile['nodes'].values() 
            if node_info['type'] == 'previous_trip'
        ]
        if previous_trips:
            destinations = [trip['data'].get('destination', 'Unknown') for trip in previous_trips]
            recommendations['previous_trip_insights'] = [
                f"Based on your previous trips to: {', '.join(destinations)}"
            ]
        
        return recommendations
    
    def save_profile(self, user_id: str, filename: str = None) -> str:
        """Save profile to JSON file"""
        if user_id not in self.profiles:
            return ""
        
        if filename is None:
            filename = f"traveler_profile_{user_id}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.profiles[user_id], f, indent=2)
        
        return filename
    
    def load_profile(self, filename: str) -> bool:
        """Load profile from JSON file"""
        try:
            with open(filename, 'r') as f:
                profile_data = json.load(f)
            
            user_id = profile_data.get('user_id')
            if user_id:
                self.profiles[user_id] = profile_data
                return True
        except Exception as e:
            print(f"Error loading profile: {e}")
        
        return False

# Global instance for the application
traveler_profiles = TravelerProfile() 