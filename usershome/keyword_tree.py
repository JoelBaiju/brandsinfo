import json

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.category_id = []

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, category_id):
        current = self.root
        word = word.lower()  # Convert the word to lowercase before inserting
        for char in word:
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        current.is_end_of_word = True
        if category_id not in current.category_id:
            current.category_id.append(category_id)  # Append category ID to the list
            
            
    def search(self, word):
        current = self.root
        results = []

        # Traverse the Trie to the end of the prefix
        for char in word:
            if char not in current.children:
                return []  # Return empty list if prefix doesn't exist
            current = current.children[char]

        # Now collect all words that start with the given prefix
        def collect_words(node, prefix):
            if node.is_end_of_word:
                results.append((prefix, node.category_id))
            for char, child_node in node.children.items():
                collect_words(child_node, prefix + char)

        # Collect words starting from the end of the prefix
        collect_words(current, word)
        
        return results


    def serialize(self):
        """Serialize the Trie into a dictionary format."""
        def serialize_node(node):
            # Recursively serialize the trie nodes
            return {
                'children': {char: serialize_node(child) for char, child in node.children.items()},
                'is_end_of_word': node.is_end_of_word,
                'category_id': node.category_id
            }

        return json.dumps(serialize_node(self.root))

    def deserialize(self, data):
        """Deserialize from dictionary format to Trie structure."""
        def deserialize_node(data):
            # Recursively deserialize the trie nodes
            node = TrieNode()
            node.children = {char: deserialize_node(child_data) for char, child_data in data['children'].items()}
            node.is_end_of_word = data['is_end_of_word']
            node.category_id = data['category_id']
            return node

        self.root = deserialize_node(json.loads(data))

# Example usage:
# Create a new Trie
trie = Trie()

keywords_with_categories = [
    ("inverter", 1),
    ("pure sine wave inverter", 1),
    ("Modified Sine Wave Inverter", 1),
    ("Battery", 2),
    ("Lead Acid Battery", 2),
    ("Lithium-Ion Battery", 2),
    ("UPS", 3),
    ("UPS Servicing", 3),
    ("Accessories", 4),
    ("Cables", 4),
    ("Connectors", 4),
    ("Stands", 4),
    ("Solar Panel", 5),
    ("Monocrystalline Panel", 5),
    ("Polycrystalline Panel", 5),
    ("Solar Inverter", 6),
    ("Grid-Tied Inverter", 6),
    ("Off-Grid Inverter", 6),
    ("Solar Battery", 7),
    ("Battery Bank", 7),
    ("Installation Service", 8),
    ("Residential Installation", 8),
    ("Commercial Installation", 8),
    ("Maintenance", 9),
    ("Panel Cleaning", 9),
    ("System Check-up", 9),
    ("Repair", 9),
    ("Electronic Appliance", 10),
    ("Lighting Fixture", 11),
    ("Bulb", 11),
    ("LED", 11),
    ("Lamp", 11),
    ("Tube Light", 11),
    ("Power Tool", 12),
    ("Drill", 12),
    ("Saw", 12),
    ("Sander", 12),
    ("Heating Device", 13),
    ("Electric Heater", 13),
    ("Water Heater", 13),
    ("Fan", 14),
    ("Ceiling Fan", 14),
    ("Table Fan", 14),
    ("Exhaust Fan", 14),
    ("Electric Switch", 15),
    ("Socket", 15),
    ("Switchboard", 15),
    ("Extension Cord", 15),
    ("Surge Protector", 15),
    ("Rechargeable Battery", 16),
    ("Standard Battery", 16),
    ("Cooking Appliance", 17),
    ("Oven", 17),
    ("Stove", 17),
    ("Microwave Oven", 17),
    ("Food Preparation", 18),
    ("Blender", 18),
    ("Food Processor", 18),
    ("Mixer", 18),
    ("Cleaning", 19),
    ("Dishwasher", 19),
    ("Garbage Disposal", 19),
    ("Induction Cooker", 20),
    ("Food Preparation Equipment", 20),
    ("Storage", 21),
    ("Refrigerator", 21),
    ("Freezer", 21),
    ("Small Appliance", 22),
    ("Toaster", 22),
    ("Electric Kettle", 22),
    ("Coffee Maker", 22),
    ("Gas Stove", 23),
    ("Burner", 23),
    ("Climate Control", 24),
    ("Air Conditioner", 24),
    ("Heater", 24),
    ("Humidifier", 24),
    ("Dehumidifier", 24),
    ("Cleaning Appliance", 25),
    ("Vacuum Cleaner", 25),
    ("Steam Mop", 25),
    ("Robotic Cleaner", 25),
    ("Laundry", 26),
    ("Washing Machine", 26),
    ("Dryer", 26),
    ("Iron", 26),
    ("Entertainment", 27),
    ("Television", 27),
    ("Home Theater System", 27),
    ("Speaker", 27),
    ("Installation", 28),
    ("Pipe Installation", 28),
    ("Water Heater Installation", 28),
    ("Repair", 29),
    ("Leak Repair", 29),
    ("Blockage Clearing", 29),
    ("Pipe Replacement", 29),
    ("Maintenance", 30),
    ("Regular Check-up", 30),
    ("Cleaning Service", 30),
    ("Emergency Service", 31),
    ("Burst Pipe", 31),
    ("Major Leak", 31),
    ("Sewer Issue", 31),
    ("Comprehensive Diagnostics", 32),
    ("laptop", 32),
    ("computer", 32),
    ("pc", 32),
    ("Detailed System Check", 32),
    ("laptop", 33),
    ("computer", 33),
    ("pc", 33),
    ("Hardware Repair", 33),
    ("Component Replacement", 33),
    ("laptop", 34),
    ("computer", 34),
    ("pc", 34),
    ("Software Optimization", 34),
    ("Speed Up", 34),
    ("Secure System", 34),
    ("laptop", 35),
    ("computer", 35),
    ("pc", 35),
    ("Data Recovery", 35),
    ("Lost File Recovery", 35),
    ("laptop", 36),
    ("computer", 36),
    ("pc", 36),
    ("Virus Removal", 36),
    ("Malware Removal", 36),
    ("CCTV Installation", 37),
    ("Camera Setup", 37),
    ("System Configuration", 38),
    ("Camera Configuration", 38),
    ("Routine Maintenance", 39),
    ("System Check", 39),
    ("Emergency Repair", 40),
    ("Fix Solution", 40),
    ("Upgrades and Expansions", 41),
    ("Smart Lighting", 42),
    ("Automated Fan", 43),
    ("Automatic Gate", 44),
    ("Smart Plug", 45),
    ("Ride-On Car", 46),
    ("Motion Toy", 47),
    ("Outdoor Equipment", 49),
    ("Lawn Mower", 49),
    ("Trimmer", 49),
    ("Garden Tool", 49),
    ("Personal Care Appliance", 50),
    ("Hair Dryer", 50),
    ("Electric Shaver", 50),
    ("Massager", 50),
    ("Fitness Equipment", 51),
    ("Treadmill", 51),
    ("Exercise Bike", 51),
    ("Dumbbell", 51),
    ("Smart Home Device", 52),
    ("Smart Speaker", 52),
    ("Smart Plug", 52),
    ("Office Supply", 53),
    ("Printer", 53),
    ("Scanner", 53),
]
    
for keyword, category_id in keywords_with_categories:
    trie.insert(keyword, category_id)

# Serialize the Trie to a file
with open('trie_data.json', 'w') as f:
    f.write(trie.serialize())
