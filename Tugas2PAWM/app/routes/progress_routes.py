from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from app import mongo  
from bson.objectid import ObjectId

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/save', methods=['POST'])
@login_required
def save_progress():
    data = request.get_json()
    users_collection = mongo.db.users
    
    # Update the user's state in MongoDB with progress, simulation results, and additional info
    update_data = {
        "progress": data.get("progress"),  # e.g., 50% completion
        "simulationResults": data.get("simulationResults", []),  # Array of results or scores
        "additionalInfo": data.get("additionalInfo", {})  # Any other relevant info
    }

    result = users_collection.update_one(
        {"_id": ObjectId(current_user.id)},  # Convert to ObjectId
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        return jsonify({"error": "No changes made or user not found"}), 404
    
    return jsonify({"message": "Progress saved successfully"}), 200

@progress_bp.route('/get', methods=['GET'])
@login_required
def get_progress():
    users_collection = mongo.db.users
    print(f"Current User ID: {current_user.id}")

    # Convert current_user.id back to ObjectId for the query
    user = users_collection.find_one({"_id": ObjectId(current_user.id)})

    if user:
        print("User  found:", user)
        return jsonify({
            "progress": user.get("progress", 0),
            "simulationResults": user.get("simulationResults", []),
            "additionalInfo": user.get("additionalInfo", {})
        }), 200
    else:
        # Debugging print if user not found
        print("User  not found.")
        return jsonify({"error": "User  not found"}), 404