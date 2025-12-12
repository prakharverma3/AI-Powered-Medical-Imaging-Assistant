"""
Brain MRI Tumor Classification Web App
Uses EfficientNetB4 model trained on brain MRI scans
Simple copy-paste solution - just run: python gradio_app.py
"""

import gradio as gr
import numpy as np
from PIL import Image
import os

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

# Ensure TensorFlow uses CPU if GPU fails
try:
    physical_devices = tf.config.list_physical_devices('GPU')
    if len(physical_devices) > 0:
        tf.config.experimental.set_memory_growth(physical_devices[0], True)
except:
    pass

# Configuration
MODEL_PATHS = [
    "efficientnetb4_best.h5",
    "efficientnetb4_best.keras"
]
IMG_SIZE = (380, 380)
CLASS_NAMES = ['glioma', 'meningioma', 'notumor', 'pituitary']

# Load the trained model
print("="*70)
print("🧠 BRAIN MRI TUMOR CLASSIFICATION - LOADING...")
print("="*70)

model = None
for MODEL_PATH in MODEL_PATHS:
    if os.path.exists(MODEL_PATH):
        try:
            model = tf.keras.models.load_model(MODEL_PATH, compile=False)
            print(f"✓ Model loaded successfully from: {MODEL_PATH}")
            print(f"✓ Input shape: {model.input_shape}")
            print(f"✓ Output classes: {len(CLASS_NAMES)}")
            break
        except Exception as e:
            print(f"✗ Failed to load {MODEL_PATH}: {str(e)[:100]}")
            continue

if model is None:
    print("\n" + "="*70)
    print("⚠️  MODEL NOT FOUND!")
    print("="*70)
    print("Please ensure you have the model file in this folder:")
    print("  • efficientnetb4_best.h5  (preferred)")
    print("  • efficientnetb4_best.keras  (alternative)")
    print("\nTo get the model:")
    print("1. Go to your Google Colab")
    print("2. Run: model.save('efficientnetb4_best.h5')")
    print("3. Download and place it in this folder")
    print("="*70)

def preprocess_image(image):
    """Preprocess the input image to match training preprocessing"""
    if not isinstance(image, Image.Image):
        image = Image.fromarray(image.astype('uint8'), 'RGB')
    
    image = image.resize(IMG_SIZE, Image.BILINEAR)
    img_array = np.array(image)
    
    if img_array.ndim == 2:
        img_array = np.stack([img_array] * 3, axis=-1)
    elif img_array.shape[-1] == 4:
        img_array = img_array[:, :, :3]
    
    img_array = np.expand_dims(img_array, axis=0)
    img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)
    
    return img_array

