from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from app import mongo
from bson.objectid import ObjectId
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/save', methods=['POST'])
@login_required
def save_progress():
    data = request.get_json()
    users_collection = mongo.db.users
    
    # Prepare the data to update
    update_data = {
        "progress": data.get("progress"),  # For example, 50% completion
        "simulationResults": data.get("simulationResults", []),  # Array of results or scores
        "additionalInfo": data.get("additionalInfo", {})  # Other relevant info
    }
    
    # Perform the update operation
    try:
        result = users_collection.update_one(
            {"_id": ObjectId(current_user.id)},  # Convert to ObjectId
            {"$set": update_data}
        )
    except Exception as e:
        logging.error(f"Error updating user progress: {e}")
        return jsonify({"error": "Error saving progress to the database"}), 500

    if result.modified_count == 0:
        return jsonify({"error": "No changes made or user not found"}), 404

    return jsonify({"message": "Progress saved successfully"}), 200

@progress_bp.route('/get', methods=['GET'])
@login_required
def get_progress():
    users_collection = mongo.db.users
    logging.info(f"Fetching progress for user ID: {current_user.id}")

    try:
        # Fetch the user data from MongoDB
        user = users_collection.find_one({"_id": ObjectId(current_user.id)})

        if user:
            logging.info(f"User found: {user}")
            return jsonify({
                "progress": user.get("progress", 0),
                "simulationResults": user.get("simulationResults", []),
                "additionalInfo": user.get("additionalInfo", {})
            }), 200
        else:
            logging.warning("User not found.")
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        logging.error(f"Error retrieving user progress: {e}")
        return jsonify({"error": "An error occurred while retrieving progress"}), 500
