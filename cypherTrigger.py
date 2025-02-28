from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    filename="app.log",  # Log file name
    level=logging.INFO,  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)

# Create a logger instance
logger = logging.getLogger(__name__)

@app.route('/log', methods=['POST'])
def log_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'})
        
        logger.info(f"Received data: {data}")
        return jsonify({'message': 'Data logged successfully'})
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
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



CALL apoc.trigger.install('neo4j', 'onRelationshipPrint',
  "
    UNWIND $createdRelationships AS r
    WITH r
    WHERE r:FRIEND
    WITH apoc.convert.toJson(r) AS value
    WITH 'http://127.0.0.1:8000/log' AS url,
     {method: 'POST',`Content-Type`: 'application/json'} AS headers,
     value AS payload

    CALL apoc.load.jsonParams(url, headers, payload) YIELD value
    RETURN value
  ",
  {phase: 'afterAsync'}
);

CALL apoc.trigger.drop('neo4j', 'onDeleteRelationshipPrint')


WITH range(1, 1000) AS ids, 
     ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hannah", "Ivy", "Jack"] AS names, 
     ["Red", "Blue", "Green", "Yellow", "Purple", "Orange", "Pink", "Brown", "Black", "White"] AS colors

UNWIND ids AS id
CREATE (:Person { 
    Pid: id, 
    name: names[toInteger(rand() * size(names))], 
    favoriteColor: colors[toInteger(rand() * size(colors))]
});


MATCH (p1:Person), (p2:Person) 
WHERE p1.Pid <> p2.Pid // Ensure a person doesn't befriend themselves
WITH p1, p2, rand() AS r
ORDER BY r // Randomize the pairs
LIMIT 2000
CREATE (p1)-[:FRIEND {friendshipStrength: toInteger(rand() * 10) + 1}]->(p2);

    """
