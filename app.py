from flask import Flask, jsonify, request, render_template
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector
from mysql.connector import Error
app = Flask(__name__)
app.json.sort_keys = False
ma = Marshmallow(app)
class ClientSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone= fields.String(required=True)
    class Meta:
        fields = ("name", "email", "phone", "client_id")
client_schema = ClientSchema()
clients_schema = ClientSchema(many=True)
db_name = "fitness_"
user = "root"
password = ""
host = "localhost"
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            database=db_name,
            user=user,
            password=password,
            host=host
        )
        if conn.is_connected():
            print("Connected to db succesfully (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧")
            return conn        
    except Error as e:
        print(f"Error: {e}")
        return None
@app.route("/")
def home():
    message = "Hello World"
    return render_template("index.html", message=message)
@app.route('/clients', methods=["POST"])
def add_client():
    client_data = client_schema.load(request.json)
    print(client_data)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    name = client_data['name']
    email = client_data['email']    
    phone = client_data['phone']
    new_client = (name, email, phone)
    print(new_client)
    query = "INSERT INTO Clients(name, email, phone) VALUES (%s, %s, %s)"
    cursor.execute(query, new_client)
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "New client was added succesfully"}), 201
@app.route("/clients", methods = ["GET"]) 
def get_clients():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM Clients"
    cursor.execute(query)
    clients = cursor.fetchall()
    print(clients)
    cursor.close()
    conn.close()
    return clients_schema.jsonify(clients)
@app.route("/clients/<int:id>", methods=["PUT"])
def update_client(id):
    try: 
        client_data = client_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400     
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        name = client_data['name']
        email = client_data["email"]
        phone = client_data["phone"]
        query = "UPDATE Clients SET name = %s, email = %s, phone = %s WHERE client_id = %s"
        updated_client = (name, email, phone, id)
        cursor.execute(query, updated_client)
        conn.commit()
        return jsonify({"message": "Customer details updated successfully"}), 200 
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"message": "Internal Server Error"}), 500  
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
@app.route("/clients/<int:id>", methods=["DELETE"])
def delete_client(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500 
        cursor = conn.cursor()
        client_to_remove = (id,)
        query = "SELECT * FROM Clients WHERE client_id = %s"
        cursor.execute(query, client_to_remove)
        client = cursor.fetchone()
        if not client:
            return jsonify({"message": "Client not found"}), 404 
        query = "SELECT * FROM WorkoutSessions WHERE client_id = %s"
        cursor.execute(query, client_to_remove)
        WorkoutSessions = cursor.fetchall()
        if WorkoutSessions:
            return jsonify({"message": "Client has associated workouts, cannot delete"}), 400 
        query = "DELETE FROM Clients WHERE client_id = %s"
        cursor.execute(query, client_to_remove)
        conn.commit()
        return jsonify({"message": "Customer Removed Successfully"}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
class WorkoutSessionsSchema(ma.Schema):
    client_id = fields.Int(required=True)
    date = fields.Date(required=True)
    workout = fields.String(required=True)
    sets = fields.Int(required=True)
    reps = fields.Int(required=True)
    WeightUsed = fields.Int(required=True)
    AboutWorkout= fields.String(required=True)
    class Meta:
        fields = ("workout_id", "client_id", "date", "workout", "sets", "reps", "WeightUsed", "AboutWorkout")  
workoutsession_schema = WorkoutSessionsSchema()
workoutsessions_schema = WorkoutSessionsSchema(many=True)  
@app.route("/workouts", methods=["POST"])
def add_workout():
    try:
        workout_data = workoutsession_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        query = "INSERT INTO WorkoutSessions (client_id, date, workout, sets, reps, WeightUsed, AboutWorkout) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (workout_data['client_id'], workout_data['date'], workout_data['workout'], workout_data['sets'], workout_data['reps'], workout_data['WeightUsed'], workout_data['AboutWorkout']))
        conn.commit()
        return jsonify({"message": "Workout added successfully"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
@app.route("/workouts", methods = ["GET"])
def get_workouts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 
    query = "SELECT * FROM WorkoutSessions"
    cursor.execute(query)
    workouts = cursor.fetchall()
    print(workouts)
    cursor.close()
    conn.close()
    return workoutsessions_schema.jsonify(workouts)   
@app.route("/workouts/<int:id>", methods=["PUT"])
def update_workouts(id):
    try: 
        workout_data = workoutsession_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400 
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500 
        cursor = conn.cursor()
        date = workout_data['date']
        workout = workout_data["workout"]
        sets = workout_data["sets"]
        reps = workout_data['reps']
        WeightUsed = workout_data["WeightUsed"]
        AboutWorkout = workout_data["AboutWorkout"]
        query = "UPDATE WorkoutSessions SET date = %s, workout = %s, sets = %s, reps = %s, WeightUsed = %s, AboutWorkout = %s WHERE workout_id = %s"
        updated_workout = (date, workout, sets, reps, WeightUsed, AboutWorkout, id)
        cursor.execute(query, updated_workout)
        conn.commit()
        return jsonify({"message": "Workout details updated successfully"}), 200 
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"message": "Internal Server Error"}), 500 
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
if __name__ == "__main__":
    app.run(debug=True)