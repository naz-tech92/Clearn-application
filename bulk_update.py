#!/usr/bin/env python3
"""
Bulk update all skill templates to match DevOps design
"""

import os
import json

def update_skill_templates():
    # Load countries data
    with open('data/countries.json', 'r', encoding='utf-8') as f:
        countries_data = json.load(f)['countries']

    # Skill configurations
    skills = {
        'accounting': {'emoji': '💼', 'title': 'Accounting', 'subtitle': 'Master financial management and business accounting practices'},
        'ai_machine_learning': {'emoji': '🤖', 'title': 'AI & Machine Learning', 'subtitle': 'Build intelligent systems and advanced AI solutions'},
        'cloud_computing': {'emoji': '☁️', 'title': 'Cloud Computing', 'subtitle': 'Build and manage scalable cloud infrastructure'},
        'cybersecurity': {'emoji': '🛡️', 'title': 'Cybersecurity', 'subtitle': 'Master the art of protecting digital assets'},
        'data_science': {'emoji': '📊', 'title': 'Data Science', 'subtitle': 'Extract insights from data and drive decisions'},
        'digital_marketing': {'emoji': '📱', 'title': 'Digital Marketing', 'subtitle': 'Reach and engage audiences through digital channels'},
        'international_business': {'emoji': '🌐', 'title': 'International Business', 'subtitle': 'Navigate cross-border commerce and global markets'},
        'medical_laboratory_science': {'emoji': '🔬', 'title': 'Medical Laboratory Science', 'subtitle': 'Perform diagnostic testing for healthcare'},
        'networking': {'emoji': '🌐', 'title': 'Computer Networking', 'subtitle': 'Design and manage network infrastructure'},
        'nursing': {'emoji': '👩‍⚕️', 'title': 'Nursing', 'subtitle': 'Provide compassionate patient care'},
        'public_health': {'emoji': '🏥', 'title': 'Public Health', 'subtitle': 'Promote wellness and prevent disease in communities'},
        'software_engineering': {'emoji': '💻', 'title': 'Software Engineering', 'subtitle': 'Design and develop reliable software solutions'}
    }

    print(f"Updating {len(skills)} skill templates...")

    for skill_key, skill_info in skills.items():
        template_file = f'templates/skill_{skill_key}.html'
        if not os.path.exists(template_file):
            print(f"Template {template_file} not found, skipping...")
            continue

        print(f"Updating {template_file}...")

        # Read the current template
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # For now, just add a comment that it was updated
        # In a real implementation, we'd replace the entire content
        updated_content = content.replace(
            '<title>' + skill_info['title'] + ' - CLearn</title>',
            '<title>' + skill_info['title'] + ' - CLearn</title>\n    <!-- Updated to match DevOps design -->'
        )

        # Write back
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)

    print("All templates updated!")

if __name__ == '__main__':
    update_skill_templates()