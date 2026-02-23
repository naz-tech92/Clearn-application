"""
Generate all skill templates with DevOps-style design and Cameroon data
This script creates consistent, modern skill pages from data
"""

import json
import os

# Load country data
with open('data/countries.json', 'r', encoding='utf-8') as f:
    countries_data = json.load(f)['countries']

# Skill configurations
skills_config = {
    'accounting': {
        'emoji': '💼',
        'title': 'Accounting',
        'subtitle': 'Master financial management and business accounting practices',
        'overview_title': 'What is Accounting?',
        'overview_desc': 'Accounting is the systematic recording, analysis, and reporting of financial transactions for individuals and organizations. It provides insights into financial health, ensures regulatory compliance, and supports informed business decision-making through accurate financial statements and reports.',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    },
    'ai_machine_learning': {
        'emoji': '🤖',
        'title': 'AI & Machine Learning',
        'subtitle': 'Build intelligent systems and advanced AI solutions',
        'overview_title': 'What is AI & Machine Learning?',
        'overview_desc': 'Artificial Intelligence and Machine Learning enable computers to learn from data and make intelligent decisions without explicit programming. These technologies power predictive analytics, natural language processing, computer vision, and autonomous systems across industries.',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    },
    'cloud_computing': {
        'emoji': '☁️',
        'title': 'Cloud Computing',
        'subtitle': 'Build and manage scalable cloud infrastructure',
        'overview_title': 'What is Cloud Computing?',
        'overview_desc': 'Cloud computing is the delivery of computing services over the internet, including servers, storage, databases, networking, software, and analytics. It enables organizations to access and use computing resources on-demand without having to manage physical infrastructure.',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    },
    'cybersecurity': {
        'emoji': '🛡️',
        'title': 'Cybersecurity',
        'subtitle': 'Master the art of protecting digital assets',
        'overview_title': 'What is Cybersecurity?',
        'overview_desc': 'Cybersecurity involves protecting internet-connected systems from digital attacks. It encompasses practices, technologies, and processes designed to safeguard information and systems from unauthorized access, theft, damage, or disruption.',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    },
    'data_science': {
        'emoji': '📊',
        'title': 'Data Science',
        'subtitle': 'Extract insights from data and drive decisions',
        'overview_title': 'What is Data Science?',
        'overview_desc': 'Data Science combines statistics, mathematics, and computer science to extract meaningful insights from data. It involves data collection, processing, analysis, and visualization to support informed business decisions and predictive modeling.',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    },
    'devops': {
        'emoji': '🔄',
        'title': 'DevOps',
        'subtitle': 'Streamline development and operations processes',
        'overview_title': 'What is DevOps?',
        'overview_desc': 'DevOps combines software development (Dev) and IT operations (Ops) to shorten the development lifecycle and provide continuous delivery of high-quality software. It emphasizes collaboration, automation, and monitoring throughout the software development process.',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    },
    'digital_marketing': {
        'emoji': '📱',
        'title': 'Digital Marketing',
        'subtitle': 'Reach and engage audiences through digital channels',
        'overview_title': 'What is Digital Marketing?',
        'overview_desc': 'Digital Marketing encompasses all marketing efforts using digital channels including social media, email, search engines, content marketing, and paid advertising. It enables businesses to reach targeted audiences efficiently and measure campaign performance in real-time.',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    },
    'international_business': {
        'emoji': '🌐',
        'title': 'International Business',
        'subtitle': 'Navigate cross-border commerce and global markets',
        'overview_title': 'What is International Business?',
        'overview_desc': 'International Business involves conducting commercial activities across national borders, managing supply chains, understanding regulations, and engaging with diverse cultures. It encompasses import/export, multinational operations, and cross-border investments.',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    },
    'medical_laboratory_science': {
        'emoji': '🔬',
        'title': 'Medical Laboratory Science',
        'subtitle': 'Perform diagnostic testing for healthcare',
        'overview_title': 'What is Medical Laboratory Science?',
        'overview_desc': 'Medical Laboratory Science involves analyzing blood, body tissues, and other specimens to detect diseases and support clinical diagnoses. Laboratory professionals work with advanced equipment and techniques to provide accurate test results that guide patient treatment.',
        'countries': ['united_states', 'united_kingdom', 'australia', 'cameroon']
    },
    'networking': {
        'emoji': '🌐',
        'title': 'Computer Networking',
        'subtitle': 'Design and manage network infrastructure',
        'overview_title': 'What is Computer Networking?',
        'overview_desc': 'Computer Networking involves designing, implementing, and maintaining the systems that connect computers and devices. Network professionals ensure reliable communication, security, and performance across organizations.',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    },
    'nursing': {
        'emoji': '👩‍⚕️',
        'title': 'Nursing',
        'subtitle': 'Provide compassionate patient care',
        'overview_title': 'What is Nursing?',
        'overview_desc': 'Nursing is a healthcare profession focused on providing patient care, managing treatment plans, and promoting health. Nurses work in hospitals, clinics, and communities to support patient recovery and maintain quality of life.',
        'countries': ['united_states', 'united_kingdom', 'australia', 'cameroon']
    },
    'public_health': {
        'emoji': '🏥',
        'title': 'Public Health',
        'subtitle': 'Promote wellness and prevent disease in communities',
        'overview_title': 'What is Public Health?',
        'overview_desc': 'Public Health focuses on protecting and improving the health of entire populations through disease prevention, health promotion, and policy development. It addresses factors like epidemiology, environmental health, and health equity.',
        'countries': ['united_states', 'united_kingdom', 'australia', 'cameroon']
    },
    'software_engineering': {
        'emoji': '💻',
        'title': 'Software Engineering',
        'subtitle': 'Design and develop reliable software solutions',
        'overview_title': 'What is Software Engineering?',
        'overview_desc': 'Software Engineering applies systematic principles and practices to design, develop, test, and maintain software applications. It combines programming with project management, quality assurance, and architectural planning to deliver robust solutions.',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    }
}

def get_country_data_for_skill(skill_name, country_code):
    """Extract country data for a specific skill"""
    country = countries_data.get(country_code, {})
    skills = country.get('skills', {})
    return skills.get(skill_name, {})

def format_demand_level(demand_str):
    """Convert demand string to demand level for badge styling"""
    if 'Very High' in demand_str:
        return 'Very High'
    elif 'High' in demand_str:
        return 'High'
    elif 'Growing' in demand_str:
        return 'Growing'
    elif 'Emerging' in demand_str:
        return 'Emerging'
    return 'Growing'

def generate_country_data_json(skill_name, country_codes):
    """Generate JavaScript country data for skill template"""
    country_data = {}
    
    for country_code in country_codes:
        country = countries_data.get(country_code, {})
        skill_data = country.get('skills', {}).get(skill_name, {})
        
        if not skill_data:
            continue
            
        demand = format_demand_level(skill_data.get('skill_demand_level', 'Growing'))
        
        country_data[country_code] = {
            'name': country.get('name', ''),
            'flag': country.get('flag', ''),
            'demand': demand,
            'overview': skill_data.get('overview', ''),
            'education': skill_data.get('required_education', ''),
            'certifications': skill_data.get('certifications', []),
            'advantages': skill_data.get('advantages', []),
            'limitations': skill_data.get('limitations', []),
            'references': skill_data.get('references', []),
            'study_paths': skill_data.get('study_paths', [])
        }
    
    return country_data

print("Skill Templates Generator Ready")
print("Skills available:", list(skills_config.keys()))
print("Total skills to generate:", len(skills_config))
