from flask import Flask, jsonify, request
import xmltodict
import json

'''
start with:
python .\cmi-config-rest-api.py


Nach was soll gesucht werden können?
- namefull           mandant/nameFull
- nameshort          mandant/nameShort
- installid          mandant/installId
- dbname             mandant/[prod or test]/db/name
- applizenzserver    mandant/[prod or test]/app/lizenzserver
- owinmandant        mandant/[prod or test]/owinServer_relay/mandant

zusätzlich Filter für prod/test (?)

Was für Felder von mandant sollen zurückgegeben werden?
- namefull                mandant/nameFull
- nameshort               mandant/nameShort
- installid               mandant/installId
- dbserver                mandant/[prod or test]/db/server
- dbname                  mandant/[prod or test]/db/name
- appserver               mandant/[prod or test]/app/server
- appinstallpathroot      mandant/[prod or test]/app/installPathRoot
- appuser                 mandant/[prod or test]/app/user
- applizenzserver         mandant/[prod or test]/app/lizenzserver
- ......



caddy for reverse proxy:
- download and install caddy
- caddy.exe run ---> create windows service
- caddyfile:
:80 {
    reverse_proxy /api/data localhost:8088
}
- caddy.exe reload


endpoint example:
http://your-server-ip/api/data?nameFull=Bedarfmanagement&server=ziaxiomapsql02

'''

app = Flask(__name__)

# Load XML data from file and parse it to a dictionary
def load_xml_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        xml_data = file.read()
    return xmltodict.parse(xml_data)

# Load data initially
xml_data_path = 'C:\DBA-Scripts\cmi-config-rest-api\cmi-mandanten-config.xml'  # Path to your XML file
xml_data = load_xml_data(xml_data_path)

# Endpoint to fetch XML data with optional filters
@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        # Reload XML data each time to ensure up-to-date info
        data = load_xml_data(xml_data_path)
        mandanten = data['mandanten']['mandant']
        
        # Ensure mandanten is a list to handle both single and multiple mandant entries
        if not isinstance(mandanten, list):
            mandanten = [mandanten]
            
        # Apply filters based on query parameters
        filters = request.args
        if filters:
            for key, value in filters.items():
                if key != 'return_value': # Only apply filters, exclude `return_value`
                    mandanten = [
                        m for m in mandanten
                        if (m.get(key) and m[key] == value) or # for first level filters, like nameFull, nameShort, installId
                        (key == 'prod_db_name' and m['prod']['db']['name'] == value) or
                        (key == 'test_db_name' and m['test']['db']['name'] == value) or
                        (key == 'prod_app_lizenzserver' and m['prod']['app']['lizenzserver'] == value) or
                        (key == 'test_app_lizenzserver' and m['test']['app']['lizenzserver'] == value) or
                        (key == 'prod_owinServer_relay' and m['prod']['owinServer']['relay'] == value) or
                        (key == 'test_owinServer_relay' and m['test']['owinServer']['relay'] == value)
                    ]

        # Extract the requested field if `return_value` is specified
        return_value = request.args.get('return_value')
        if return_value:
            # Map return_value to the appropriate path in the nested structure
            value_map = {
                'nameFull': lambda m: m['nameFull'],
                'prod_db_server': lambda m: m['prod']['db']['server'],
                'test_db_server': lambda m: m['test']['db']['server'],
                'prod_db_name': lambda m: m['prod']['db']['name'],
                'test_db_name': lambda m: m['test']['db']['name'],
                'prod_app_server': lambda m: m['prod']['app']['server'],
                'test_app_server': lambda m: m['test']['app']['server'],
                'prod_app_installPathRoot': lambda m: m['prod']['app']['installPathRoot'],
                'test_app_installPathRoot': lambda m: m['test']['app']['installPathRoot'],
                'prod_app_user': lambda m: m['prod']['app']['user'],
                'test_app_user': lambda m: m['test']['app']['user'],
                'prod_app_lizenzserver': lambda m: m['prod']['app']['lizenzserver'],
                'test_app_lizenzserver': lambda m: m['test']['app']['lizenzserver'],
                'prod_sts_v3': lambda m: m['prod']['sts']['v3'],
                'test_sts_v3': lambda m: m['test']['sts']['v3'],
                'prod_objektLoader_port': lambda m: m['prod']['objektLoader']['port'],
                'test_objektLoader_port': lambda m: m['test']['objektLoader']['port'],
            }

            # Only return the specified field for each matching mandant
            mandanten = [
                {return_value: value_map[return_value](m)} for m in mandanten if return_value in value_map
            ]

        return jsonify(mandanten)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8088)
