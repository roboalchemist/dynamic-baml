#!/usr/bin/env python3
"""
Real-World Use Cases for Dynamic BAML

This example demonstrates practical applications:
- Document processing and data extraction
- Customer feedback analysis
- Content categorization and tagging
- Product information extraction
- Resume/CV parsing
- Invoice and receipt processing
"""

from dynamic_baml import call_with_schema
import json


def customer_feedback_analysis():
    """Extract insights from customer feedback for business intelligence."""
    print("💬 Customer Feedback Analysis")
    print("-" * 40)
    
    schema = {
        "feedback_analysis": {
            "customer_info": {
                "type": {
                    "type": "enum",
                    "values": ["individual", "business", "enterprise"]
                },
                "satisfaction_level": {
                    "type": "enum",
                    "values": ["very_unsatisfied", "unsatisfied", "neutral", "satisfied", "very_satisfied"]
                }
            },
            "product_mentions": [
                {
                    "product_name": "string",
                    "sentiment": {
                        "type": "enum",
                        "values": ["positive", "negative", "neutral"]
                    },
                    "specific_issues": ["string"],
                    "praised_features": ["string"]
                }
            ],
            "actionable_insights": {
                "priority": {
                    "type": "enum",
                    "values": ["low", "medium", "high", "urgent"]
                },
                "department": {
                    "type": "enum",
                    "values": ["support", "development", "sales", "billing", "management"]
                },
                "suggested_actions": ["string"]
            },
            "follow_up_required": "bool",
            "estimated_resolution_time": "string"
        }
    }
    
    feedback = """
    Hi, I'm writing as the IT director for MegaCorp Inc. We've been using your DataFlow Pro 
    for 6 months now and overall we're quite satisfied with the real-time analytics 
    capabilities. The dashboard is intuitive and our team picked it up quickly.
    
    However, we're experiencing some significant issues with the API integration. 
    The authentication keeps timing out, especially during peak hours, which is 
    disrupting our automated reports. This is becoming a major problem for our 
    daily operations.
    
    We also love the new machine learning features you added - they've helped us 
    identify trends we never saw before. But the pricing structure is confusing, 
    and we got charged unexpectedly for extra API calls last month.
    
    We need this API issue resolved urgently as it's affecting our client deliverables. 
    Please prioritize this and get back to us within 24 hours.
    """
    
    result = call_with_schema(
        f"Analyze this customer feedback for business insights:\n\n{feedback}",
        schema,
        {"provider": "openai", "model": "gpt-4"}
    )
    
    print("📊 Feedback Analysis Result:")
    print(json.dumps(result, indent=2))
    return result


