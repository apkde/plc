from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyC98GzPh68efA5RuV9NM6V48ohRQvj6LdI"  # Replace with your actual API key
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.get_json()
        source_code = data.get('code', '')
        direction = data.get('direction', '')

        if direction == "st_to_ladder":
            prompt = f"""As a PLC programmer, analyze this requirement and create a ladder diagram:
            {source_code}

            Create a ladder diagram following these rules:
            1. Use proper PLC addressing:
               - Inputs: X0.0, X0.1, etc.
               - Outputs: Y0.0, Y0.1, etc.
               - Internal bits: M0.0, M0.1, etc.
            2. Include proper descriptions and comments
            3. Format each rung exactly like this:

            (* Main Control Logic *)
            Rung 001 - [Description]
            |----[NAME1]----[NAME2]----[NAME3]----[NAME4]----[NAME5]----|
            |     X0.0      X0.1      M0.0      M0.1      Y0.0       |

            4. Use standard contact symbols:
               - ----[ ]---- for NO contacts
               - ----[/]---- for NC contacts
               - ----(  )---- for output coils
               - ----(S)---- for SET coils
               - ----(R)---- for RESET coils
            5. Keep each rung on exactly two lines
            6. Include proper power rails and connections
            7. Add necessary safety interlocks

            Generate a complete ladder program that implements this functionality."""

            response = model.generate_content(prompt)
            converted_code = response.text.strip()
            
            return jsonify({
                'success': True,
                'converted_code': converted_code
            })
            
        elif direction == "ladder_to_st":
            prompt = f"""Convert this ladder diagram to Structured Text (ST) code:
            {source_code}

            Follow these rules:
            1. Use IEC 61131-3 syntax
            2. Include variable declarations
            3. Use proper addressing
            4. Add comments for clarity
            5. Format code properly
            
            Generate complete ST code."""

            response = model.generate_content(prompt)
            converted_code = response.text.strip()
            
            return jsonify({
                'success': True,
                'converted_code': converted_code
            })
        
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid conversion direction'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/export', methods=['POST'])
def export():
    try:
        data = request.get_json()
        source_code = data.get('source_code', '')
        converted_code = data.get('converted_code', '')
        export_type = data.get('type', '')

        os.makedirs('exports', exist_ok=True)

        if export_type == 'tia':
            with open('exports/tia_export.scl', 'w') as f:
                f.write(converted_code)
            filename = 'tia_export.scl'
        else:
            xml_content = f"""<?xml version="1.0" encoding="utf-8"?>
<pou xmlns="http://www.plcopen.org/xml/tc6_0200">
    <body>
        <ST>{converted_code}</ST>
    </body>
</pou>"""
            with open('exports/somachine_export.xml', 'w') as f:
                f.write(xml_content)
            filename = 'somachine_export.xml'

        return jsonify({
            'success': True,
            'filename': filename
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)