# **AI-Powered Brain MRI Enhancement, Classification & Diagnostic Assistance**

### **Comprehensive README **

## **📌 Project Title:**

**A Deep Learning–Based End-to-End System for Brain MRI Enhancement, Tumor Classification & Clinical Decision Support**

---

# **1. Introduction**

Brain tumors such as **glioma, meningioma, and pituitary adenomas** require timely and accurate diagnosis. Manual MRI interpretation is time-consuming and highly dependent on radiologist expertise.
This project presents an **end-to-end automated pipeline** that:

* Enhances MRI scans using deep learning-based image restoration models.
* Classifies tumor type using a state-of-the-art convolutional neural network.
* Provides an intuitive **Gradio web interface** for clinicians and students.
* Offers a unified workflow combining **enhancement → classification → visualization**.

The project is based on a series of chapters (1–6) from the research documentation, along with multiple modeling Jupyter notebooks and a runnable web application.

---

# **2. Project Objectives**

### **Primary Objectives**

1. Enhance Medical Images – Improve the quality of medical scans by reducing noise, motion artifacts, and poor contrast to make them clearer and easier to interpret. 

2. Detect Abnormalities Accurately – Use deep learning models to identify potential issues such as tumours or lesions with high precision and reliability. 

3. Provide Explainable AI Results – Integrate explainable AI (XAI) techniques to highlight the exact regions of a scan influencing predictions, building trust and transparency for doctors. 

4. Improve Accessibility and Patient Understanding – Provide a platform through web and mobile applications that not only makes the system widely accessible but also presents results in simple language and visual highlights so even people without medical knowledge can understand their reports. 

---

# **3. Literature Review Summary**

* Traditional machine learning approaches required **hand-crafted features**, leading to inconsistent performance.
* Deep CNN-based approaches significantly improved classification due to automatic feature extraction.
* Image enhancement prior to classification is shown to **increase diagnostic interpretability** and reduce noise-induced errors.
* EfficientNet architectures outperform predecessors due to compound scaling and optimized parameter efficiency.
* Studies highlight the need for **explainability, robustness, and clinician-friendly interfaces** — all addressed in this system.

---

# **4. System Architecture**

## **4.1 Pipeline Overview**

```
MRI Image → Enhancement Module → Classifier → Prediction + Confidence → User Interface
```

## **4.2 Enhancement Models Implemented**

| Model     | Purpose                | Strengths                | Notes                   |
| --------- | ---------------------- | ------------------------ | ----------------------- |
| **DnCNN** | Denoising              | Removes Gaussian noise   | Fast, light-weight      |
| **EDSR**  | Super-resolution       | Recovers fine structures | Deeper model            |
| **U-Net** | Structural restoration | Best SSIM & PSNR         | Selected as final model |

### **Performance (from Chapter 4 & 5)**

* **U-Net SSIM:** ~0.90
* **U-Net PSNR:** ~32.45 dB
* Chosen as the **primary enhancement model**.

---

## **4.3 Classification Models Evaluated**

The following models were trained and compared (Jupyter notebooks included):

| Model               | Type                     | Notes                     |
| ------------------- | ------------------------ | ------------------------- |
| Simple CNN          | Baseline                 | Good for comparison       |
| **VGG16**           | Transfer Learning        | High accuracy but heavier |
| **ResNet50**        | Deep residual network    | Good generalization       |
| **Xception**        | Depthwise separable conv | Faster training           |
| **EfficientNet-B4** | Compound scaling         | **Best performance**      |

### **Champion Model: EfficientNet-B4**

* Input resolution: **380×380**
* Used **staged training**:

  * Train classifier head
  * Fine-tune entire network
* Optimizer: **Adam**
* LR scheduling + callback support

---

## **4.4 Dataset & Splits**

* Dataset: Brain Tumor Classification dataset (4 classes)
* Preprocessed into 4 folders:

  ```
  glioma/
  meningioma/
  pituitary/
  no_tumor/
  ```
* **Split ratio** (document-confirmed):

  * **70% Train**
  * **20% Validation**
  * **10% Test**

Dataset augmentation included flips, rotations, zooming, and brightness shifts to improve generalization.

---

# **5. Model Performance**

(*Aggregated from Chapter 4 & 5 + notebooks*)

## **5.1 Classification Results (EfficientNet-B4)**

| Metric        | Score                   |
| ------------- | ----------------------- |
| **Accuracy**  | **≈ 98.17%**            |
| **Precision** | High across all classes |
| **Recall**    | ~99% for No-Tumor       |
| **AUC**       | ~0.999 (macro)          |

