################################
# * CMI Configuration REST API #
################################
# 
# PREREQUISITES
#     - install python3 (make available to all windows users)
#     - and packages: pip install Flask xmltodict (as administrator so that it's available to all users)
#     - The XML file with the CMI configuration must be present and accessible. Modify the path if nescessary.
#     - change api_port if you want to run it on a different port than 5001.
# 
# AUTHOR
#     Roger Rutishauser - DBA, October-December 2024
#
from flask import Flask, jsonify, request
import xml.etree.ElementTree as ET
app = Flask(__name__)

################### change if nescessary ###############
xml_data_path = r'D:\gitlab\cmi-config\static\cmi-config.xml'
api_port = 5001
########################################################

def load_xml_data(file_path):
    def parse_element(element):
        """Recursively parse an XML element into a dictionary, including attributes."""
        parsed_data = {}

        # Falls das Element Attribute hat, speichere sie
        if element.attrib:
            parsed_data.update(element.attrib)

        # Falls das Element Text hat, speichere es
        text = element.text.strip() if element.text else None
        if text:
            parsed_data["_text"] = text  # Optional: Falls Text enthalten ist

        # Falls das Element Kinder hat, rekursiv parsen
        if len(element) > 0:
            for child in element:
                if child.tag not in parsed_data:
                    parsed_data[child.tag] = parse_element(child)
                else:
                    if not isinstance(parsed_data[child.tag], list):
                        parsed_data[child.tag] = [parsed_data[child.tag]]
                    parsed_data[child.tag].append(parse_element(child))
        # Gib Dictionary zurück, oder wenn leer, nur Text
        return parsed_data if parsed_data else text

    tree = ET.parse(file_path)
    root = tree.getroot()
    data = {}

    for section in ['cmi', 'ais']:
        section_data = []
        section_root = root.find(section)
        if section_root is not None:
            for env in ['prod', 'test']:
                env_data = section_root.find(env)
                if env_data is not None:
                    for mandant in env_data.findall('mandant'):
                        mandant_data = {
                            'environment': env,  # Add environment info
                            'apptype': section,  # Add section info
                        }
                        # Dynamically parse all children of <mandant>
                        mandant_data.update({child.tag: parse_element(child) for child in mandant})
                        section_data.append(mandant_data)
        data[section] = section_data
    return data


def filter_data(data, filters, exact=False):
    """Filtert eine Liste von Mandanten-Dicts basierend auf Filters.
    Bei exact=True wird auf exakte Übereinstimmung geprüft, sonst Teilstring-Suche."""
    filtered = []
    for mandant in data:
        match = True
        for key, value in filters.items():
            keys = key.split('/')  # Flatten nested keys
            target = mandant
            for k in keys:
                if isinstance(target, dict) and k in target:
                    target = target[k]
                else:
                    match = False
                    break
            if not match:
                break

            # Unwrap dict mit nur _text
            if isinstance(target, dict) and '_text' in target:
                target = target['_text']
            target_str = str(target)

            if exact:
                if target_str.lower() != value.lower():
                    match = False
                    break
            else:
                if value.lower() not in target_str.lower():
                    match = False
                    break
        if match:
            filtered.append(mandant)
    return filtered

@app.route('/api/data', methods=['GET'])
def get_all_data():
    data = load_xml_data(xml_data_path)
    args = request.args.to_dict()
    exact = args.pop('exactmatch', 'false').lower() in ('1', 'true', 'yes')
    response = data['cmi'] + data['ais']
    if args:
        response = filter_data(response, args, exact=exact)
    return jsonify(response), 200

@app.route('/api/data/<section>', methods=['GET'])
def get_section_data(section):
    data = load_xml_data(xml_data_path)
    if section not in data:
        return jsonify({'error': f'Section "{section}" not found.'}), 404
    args = request.args.to_dict()
    exact = args.pop('exactmatch', 'false').lower() in ('1', 'true', 'yes')
    response = data[section]
    if args:
        response = filter_data(response, args, exact=exact)
    return jsonify(response), 200

@app.route('/api/data/<section>/<environment>', methods=['GET'])
def get_section_environment_data(section, environment):
    data = load_xml_data(xml_data_path)
    if section not in data:
        return jsonify({'error': f'Section "{section}" not found.'}), 404
    environment_data = [m for m in data[section] if m.get('environment') == environment]
    args = request.args.to_dict()
    exact = args.pop('exactmatch', 'false').lower() in ('1', 'true', 'yes')
    if args:
        environment_data = filter_data(environment_data, args, exact=exact)
    return jsonify(environment_data), 200

if __name__ == '__main__':
    app.run(port=api_port)