def resume_parsing():
    """Parse resumes for HR and recruitment systems."""
    print("\n📄 Resume/CV Parsing")
    print("-" * 40)
    
    schema = {
        "candidate_profile": {
            "personal_info": {
                "name": "string",
                "email": "string",
                "phone": {"type": "string", "optional": True},
                "location": {"type": "string", "optional": True}
            },
            "professional_summary": "string",
            "experience": [
                {
                    "company": "string",
                    "position": "string",
                    "duration": "string",
                    "responsibilities": ["string"],
                    "achievements": {"type": "array", "items": "string", "optional": True}
                }
            ],
            "education": [
                {
                    "institution": "string",
                    "degree": "string",
                    "field": "string",
                    "graduation_year": {"type": "int", "optional": True}
                }
            ],
            "skills": {
                "technical": ["string"],
                "soft_skills": ["string"],
                "languages": {"type": "array", "items": "string", "optional": True}
            },
            "certifications": {
                "type": "array",
                "items": {
                    "name": "string",
                    "issuer": "string",
                    "date": {"type": "string", "optional": True}
                },
                "optional": True
            }
        }
    }
    
    resume_text = """
    SARAH JOHNSON
    Senior Software Engineer
    sarah.johnson@email.com | (555) 123-4567 | San Francisco, CA
    
    PROFESSIONAL SUMMARY
    Experienced full-stack developer with 8+ years building scalable web applications. 
    Passionate about clean code, agile methodologies, and mentoring junior developers.
    
    WORK EXPERIENCE
    
    Senior Software Engineer | TechCorp Inc. | 2021 - Present
    • Led development of microservices architecture serving 10M+ users
    • Mentored team of 5 junior developers, improving code review efficiency by 40%
    • Implemented CI/CD pipeline reducing deployment time from 4 hours to 30 minutes
    • Technologies: React, Node.js, AWS, Docker, Kubernetes
    
    Software Engineer | StartupXYZ | 2019 - 2021
    • Built customer-facing dashboard used by 50,000+ daily active users
    • Optimized database queries improving application performance by 60%
    • Collaborated with product team to deliver features ahead of schedule
    
    Junior Developer | WebSolutions | 2016 - 2019
    • Developed responsive websites for small to medium businesses
    • Maintained legacy PHP applications and migrated to modern frameworks
    • Participated in code reviews and agile sprint planning
    
    EDUCATION
    
    Bachelor of Science in Computer Science | UC Berkeley | 2016
    Relevant Coursework: Data Structures, Algorithms, Database Systems
    
    TECHNICAL SKILLS
    Languages: JavaScript, Python, Java, TypeScript, SQL
    Frameworks: React, Vue.js, Express.js, Django, Spring Boot
    Tools: Git, Docker, AWS, Jenkins, JIRA
    Databases: PostgreSQL, MongoDB, Redis
    
    SOFT SKILLS
    Leadership, Problem Solving, Communication, Team Collaboration
    
    LANGUAGES
    English (Native), Spanish (Conversational), Mandarin (Basic)
    
    CERTIFICATIONS
    AWS Certified Solutions Architect | Amazon Web Services | 2022
    Certified Scrum Master | Scrum Alliance | 2021
    """
    
    result = call_with_schema(
        f"Parse this resume and extract structured information:\n\n{resume_text}",
        schema,
        {"provider": "openai", "model": "gpt-4"}
    )
    
    print("👤 Parsed Resume Data:")
    print(json.dumps(result, indent=2))
    return result


def product_catalog_extraction():
    """Extract product information from unstructured descriptions."""
    print("\n🛍️ Product Catalog Extraction")
    print("-" * 40)
    
    schema = {
        "product": {
            "basic_info": {
                "name": "string",
                "brand": "string",
                "category": "string",
                "subcategory": {"type": "string", "optional": True}
            },
            "pricing": {
                "price": "float",
                "currency": "string",
                "discount": {"type": "float", "optional": True},
                "promotion": {"type": "string", "optional": True}
            },
            "specifications": {
                "dimensions": {"type": "string", "optional": True},
                "weight": {"type": "string", "optional": True},
                "color_options": ["string"],
                "material": {"type": "string", "optional": True},
                "key_features": ["string"]
            },
            "availability": {
                "in_stock": "bool",
                "stock_level": {
                    "type": "enum",
                    "values": ["low", "medium", "high", "out_of_stock"]
                },
                "shipping_time": "string"
            },
            "ratings": {
                "average_rating": {"type": "float", "optional": True},
                "review_count": {"type": "int", "optional": True},
                "pros": {"type": "array", "items": "string", "optional": True},
                "cons": {"type": "array", "items": "string", "optional": True}
            }
        }
    }
    
    product_description = """
    iPhone 15 Pro Max - Apple's Latest Flagship
    
    Experience the power of the A17 Pro chip in Apple's most advanced iPhone yet. 
    The iPhone 15 Pro Max features a stunning 6.7-inch Super Retina XDR display 
    with ProMotion technology.
    
    Price: $1,199.00 USD (SPECIAL OFFER: Save $100 with trade-in!)
    
    Key Features:
    • A17 Pro chip with 6-core GPU for incredible performance
    • Pro camera system with 48MP main camera, 12MP ultra-wide, and 12MP telephoto
    • Action button for quick access to your favorite features
    • USB-C connectivity for universal charging
    • Titanium design - lighter yet stronger than steel
    • All-day battery life with up to 29 hours video playback
    
    Available Colors: Natural Titanium, Blue Titanium, White Titanium, Black Titanium
    
    Dimensions: 6.30 x 3.02 x 0.32 inches
    Weight: 7.81 ounces (221 grams)
    
    Customer Reviews: 4.5/5 stars (2,847 reviews)
    Customers love: Premium build quality, excellent camera system, fast performance
    Common concerns: High price point, lack of USB-C cable in box
    
    Stock Status: In Stock - Ships within 1-2 business days
    Current inventory level: High stock available
    """
    
    result = call_with_schema(
        f"Extract detailed product information from this description:\n\n{product_description}",
        schema,
        {"provider": "openai", "model": "gpt-4"}
    )
    
    print("📱 Extracted Product Data:")
    print(json.dumps(result, indent=2))
    return result


