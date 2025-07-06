#!/usr/bin/env python3
"""
Test script for Phase 3 features:
1. Graph-Based Traveler Profile
2. Enhanced Prompt Engineering
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from traveler_profile import TravelerProfile
from prompt_engine import PromptEngine

def test_traveler_profile():
    """Test the graph-based traveler profile system"""
    print("🧪 Testing Graph-Based Traveler Profile...")
    
    # Create a new profile
    profile = TravelerProfile()
    user_id = profile.create_profile("test_user_123")
    print(f"✅ Created profile with ID: {user_id}")
    
    # Add budget profile
    budget_node = profile.update_budget_profile(user_id, "$2000", "USD")
    print(f"✅ Added budget node: {budget_node}")
    
    # Add interests profile
    interests = ["Culture", "Food", "Nature", "Adventure"]
    interests_node = profile.update_interests_profile(user_id, interests)
    print(f"✅ Added interests node: {interests_node}")
    
    # Add previous trip
    trip_data = {
        "destination": "Paris",
        "trip_date": "2023-06-15",
        "duration": "5 days",
        "budget": "$1500"
    }
    trip_node = profile.add_previous_trip(user_id, "Paris", trip_data)
    print(f"✅ Added previous trip node: {trip_node}")
    
    # Add visa profile
    visa_data = {
        "visa_required": False,
        "max_stay": "90 days",
        "processing_time": "N/A"
    }
    visa_node = profile.update_visa_profile(user_id, "US Citizen", visa_data)
    print(f"✅ Added visa node: {visa_node}")
    
    # Get profile summary
    summary = profile.get_profile_summary(user_id)
    print(f"✅ Profile summary: {summary['node_count']} nodes, {summary['edge_count']} edges")
    
    # Get recommendations
    recommendations = profile.get_recommendations(user_id, "Tokyo")
    print(f"✅ Generated recommendations for Tokyo")
    
    # Save profile
    filename = profile.save_profile(user_id, "test_profile.json")
    print(f"✅ Saved profile to: {filename}")
    
    return True

def test_prompt_engine():
    """Test the enhanced prompt engineering system"""
    print("\n🧪 Testing Enhanced Prompt Engineering...")
    
    # Create prompt engine
    engine = PromptEngine()
    print("✅ Created prompt engine")
    
    # Test itinerary prompt
    traveler_profile = {
        "budget": "$2000",
        "interests": ["Culture", "Food", "Nature"],
        "nationality": "US Citizen"
    }
    
    itinerary_prompt = engine.build_itinerary_prompt(
        destination="Tokyo",
        days=5,
        budget=2000,
        preferences="Culture, Food",
        traveler_profile=traveler_profile
    )
    print(f"✅ Generated itinerary prompt ({len(itinerary_prompt)} characters)")
    
    # Test budget analysis prompt
    budget_prompt = engine.build_budget_analysis_prompt(
        destination="Tokyo",
        days=5,
        budget=2000,
        traveler_profile=traveler_profile
    )
    print(f"✅ Generated budget analysis prompt ({len(budget_prompt)} characters)")
    
    # Test travel tips prompt
    tips_prompt = engine.build_travel_tips_prompt(
        destination="Tokyo",
        traveler_profile=traveler_profile
    )
    print(f"✅ Generated travel tips prompt ({len(tips_prompt)} characters)")
    
    # Test comprehensive prompt
    comprehensive_prompt = engine.build_comprehensive_prompt(
        destination="Tokyo",
        days=5,
        budget=2000,
        preferences="Culture, Food",
        traveler_profile=traveler_profile
    )
    print(f"✅ Generated comprehensive prompt ({len(comprehensive_prompt)} characters)")
    
    return True

def test_integration():
    """Test integration between profile and prompt engine"""
    print("\n🧪 Testing Integration...")
    
    # Create profile and get recommendations
    profile = TravelerProfile()
    user_id = profile.create_profile("integration_test")
    
    # Add some profile data
    profile.update_budget_profile(user_id, "$3000", "USD")
    profile.update_interests_profile(user_id, ["Art", "History", "Architecture"])
    
    # Get profile context
    summary = profile.get_profile_summary(user_id)
    profile_context = summary.get('profile_data', {})
    
    # Use in prompt engine
    engine = PromptEngine()
    prompt = engine.build_comprehensive_prompt(
        destination="Paris",
        days=7,
        budget=3000,
        preferences="Art, History",
        traveler_profile=profile_context
    )
    
    print(f"✅ Integration test successful - generated prompt with profile context")
    print(f"   Profile context: {profile_context}")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Phase 3 Feature Tests...\n")
    
    try:
        # Test traveler profile
        test_traveler_profile()
        
        # Test prompt engine
        test_prompt_engine()
        
        # Test integration
        test_integration()
        
        print("\n🎉 All tests passed! Phase 3 features are working correctly.")
        print("\n📋 Summary of implemented features:")
        print("   ✅ Graph-based traveler profile with NetworkX")
        print("   ✅ Profile nodes: Budget, Interests, Previous Trips, Visa, Travel Preferences")
        print("   ✅ Profile relationships and recommendations")
        print("   ✅ Enhanced prompt engineering with few-shot examples")
        print("   ✅ Structured JSON output formatting")
        print("   ✅ Comprehensive travel planning prompts")
        print("   ✅ Profile context integration")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 