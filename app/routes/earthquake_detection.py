from flask import Blueprint, request, jsonify
import torch
from PIL import Image
from app.models.crack_classifier import CrackClassifier, inference_transforms, device, model, CLASS_LABELS  # your model file path

earthquake_bp = Blueprint("earthquake", __name__)

@earthquake_bp.route('/api/detect-earthquake', methods=['POST'])
def detect_earthquake_route():
    if 'image' not in request.files:
        return jsonify({"error": "Image file missing"}), 400
    
    image_file = request.files['image']
    return e_detect_earthquake(image_file)

def e_detect_earthquake(image_file):
    try:
        img = Image.open(image_file).convert("RGB")
        img_tensor = inference_transforms(img).to(device)
        with torch.no_grad():
            output = model(img_tensor.unsqueeze(0))
        probabilities = torch.softmax(output, dim=1).squeeze().tolist()
        max_prob_idx = int(torch.argmax(output, dim=1).item())

        result = {
            "predicted_class": CLASS_LABELS[max_prob_idx], 
            "confidence": round(probabilities[max_prob_idx]*100, 2),  # percentage
            "probabilities": {CLASS_LABELS[i]: round(p*100, 2) for i, p in enumerate(probabilities)}
        }
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
