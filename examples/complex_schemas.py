#!/usr/bin/env python3
"""
Complex Schemas Example for Dynamic BAML

This example demonstrates advanced schema capabilities:
- Nested objects and complex hierarchies
- Arrays of various types
- Enum values and constraints
- Optional fields
- Mixed type structures
"""

from dynamic_baml import call_with_schema
import json


def nested_objects_example():
    """Example with deeply nested object structures."""
    
    schema = {
        "company": {
            "name": "string",
            "founded": "int",
            "headquarters": {
                "address": "string",
                "city": "string",
                "country": "string",
                "coordinates": {
                    "latitude": "float",
                    "longitude": "float"
                }
            },
            "employees": {
                "total": "int",
                "departments": {
                    "engineering": "int",
                    "sales": "int",
                    "marketing": "int"
                }
            }
        },
        "products": [
            {
                "name": "string",
                "category": "string",
                "price": "float",
                "features": ["string"]
            }
        ]
    }
    
    text = """
    TechCorp was founded in 2015 and is headquartered at 123 Innovation Drive, 
    San Francisco, California, USA (coordinates: 37.7749°N, 122.4194°W). 
    The company has 1,200 employees: 600 in engineering, 300 in sales, and 300 in marketing.
    
    Their main products include:
    1. DataFlow Pro ($299/month) - A data analytics platform with real-time dashboards, 
       machine learning integration, and API connectivity.
    2. CloudSync Enterprise ($199/month) - A cloud storage solution offering 
       unlimited storage, advanced security, and team collaboration tools.
    """
    
    prompt = f"""
    Extract comprehensive company information from the following text:
    
    {text}
    
    Please extract all company details, location information, employee counts, 
    and product information with their features.
    """
    
    result = call_with_schema(prompt, schema, {"provider": "openai", "model": "gpt-4"})
    
    print("🏢 Complex Company Structure:")
    print(json.dumps(result, indent=2))
    return result


def enum_and_arrays_example():
    """Example with multiple enums and various array types."""
    
    schema = {
        "event": {
            "title": "string",
            "type": {
                "type": "enum",
                "values": ["conference", "workshop", "webinar", "meetup", "hackathon"]
            },
            "status": {
                "type": "enum", 
                "values": ["planning", "open_registration", "sold_out", "in_progress", "completed"]
            },
            "priority": {
                "type": "enum",
                "values": ["low", "medium", "high", "critical"]
            }
        },
        "schedule": [
            {
                "session_name": "string",
                "speaker": "string",
                "duration_minutes": "int",
                "tags": ["string"]
            }
        ],
        "attendee_counts": ["int"],
        "ticket_prices": ["float"],
        "sponsors": ["string"]
    }
    
    text = """
    The Annual AI Conference 2024 is a high-priority conference event that's currently 
    in the open registration phase. The event features multiple sessions:
    
    - "Future of Machine Learning" by Dr. Sarah Chen (90 minutes) 
      [tags: AI, Machine Learning, Research]
    - "Practical Deep Learning" by Prof. Mike Johnson (60 minutes)
      [tags: Deep Learning, Practical, Hands-on]
    - "Ethics in AI" by Dr. Lisa Park (45 minutes)
      [tags: Ethics, AI Policy, Society]
    
    Expected attendance: 500 people for day 1, 400 for day 2, 350 for day 3.
    Ticket prices: $299.99 for regular admission, $499.99 for VIP, $199.99 for students.
    
    Event sponsors include TechCorp, DataFlow Inc, and AI Innovations Ltd.
    """
    
    prompt = f"""
    Extract detailed event information including all sessions, schedules, 
    pricing, and logistics from:
    
    {text}
    """
    
    result = call_with_schema(prompt, schema, {"provider": "openai", "model": "gpt-4"})
    
    print("🎯 Event with Enums and Arrays:")
    print(json.dumps(result, indent=2))
    return result


def optional_fields_example():
    """Example demonstrating optional field handling."""
    
    schema = {
        "user": {
            "name": "string",
            "email": "string",
            "phone": {"type": "string", "optional": True},
            "bio": {"type": "string", "optional": True}
        },
        "preferences": {
            "newsletter": "bool",
            "notifications": "bool",
            "theme": {
                "type": "enum",
                "values": ["light", "dark", "auto"],
                "optional": True
            },
            "language": {"type": "string", "optional": True}
        },
        "social_media": {
            "twitter": {"type": "string", "optional": True},
            "linkedin": {"type": "string", "optional": True},
            "github": {"type": "string", "optional": True}
        },
        "skills": {
            "type": "array",
            "items": "string",
            "optional": True
        }
    }
    
    text = """
    User profile for Emily Rodriguez (emily.rodriguez@example.com). 
    She wants to receive newsletters and notifications. 
    Her LinkedIn profile is linkedin.com/in/emily-rodriguez.
    Emily is skilled in Python, JavaScript, and Data Science.
    """
    
    prompt = f"""
    Extract user profile information from the text. Note that some fields 
    like phone, bio, twitter, github, theme, and language might not be mentioned 
    and should be omitted if not present:
    
    {text}
    """
    
    result = call_with_schema(prompt, schema, {"provider": "openai", "model": "gpt-4"})
    
    print("👤 User Profile with Optional Fields:")
    print(json.dumps(result, indent=2))
    return result