def invoice_processing():
    """Process invoices and extract billing information."""
    print("\n📋 Invoice Processing")
    print("-" * 40)
    
    schema = {
        "invoice": {
            "header": {
                "invoice_number": "string",
                "date": "string",
                "due_date": {"type": "string", "optional": True},
                "po_number": {"type": "string", "optional": True}
            },
            "vendor": {
                "name": "string",
                "address": "string",
                "phone": {"type": "string", "optional": True},
                "email": {"type": "string", "optional": True},
                "tax_id": {"type": "string", "optional": True}
            },
            "billing_to": {
                "company": "string",
                "address": "string",
                "contact": {"type": "string", "optional": True}
            },
            "line_items": [
                {
                    "description": "string",
                    "quantity": "int",
                    "unit_price": "float",
                    "total": "float",
                    "category": {"type": "string", "optional": True}
                }
            ],
            "totals": {
                "subtotal": "float",
                "tax_rate": {"type": "float", "optional": True},
                "tax_amount": {"type": "float", "optional": True},
                "total_amount": "float",
                "currency": "string"
            },
            "payment_terms": {"type": "string", "optional": True}
        }
    }
    
    invoice_text = """
    ACME OFFICE SUPPLIES
    123 Business Blvd, Suite 100
    New York, NY 10001
    Phone: (555) 987-6543
    Email: billing@acmeoffice.com
    Tax ID: 12-3456789
    
    INVOICE
    
    Invoice #: INV-2024-0892
    Date: January 15, 2024
    Due Date: February 14, 2024
    PO Number: PO-78945
    
    Bill To:
    TechStart Inc.
    456 Innovation Drive
    San Francisco, CA 94107
    Attn: Finance Department
    
    Description                     Qty    Unit Price    Total
    -------------------------------------------------------
    Ergonomic Office Chairs        12     $299.99       $3,599.88
    Standing Desks (Adjustable)    6      $649.99       $3,899.94
    Wireless Keyboards             15     $89.99        $1,349.85
    4K Monitors (27-inch)          8      $449.99       $3,599.92
    Cable Management Systems       20     $24.99        $499.80
    
    Subtotal:                                            $12,949.39
    Sales Tax (8.25%):                                   $1,068.32
    
    TOTAL AMOUNT DUE:                                    $14,017.71 USD
    
    Payment Terms: Net 30 days
    """
    
    result = call_with_schema(
        f"Process this invoice and extract all billing information:\n\n{invoice_text}",
        schema,
        {"provider": "openai", "model": "gpt-4"}
    )
    
    print("💰 Processed Invoice Data:")
    print(json.dumps(result, indent=2))
    return result