def predict(image):
    """Make prediction on the uploaded image"""
    if model is None:
        return {
            "Error": 1.0
        }, "<h3 style='color: red;'>⚠️ Model not loaded. Please check the model file.</h3>"
    
    if image is None:
        return {}, "<h3 style='color: orange;'>⚠️ Please upload an image first.</h3>"
    
    try:
        processed_img = preprocess_image(image)
        predictions = model.predict(processed_img, verbose=0)[0]
        
        confidences = {
            CLASS_NAMES[i]: float(predictions[i]) 
            for i in range(len(CLASS_NAMES))
        }
        
        top_class_idx = np.argmax(predictions)
        top_class = CLASS_NAMES[top_class_idx]
        confidence = predictions[top_class_idx] * 100
        
        # Color coding based on class
        class_colors = {
            'glioma': '#e74c3c',
            'meningioma': '#e67e22',
            'notumor': '#27ae60',
            'pituitary': '#3498db'
        }
        
        result_html = f"""
        <div style="padding: 25px; border-radius: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
            <h2 style="color: white; text-align: center; margin-bottom: 20px; font-size: 28px;">🧠 Diagnosis Result</h2>
            <div style="background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 20px; padding: 20px; background: linear-gradient(135deg, {class_colors.get(top_class, '#667eea')} 0%, {class_colors.get(top_class, '#764ba2')} 100%); border-radius: 10px;">
                    <h3 style="color: white; margin: 0; font-size: 32px; text-transform: uppercase; letter-spacing: 2px;">{top_class}</h3>
                    <p style="color: white; margin: 10px 0 0 0; font-size: 24px; font-weight: bold;">{confidence:.2f}% Confidence</p>
                </div>
                <hr style="border: 2px solid #eee; margin: 20px 0;">
                <h4 style="color: #555; margin-bottom: 15px; font-size: 18px;">📊 All Class Probabilities:</h4>
                <div style="margin-top: 15px;">
                    {''.join([f'''
                    <div style="margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <strong style="color: #333; text-transform: capitalize;">{name}</strong>
                            <span style="color: {class_colors.get(name, '#667eea')}; font-weight: bold;">{prob*100:.2f}%</span>
                        </div>
                        <div style="background: #eee; height: 8px; border-radius: 10px; overflow: hidden;">
                            <div style="background: {class_colors.get(name, '#667eea')}; height: 100%; width: {prob*100}%; transition: width 0.5s;"></div>
                        </div>
                    </div>
                    ''' for name, prob in confidences.items()])}
                </div>
            </div>
        </div>
        """
        
        return confidences, result_html
        
    except Exception as e:
        error_msg = f"<h3 style='color: red;'>⚠️ Error during prediction: {str(e)}</h3>"
        return {"Error": 1.0}, error_msg

# Custom CSS
custom_css = """
#header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 40px;
    border-radius: 20px;
    margin-bottom: 30px;
    box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
}

#header h1 {
    color: white;
    text-align: center;
    margin: 0;
    font-size: 3em;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
}

#header p {
    color: #f0f0f0;
    text-align: center;
    margin-top: 15px;
    font-size: 1.2em;
}

.gradio-container {
    max-width: 1400px !important;
    margin: auto !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

#upload_box {
    border: 3px dashed #667eea !important;
    border-radius: 20px !important;
    background: #f8f9ff !important;
    transition: all 0.3s ease;
    min-height: 400px;
}

#upload_box:hover {
    border-color: #764ba2 !important;
    background: #f0f2ff !important;
    transform: scale(1.01);
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
}

.metric-box {
    background: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    margin: 15px 0;
}

button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    color: white !important;
    font-size: 18px !important;
    font-weight: bold !important;
    padding: 15px 40px !important;
    border-radius: 10px !important;
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4) !important;
    transition: all 0.3s ease !important;
}

button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
}
"""

# Create Gradio interface
with gr.Blocks(css=custom_css, title="🧠 Brain MRI Tumor Classifier", theme=gr.themes.Soft()) as demo:
    
    gr.HTML("""
        <div id="header">
            <h1>🧠 Brain MRI Tumor Classification</h1>
            <p>Upload a brain MRI scan to classify tumor type using EfficientNetB4 Deep Learning Model</p>
        </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            input_image = gr.Image(
                label="Brain MRI Scan",
                type="numpy",
                elem_id="upload_box",
                height=400
            )
            
            predict_btn = gr.Button(
                "🔍 CLASSIFY TUMOR",
                variant="primary",
                size="lg"
            )
        
        with gr.Column(scale=1):
            output_label = gr.Label(
                label="Classification Confidence",
                num_top_classes=4
            )
            
            output_html = gr.HTML(label="Detailed Analysis")
    
    # Connect prediction
    predict_btn.click(
        fn=predict,
        inputs=input_image,
        outputs=[output_label, output_html]
    )

# Launch
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 LAUNCHING WEB APPLICATION")
    print("="*70)
    print(f"Model Status: {'✓ Loaded' if model is not None else '✗ Not Loaded'}")
    print(f"Classes: {', '.join(CLASS_NAMES)}")
    print(f"Image Size: {IMG_SIZE}")
    print("="*70 + "\n")
    
    demo.launch(
        share=False,  # Set to True for public link
        server_name="127.0.0.1",  
        server_port=7860,
        show_error=True
    )