def mixed_complex_example():
    """Example with highly complex mixed schema types."""
    
    schema = {
        "project": {
            "name": "string",
            "description": "string",
            "status": {
                "type": "enum",
                "values": ["planning", "active", "on_hold", "completed", "cancelled"]
            },
            "budget": {
                "total": "float",
                "spent": "float",
                "currency": "string"
            },
            "timeline": {
                "start_date": "string",
                "end_date": {"type": "string", "optional": True},
                "milestones": [
                    {
                        "name": "string",
                        "date": "string",
                        "completed": "bool",
                        "deliverables": ["string"]
                    }
                ]
            },
            "team": [
                {
                    "name": "string",
                    "role": {
                        "type": "enum",
                        "values": ["manager", "developer", "designer", "analyst", "tester"]
                    },
                    "allocation": "float",
                    "skills": ["string"],
                    "contact": {
                        "email": "string",
                        "phone": {"type": "string", "optional": True}
                    }
                }
            ],
            "risks": {
                "type": "array",
                "items": {
                    "description": "string",
                    "probability": {
                        "type": "enum",
                        "values": ["low", "medium", "high"]
                    },
                    "impact": {
                        "type": "enum", 
                        "values": ["low", "medium", "high"]
                    },
                    "mitigation": {"type": "string", "optional": True}
                },
                "optional": True
            }
        }
    }
    
    text = """
    Project: NextGen E-commerce Platform
    
    Description: Building a modern, scalable e-commerce platform with AI-powered 
    recommendations and real-time inventory management. Currently in active development.
    
    Budget: $2,500,000 total budget in USD, with $850,000 already spent.
    
    Timeline: Started January 15, 2024, planned completion by December 31, 2024.
    
    Key milestones:
    1. MVP Development (March 30, 2024) - COMPLETED
       Deliverables: Basic user interface, product catalog, shopping cart
    2. AI Integration (June 15, 2024) - IN PROGRESS  
       Deliverables: Recommendation engine, predictive analytics
    3. Beta Launch (September 1, 2024) - PENDING
       Deliverables: User testing, performance optimization, bug fixes
    
    Team members:
    - Sarah Kim (Project Manager, 100% allocation) - email: sarah.kim@company.com
      Skills: Agile, Stakeholder Management, Risk Assessment
    - Alex Chen (Senior Developer, 80% allocation) - email: alex.chen@company.com, phone: 555-0123
      Skills: React, Node.js, AWS, Database Design
    - Maria Santos (UI/UX Designer, 60% allocation) - email: maria.santos@company.com  
      Skills: Figma, User Research, Prototyping
    - Tom Wilson (Data Analyst, 40% allocation) - email: tom.wilson@company.com
      Skills: Python, SQL, Machine Learning, Statistics
    
    Key risks:
    1. Third-party API integration delays (medium probability, high impact) 
       - Mitigation: Identify backup vendors and maintain vendor relationships
    2. Team member availability during holiday season (high probability, medium impact)
    """
    
    prompt = f"""
    Extract comprehensive project information including team details, timeline, 
    budget, milestones, and risk assessment from:
    
    {text}
    
    Pay careful attention to:
    - Team member allocation percentages as decimal values (e.g., 100% = 1.0)
    - Milestone completion status from the context
    - Risk probability and impact levels
    - Optional fields that may not be present
    """
    
    result = call_with_schema(prompt, schema, {"provider": "openai", "model": "gpt-4"})
    
    print("🚀 Complex Project Structure:")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    print("=== Dynamic BAML Complex Schemas Examples ===\n")
    
    print("1. Nested Objects Example:")
    print("-" * 40)
    nested_objects_example()
    
    print("\n\n2. Enums and Arrays Example:")
    print("-" * 40)
    enum_and_arrays_example()
    
    print("\n\n3. Optional Fields Example:")
    print("-" * 40)
    optional_fields_example()
    
    print("\n\n4. Mixed Complex Example:")
    print("-" * 40)
    mixed_complex_example()
    
    print("\n✅ All complex schema examples completed!") 