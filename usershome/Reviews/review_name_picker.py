import os
import random

# Cache names at the module level
MALE_NAMES = []
FEMALE_NAMES = []

def load_name_lists():
    global MALE_NAMES, FEMALE_NAMES

    if not MALE_NAMES:  # Load once
        base_path = os.path.dirname(os.path.abspath(__file__))  # Same directory as this script

        with open(os.path.join(base_path, 'male_names.txt'), 'r', encoding='utf-8') as f:
            MALE_NAMES = [line.strip() for line in f if line.strip()]

        with open(os.path.join(base_path, 'female_names.txt'), 'r', encoding='utf-8') as f:
            FEMALE_NAMES = [line.strip() for line in f if line.strip()]

def get_random_name(gender: str) -> str:
    load_name_lists()

    if gender == 'male':
        return random.choice(MALE_NAMES)
    elif gender == 'female':
        return random.choice(FEMALE_NAMES)
    else:  # 'unisex'
        return random.choice(MALE_NAMES + FEMALE_NAMES)