### **Confusion Matrix Highlights**

* Extremely low misclassification rates
* No-Tumor and Pituitary classes show strongest confidence

---

## **5.2 Enhancement Model Results**

| Model     | SSIM       | PSNR (dB)       |
| --------- | ---------- | --------------- |
| **U-Net** | **0.9066** | **32.45**       |
| DnCNN     | 0.80–0.85  | Lower           |
| EDSR      | 0.88       | Good but slower |

U-Net consistently outperformed others in structure preservation — crucial for tumor boundary clarity.

---

# **6. Web Application (Gradio App)**

(*from gradio_app.py*)

### **Features**

* Upload MRI image
* Automatic resizing & preprocessing
* Model-based classification
* Clean, styled UI with:

  * Prediction label
  * Probability bars
  * Enhanced image preview
  * Error-handling & model-loading fallback

### **Run the app**

```bash
python gradio_app.py
```

### **Model Loading Logic**

The script **auto-detects**:

* `efficientnetb4_best.h5`
* or
* `efficientnetb4_best.keras`

If not found → instructs user to place model file in root directory.

---

# **7. Evaluation & Testing Strategy**

(*Chapter 4*)

### **Testing Stages**

1. **Unit testing** of enhancement and classification modules
2. **Integration testing** (pipeline correctness using 50 random images)
3. **Performance testing** using:

   * PSNR
   * SSIM
   * Accuracy/F1/AUC
4. **Stress testing**:

   * Noisy images
   * Low resolution inputs
   * Rotated and off-center scans

### **Pipeline Stability**

* ~100% correct on curated integration test set
* Average inference time ~2.8 seconds per image (CPU-based prototype)

---

# **8. System Deployment**

(*Chapter 6*)

### **Prototype Deployment**

* Local Gradio web application
* Suitable for demonstration, academic submission, and preliminary clinical testing

### **Planned Production Deployment**

* Integrate with **FastAPI REST services**
* Dockerized service
* Add **DICOM support**
* Hospital PACS integration
* End-to-end secure authentication
* Cloud GPU hosting for real-time inference

---

# **9. Limitations**

(*Chapter 6*)

* Works on **2D MRI slices**, not full 3D volumes
* Limited dataset diversity (scanner variability not tested thoroughly)
* No built-in **explainability** yet (Grad-CAM planned)
* Not a replacement for radiological diagnosis — clinical validation required

---

# **10. Future Enhancements**

(*from project conclusion*)

* Upgrade to **3D U-Net / nnU-Net** for volumetric segmentation
* Adopt **Vision-Language Models (VLMs)** for automated radiology report generation
* Integrate **Grad-CAM++** visual explanations
* Domain adaptation for low-field MRI scanners
* Deploy as full-stack medical imaging system with patient history integration
* Add **auto-triaging system** using severity estimation models

---

# **11. Repository Structure**

```
project/
│
├── Chapter1.pdf   → Introduction, problem statement
├── Chapter2.pdf   → Literature survey
├── Chapter3.pdf   → System design, methodology
├── Chapter4.pdf   → Testing & evaluation
├── Chapter5.pdf   → Results & screenshots
├── Chapter6.pdf   → Conclusions & future scope
│
├── gradio_app.py  → Web UI & inference code
├── enhancement_models.ipynb → DnCNN, EDSR, U-Net
├── VGG16.ipynb
├── ResNet50.ipynb
├── Xception.ipynb
├── CNN_classification.ipynb
└── efficientnet_b4.ipynb (implied)
```

---

# **12. How to Use the System**

### **Install dependencies**

```bash
pip install -r requirements.txt
```

### **Run enhancement or classifier notebooks**

Open Jupyter Lab or Colab; each notebook is plug-and-play.

### **Run the complete system via Gradio**

```bash
python gradio_app.py
```

### **Provide your own MRI dataset**

Place your images in folders matching:

```
glioma/
meningioma/
pituitary/
no_tumor/
```

---

# **13. Credits**

This project aggregates work from:

* Research documentation (Chapter 1–6)
* Model training notebooks
* Preprocessing and enhancement experiments
* EfficientNet-B4 classification module
* Gradio web interface implementation

All development, experimentation, and system integration was performed as part of a comprehensive academic/engineering project.

---

# **14. License**

Choose your preferred license (MIT recommended for open-source academic projects).


