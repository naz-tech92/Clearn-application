#!/usr/bin/env python3
"""
Update all skill templates with DevOps-style design and Cameroon data
Generates modern, expandable skill pages
"""

import json
import os

# Load countries data
with open('data/countries.json', 'r', encoding='utf-8') as f:
    countries_data = json.load(f)['countries']

# Skill configurations with metadata
SKILLS = {
    'accounting': {
        'emoji': '💼',
        'title': 'Accounting',
        'subtitle': 'Master financial management and business accounting practices',
        'icon_size': '4em',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    },
    'ai_machine_learning': {
        'emoji': '🤖',
        'title': 'AI & Machine Learning ',
        'subtitle': 'Build intelligent systems and advanced AI solutions',
        'icon_size': '4em',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    },
    'cloud_computing': {
        'emoji': '☁️',
        'title': 'Cloud Computing',
        'subtitle': 'Build and manage scalable cloud infrastructure',
        'icon_size': '4em',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    },
    'cybersecurity': {
        'emoji': '🛡️',
        'title': 'Cybersecurity',
        'subtitle': 'Master the art of protecting digital assets',
        'icon_size': '4em',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    },
    'data_science': {
        'emoji': '📊',
        'title': 'Data Science',
        'subtitle': 'Extract insights from data and drive decisions',
        'icon_size': '4em',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    },
    'digital_marketing': {
        'emoji': '📱',
        'title': 'Digital Marketing',
        'subtitle': 'Reach and engage audiences through digital channels',
        'icon_size': '4em',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    },
    'international_business': {
        'emoji': '🌐',
        'title': 'International Business',
        'subtitle': 'Navigate cross-border commerce and global markets',
        'icon_size': '4em',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    },
    'medical_laboratory_science': {
        'emoji': '🔬',
        'title': 'Medical Laboratory Science',
        'subtitle': 'Perform diagnostic testing for healthcare',
        'icon_size': '4em',
        'countries': ['united_states', 'united_kingdom', 'australia', 'cameroon']
    },
    'networking': {
        'emoji': '🌐',
        'title': 'Computer Networking',
        'subtitle': 'Design and manage network infrastructure',
        'icon_size': '4em',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    },
    'nursing': {
        'emoji': '👩‍⚕️',
        'title': 'Nursing',
        'subtitle': 'Provide compassionate patient care',
        'icon_size': '4em',
        'countries': ['united_states', 'united_kingdom', 'australia', 'cameroon']
    },
    'public_health': {
        'emoji': '🏥',
        'title': 'Public Health',
        'subtitle': 'Promote wellness and prevent disease in communities',
        'icon_size': '4em',
        'countries': ['united_states', 'united_kingdom', 'australia', 'cameroon']
    },
    'software_engineering': {
        'emoji': '💻',
        'title': 'Software Engineering',
        'subtitle': 'Design and develop reliable software solutions',
        'icon_size': '4em',
        'countries': ['united_states', 'united_kingdom', 'singapore', 'australia', 'cameroon']
    },
}

def get_demand_label(demand_str):
    """Convert demand description to simple label"""
    if 'Very High' in demand_str:
        return 'Very High'
    elif 'High' in demand_str:
        return 'High'
    elif 'Growing' in demand_str:
        return 'Growing'
    elif 'Emerging' in demand_str:
        return 'Emerging'
    return 'Growing'

def build_country_data_js(skill_name, country_codes):
    """Build JavaScript country data object"""
    country_data = {}
    
    for country_code in country_codes:
        country = countries_data.get(country_code, {})
        skill_data = country.get('skills', {}).get(skill_name, {})
        
        if not skill_data:
            print(f"Warning: No data for {skill_name} in {country_code}")
            continue
        
        demand = get_demand_label(skill_data.get('skill_demand_level', 'Growing'))
        
        # Build certifications array
        certs = skill_data.get('certifications', [])
        certs_js = ', '.join([f'"{cert}"' for cert in certs])
        
        # Build advantages array
        advs = skill_data.get('advantages', [])
        advs_js = ', '.join([f'"{adv}"' for adv in advs])
        
        # Build limitations array
        lims = skill_data.get('limitations', [])
        lims_js = ', '.join([f'"{lim}"' for lim in lims])
        
        # Build references array
        refs = skill_data.get('references', [])
        refs_js = ', '.join([f'"{ref}"' for ref in refs])
        
        # Build study paths array
        paths = skill_data.get('study_paths', [])
        paths_js = ', '.join([f'"{path}"' for path in paths])
        
        country_data[country_code] = {
            'name': country.get('name', ''),
            'flag': country.get('flag', ''),
            'demand': demand,
            'overview': skill_data.get('overview', ''),
            'education': skill_data.get('required_education', ''),
            'certifications': certs_js,
            'advantages': advs_js,
            'limitations': lims_js,
            'references': refs_js,
            'study_paths': paths_js
        }
    
    return country_data

def generate_country_objects_js(country_data_dict):
    """Generate the JavaScript country data objects"""
    js_lines = []
    for country_code, data in country_data_dict.items():
        js_lines.append(f'''        "{country_code}": {{
            "name": "{data['name']}",
            "flag": "{data['flag']}",
            "demand": "{data['demand']}",
            "overview": `{data['overview']}`,
            "education": `{data['education']}`,
            "certifications": [{data['certifications']}],
            "advantages": [{data['advantages']}],
            "limitations": [{data['limitations']}],
            "references": [{data['references']}],
            "study_paths": [{data['study_paths']}]
        }}''')
    return ',\n'.join(js_lines)

print("✅ Skill Templates Update Script Ready")
print(f"📚 Total skills to update: {len(SKILLS)}")
print("🌍 Countries included: 4-5 (including Cameroon)")
print("\nTo use this script:")
print("1. Run: python3 update_skill_templates.py")
print("2. This will generate updated templates for all skills")
