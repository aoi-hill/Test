from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/log', methods=['POST'])
def log_data():
    print("hello")
    try:
        data = request.get_json()
        print(data,'====')
        if not data:
            return jsonify({'error': 'No data provided'})
        
        logging.info(f"Received data: {data}")
        return jsonify({'message': 'Data logged successfully'})
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({'error': 'Internal server error'})

if __name__ == '__main__':
    app.run(debug=True, port=8000)

    """
    CALL apoc.trigger.install('neo4j', 'onCreatePrint',
  "
    UNWIND $createdNodes AS n
    WITH n
    WHERE n:Person
    WITH apoc.convert.toJson(n) AS value
    WITH 'http://127.0.0.1:8000/log' AS url,
     {method: 'POST',`Content-Type`: 'application/json'} AS headers,
     value AS payload

    CALL apoc.load.jsonParams(url, headers, payload) YIELD value
    RETURN value
  ",
  {phase: 'afterAsync'}
);

    """
