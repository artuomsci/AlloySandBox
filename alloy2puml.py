import re
from typing import List, Dict

class AlloyToPlantUMLConverter:
    def __init__(self):
        self.multiplicity_map = {
            'some': '1..*',
            'one': '1',
            'lone': '0..1',
            'set': '0..*'
        }
    
    def convert(self, alloy_code: str) -> str:
        plantuml = ['@startuml']
        
        # Extract signatures with fields and inheritance
        signatures = self._parse_signatures(alloy_code)
        for sig in signatures:
            plantuml.append(f'class {sig["name"]} {{}}')
            if sig['extends']:
                plantuml.append(f'{sig["name"]} --|> {sig["extends"]}')
            
            for field in sig['fields']:
                multiplicity = self.multiplicity_map.get(field['mult'], '')
                plantuml.append(
                    f'{sig["name"]} "{multiplicity}" *-- "{self._get_target_mult(field)}" {field["type"]}'
                )
        
        # Constraints intentionally omitted per user request
        
        plantuml.append('@enduml')
        return '\n'.join(plantuml)
    
    def _parse_signatures(self, code: str) -> List[Dict]:
        pattern = r'sig\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{([^}]*)\}'
        signatures = []
        
        for match in re.finditer(pattern, code, re.DOTALL):
            name, extends, fields = match.groups()
            fields = self._parse_fields(fields.strip())
            signatures.append({
                'name': name,
                'extends': extends,
                'fields': fields
            })
        return signatures
    
    def _parse_fields(self, fields_str: str) -> List[Dict]:
        field_pattern = r'(\w+)\s*:\s*(\w+)\s+(\w+)'
        return [
            {'name': m[0], 'mult': m[1], 'type': m[2]}
            for m in re.findall(field_pattern, fields_str)
        ]
    
    def _get_target_mult(self, field: Dict) -> str:
        return self.multiplicity_map.get(field['mult'], '')
    
    def _parse_constraints(self, code: str) -> List[str]:
        fact_pattern = r'fact\s+(\w+)\s*\{(.+?)\}'
        constraints = []
        for match in re.finditer(fact_pattern, code, re.DOTALL):
            name, body = match.groups()
            cleaned = ' '.join(body.strip().split())
            constraints.append(f'{name}: {cleaned}')
        return constraints

if __name__ == '__main__':
    import sys
    import os
    import glob
    
    if len(sys.argv) != 2:
        print("Usage: python alloy2puml.py <input_dir>")
        print("  Processes all *.als files in the directory")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    if not os.path.isdir(input_dir):
        print(f"Error: {input_dir} is not a valid directory")
        sys.exit(1)
        
    converter = AlloyToPlantUMLConverter()
    combined = ['@startuml']
    
    for input_path in glob.glob(os.path.join(input_dir, '*.als')):
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                uml = converter.convert(f.read())
                # Remove individual start/end tags and add to combined
                combined.extend(line for line in uml.split('\n')
                              if not line.startswith(('@startuml', '@enduml')))
                combined.append('')  # Add spacing between files
        except Exception as e:
            print(f"Error processing {input_path}: {str(e)}")
    
    combined.append('@enduml')
    output_path = os.path.join(input_dir, 'combined.puml')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(combined))
    print(f"Generated combined diagram: {output_path}")