def content_categorization():
    """Categorize and tag content for content management systems."""
    print("\n📚 Content Categorization and Tagging")
    print("-" * 40)
    
    schema = {
        "content_analysis": {
            "categorization": {
                "primary_category": {
                    "type": "enum",
                    "values": ["technology", "business", "science", "health", "education", "entertainment", "sports", "politics", "lifestyle"]
                },
                "subcategories": ["string"],
                "content_type": {
                    "type": "enum",
                    "values": ["article", "tutorial", "news", "opinion", "review", "research", "guide"]
                }
            },
            "audience": {
                "target_level": {
                    "type": "enum",
                    "values": ["beginner", "intermediate", "advanced", "expert"]
                },
                "target_audience": ["string"],
                "age_group": {
                    "type": "enum",
                    "values": ["children", "teens", "young_adults", "adults", "seniors", "all_ages"]
                }
            },
            "metadata": {
                "reading_time_minutes": "int",
                "word_count": "int",
                "language": "string",
                "tone": {
                    "type": "enum",
                    "values": ["formal", "casual", "technical", "conversational", "academic"]
                }
            },
            "tags": ["string"],
            "keywords": ["string"],
            "summary": "string"
        }
    }
    
    article_content = """
    Getting Started with Machine Learning: A Beginner's Guide to Python Libraries
    
    Machine learning has become one of the most exciting fields in technology, 
    and Python has emerged as the go-to programming language for ML practitioners. 
    Whether you're a software developer looking to expand your skills or a 
    complete beginner curious about AI, this guide will help you take your first 
    steps into the world of machine learning.
    
    What is Machine Learning?
    
    Machine learning is a subset of artificial intelligence that enables computers 
    to learn and make decisions from data without being explicitly programmed for 
    every scenario. Instead of following pre-written instructions, ML algorithms 
    identify patterns in data and use these patterns to make predictions or decisions.
    
    Why Python for Machine Learning?
    
    Python's popularity in machine learning stems from several factors:
    - Simple, readable syntax that's perfect for beginners
    - Extensive ecosystem of specialized libraries
    - Strong community support and documentation
    - Integration capabilities with other technologies
    
    Essential Python Libraries for ML
    
    1. NumPy: The foundation for numerical computing in Python
    2. Pandas: Data manipulation and analysis made easy
    3. Scikit-learn: User-friendly machine learning algorithms
    4. Matplotlib: Data visualization for understanding your results
    5. Jupyter Notebooks: Interactive development environment
    
    Your First ML Project
    
    Let's create a simple prediction model using a classic dataset. We'll predict 
    house prices based on features like size, location, and age. This project will 
    introduce you to the basic workflow of machine learning: data preparation, 
    model training, and evaluation.
    
    [Code examples and detailed explanations would follow...]
    
    Next Steps
    
    Once you've completed this tutorial, consider exploring more advanced topics 
    like deep learning with TensorFlow or PyTorch, or specialized applications 
    like natural language processing or computer vision.
    
    Remember, machine learning is a journey, not a destination. Start with the 
    basics, practice regularly, and don't be afraid to experiment with different 
    approaches. The ML community is welcoming and always ready to help newcomers.
    """
    
    result = call_with_schema(
        f"Analyze and categorize this content:\n\n{article_content}",
        schema,
        {"provider": "openai", "model": "gpt-4"}
    )
    
    print("🏷️ Content Analysis Result:")
    print(json.dumps(result, indent=2))
    return result


def batch_processing_example():
    """Demonstrate batch processing for multiple documents."""
    print("\n⚡ Batch Processing Example")
    print("-" * 40)
    
    schema = {
        "document_summary": {
            "title": "string",
            "main_topic": "string",
            "sentiment": {
                "type": "enum",
                "values": ["positive", "negative", "neutral"]
            },
            "key_points": ["string"],
            "action_items": ["string"],
            "urgency": {
                "type": "enum",
                "values": ["low", "medium", "high"]
            }
        }
    }
    
    documents = [
        {
            "id": "email_001",
            "content": "Hi team, great job on the Q4 results! Our revenue increased by 25% and customer satisfaction scores are at an all-time high. Let's schedule a celebration meeting next week."
        },
        {
            "id": "support_ticket_047",
            "content": "URGENT: Our main server is experiencing critical issues. Customer-facing applications are down. Multiple clients are reporting complete service outages. Need immediate attention from DevOps team."
        },
        {
            "id": "proposal_review",
            "content": "The client proposal looks solid overall. The technical approach is sound and the timeline seems realistic. However, we should review the budget allocation for the testing phase and consider adding more buffer time."
        }
    ]
    
    results = []
    for doc in documents:
        print(f"Processing document: {doc['id']}")
        
        result = call_with_schema(
            f"Analyze this document and extract key information:\n\n{doc['content']}",
            schema,
            {"provider": "openai", "model": "gpt-4"}
        )
        
        results.append({
            "document_id": doc["id"],
            "analysis": result
        })
    
    print("\n📊 Batch Processing Results:")
    for result in results:
        print(f"\n{result['document_id']}:")
        print(f"  Topic: {result['analysis']['document_summary']['main_topic']}")
        print(f"  Sentiment: {result['analysis']['document_summary']['sentiment']}")
        print(f"  Urgency: {result['analysis']['document_summary']['urgency']}")
        print(f"  Action Items: {len(result['analysis']['document_summary']['action_items'])}")
    
    return results


if __name__ == "__main__":
    print("=== Dynamic BAML Real-World Use Cases ===\n")
    
    customer_feedback_analysis()
    resume_parsing()
    product_catalog_extraction()
    invoice_processing()
    content_categorization()
    batch_processing_example()
    
    print("\n✅ All real-world examples completed!") 