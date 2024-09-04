import pickle5 as pickle

QUESTIONS_2 = [
    # Mean Features
    ("Do you feel a noticeable lump in your breast?", "radius_mean", 15.5),
    ("Does the lump feel rough to the touch?", "texture_mean", 20.0),
    ("Is the lump's edge easy to feel when you touch it?", "perimeter_mean", 100.0),
    (
        "Does the lump take up a significant amount of space in your breast?",
        "area_mean",
        800.0,
    ),
    ("Does the lump feel bumpy or uneven?", "smoothness_mean", 0.10),
    ("When you press the lump, does it feel tight and firm?", "compactness_mean", 0.12),
    ("Does the lump have any inward curves or indentations?", "concavity_mean", 0.15),
    (
        "Do you notice any small dimples or dents on the lump?",
        "concave points_mean",
        0.08,
    ),
    ("Does the lump seem to have an uneven shape?", "symmetry_mean", 0.19),
    ("Does the lump have an irregular shape?", "fractal_dimension_mean", 0.07),
    # Standard Error (SE) Features
    (
        "Does the lump's size seem to change when you touch different areas?",
        "radius_se",
        0.35,
    ),
    ("Does the lump's texture feel different in some spots?", "texture_se", 1.5),
    ("Does the edge of the lump feel different in some places?", "perimeter_se", 3.0),
    ("Does the lump's size feel different when you press on it?", "area_se", 50.0),
    (
        "Does the lump's surface feel smoother in some areas and bumpier in others?",
        "smoothness_se",
        0.009,
    ),
    ("Does the lump feel more firm in some areas than others?", "compactness_se", 0.04),
    (
        "Does the lump's shape seem to curve inwards more in some spots?",
        "concavity_se",
        0.05,
    ),
    (
        "Are the small dimples or dents on the lump more noticeable in some areas?",
        "concave points_se",
        0.02,
    ),
    (
        "Does the shape of the lump seem to vary depending on where you touch it?",
        "symmetry_se",
        0.03,
    ),
    (
        "Does the lump's shape feel more complicated in some areas?",
        "fractal_dimension_se",
        0.004,
    ),
    # Worst Features
    ("Has the lump ever felt particularly large?", "radius_worst", 20.0),
    ("Has the lump ever felt rougher than usual?", "texture_worst", 30.0),
    (
        "Has the edge of the lump ever felt very distinct and easy to trace?",
        "perimeter_worst",
        120.0,
    ),
    (
        "Has the lump ever seemed to take up a lot of space in your breast?",
        "area_worst",
        1500.0,
    ),
    ("Has the lump ever felt very uneven or bumpy?", "smoothness_worst", 0.16),
    ("Has the lump ever felt particularly firm or hard?", "compactness_worst", 0.50),
    ("Has the lump ever had deep indentations or curves?", "concavity_worst", 0.60),
    (
        "Have you ever noticed a lot of small dimples or dents on the lump?",
        "concave points_worst",
        0.18,
    ),
    ("Has the lump ever felt very irregular in shape?", "symmetry_worst", 0.35),
    (
        "Has the lump ever had a very complicated or irregular shape?",
        "fractal_dimension_worst",
        0.09,
    ),
]
QUESTIONS = [
    # Mean Features
    ("Do you feel a noticeable lump in your breast?", "radius_mean", 12.0),
    ("Does the lump feel rough to the touch?", "texture_mean", 18.0),
    ("Is the lump's edge easy to feel when you touch it?", "perimeter_mean", 85.0),
    (
        "Does the lump take up a significant amount of space in your breast?",
        "area_mean",
        500.0,
    ),
    ("Does the lump feel bumpy or uneven?", "smoothness_mean", 0.1),
    ("When you press the lump, does it feel tight and firm?", "compactness_mean", 0.2),
    ("Does the lump have any inward curves or indentations?", "concavity_mean", 0.2),
    (
        "Do you notice any small dimples or dents on the lump?",
        "concave points_mean",
        0.1,
    ),
    ("Does the lump seem to have an uneven shape?", "symmetry_mean", 0.2),
    ("Does the lump have an irregular shape?", "fractal_dimension_mean", 0.06),
    # Standard Error (SE) Features
    (
        "Does the lump's size seem to change when you touch different areas?",
        "radius_se",
        0.3,
    ),
    ("Does the lump's texture feel different in some spots?", "texture_se", 0.9),
    ("Does the edge of the lump feel different in some places?", "perimeter_se", 3.0),
    ("Does the lump's size feel different when you press on it?", "area_se", 20.0),
    (
        "Does the lump's surface feel smoother in some areas and bumpier in others?",
        "smoothness_se",
        0.01,
    ),
    ("Does the lump feel more firm in some areas than others?", "compactness_se", 0.03),
    (
        "Does the lump's shape seem to curve inwards more in some spots?",
        "concavity_se",
        0.03,
    ),
    (
        "Are the small dimples or dents on the lump more noticeable in some areas?",
        "concave points_se",
        0.015,
    ),
    (
        "Does the shape of the lump seem to vary depending on where you touch it?",
        "symmetry_se",
        0.02,
    ),
    (
        "Does the lump's shape feel more complicated in some areas?",
        "fractal_dimension_se",
        0.005,
    ),
    # Worst Features
    ("Has the lump ever felt particularly large?", "radius_worst", 18.0),
    ("Has the lump ever felt rougher than usual?", "texture_worst", 25.0),
    (
        "Has the edge of the lump ever felt very distinct and easy to trace?",
        "perimeter_worst",
        120.0,
    ),
    (
        "Has the lump ever seemed to take up a lot of space in your breast?",
        "area_worst",
        800.0,
    ),
    ("Has the lump ever felt very uneven or bumpy?", "smoothness_worst", 0.15),
    ("Has the lump ever felt particularly firm or hard?", "compactness_worst", 0.25),
    ("Has the lump ever had deep indentations or curves?", "concavity_worst", 0.3),
    (
        "Have you ever noticed a lot of small dimples or dents on the lump?",
        "concave points_worst",
        0.12,
    ),
    ("Has the lump ever felt very irregular in shape?", "symmetry_worst", 0.3),
    (
        "Has the lump ever had a very complicated or irregular shape?",
        "fractal_dimension_worst",
        0.08,
    ),
]
QUESTIONS_1 = [
    (
        "Do you feel a lump in your breast?",
        "radius_mean",
        15.5,
    ),
    (
        "Do you have consistent pain in your armpit or breast?",
        "texture_mean",
        20.0,
    ),
    (
        "Do you notice any redness or pitting on your breast skin?",
        "perimeter_mean",
        100.0,
    ),
    (
        "Has the size or shape of your breast changed recently?",
        "area_mean",
        800.0,
    ),
    (
        "Do you experience nipple discharge (not breast milk)?",
        "smoothness_mean",
        0.10,
    ),
    (
        "Is your nipple inverted?",
        "compactness_mean",
        0.12,
    ),
    (
        "Do you have a rash on or around your nipple?",
        "concavity_mean",
        0.15,
    ),
    (
        "Is there swelling in your armpit or around your collarbone?",
        "concave points_mean",
        0.08,
    ),
    (
        "Have you noticed any puckering or dimpling of the breast skin?",
        "symmetry_mean",
        0.19,
    ),
    (
        "Do you feel areas of thickened tissue in your breast?",
        "fractal_dimension_mean",
        0.07,
    ),
    (
        "Do you have persistent breast skin irritation or dimpling?",
        "radius_se",
        0.35,
    ),
    (
        "Have you noticed redness or enlarged pores on your breast?",
        "texture_se",
        1.5,
    ),
    (
        "Do you feel any hardness or firmness in your breast?",
        "perimeter_se",
        3.0,
    ),
    (
        "Do you experience unusual warmth in your breast?",
        "area_se",
        50.0,
    ),
    (
        "Do you have persistent itching of your breast or nipple?",
        "smoothness_se",
        0.009,
    ),
    (
        "Have you observed any ulceration on your breast skin?",
        "compactness_se",
        0.04,
    ),
    (
        "Do you see prominent veins on your breast?",
        "concavity_se",
        0.05,
    ),
    (
        "Has your nipple changed shape or appearance?",
        "concave points_se",
        0.02,
    ),
    (
        "Do you experience peeling or flaking of your nipple skin?",
        "symmetry_se",
        0.03,
    ),
    (
        "Have you noticed any changes in the appearance of your nipple?",
        "fractal_dimension_se",
        0.004,
    ),
    (
        "Have you experienced a sudden change in your breast size?",
        "radius_worst",
        20.0,
    ),
    (
        "Do you notice asymmetry between your breasts?",
        "texture_worst",
        30.0,
    ),
    (
        "Is there swelling of your entire breast?",
        "perimeter_worst",
        120.0,
    ),
    (
        "Do you see skin changes such as puckering or dimpling?",
        "area_worst",
        1500.0,
    ),
    (
        "Do you feel thickened areas or lumps in your breast?",
        "smoothness_worst",
        0.16,
    ),
    (
        "Do you have unexplained pain or tenderness in your breast?",
        "compactness_worst",
        0.50,
    ),
    (
        "Do you feel lumps or masses in your breast tissue?",
        "concavity_worst",
        0.60,
    ),
    (
        "Do you experience nipple discharge that isn't breast milk?",
        "concave points_worst",
        0.18,
    ),
    (
        "Do you have unusual warmth or redness in your breast?",
        "symmetry_worst",
        0.35,
    ),
    (
        "Do you notice any visible veins or blood vessels on your breast?",
        "fractal_dimension_worst",
        0.09,
    ),
]
CATEGORIES = [
    "Lump in Breast",
    "Pain in Armpit/Breast",
    "Redness of Breast Skin",
    "Change in Size/Shape",
    "Nipple Discharge",
    "Inverted Nipple",
    "Rash on Nipple",
    "Swelling in Armpit/Collarbone",
    "Skin Texture Changes",
    "Thickened Tissue Areas",
]
section_headers = [
    "Physical Symptoms",
    "Skin and Texture",
    "Sensation",
    "Nipple and Discharge",
    "Lumps",
]
RISK_LEVEL = [
    {
        "level": "Low",
        "info": "Your risk level based on the assessment is <strong>Low</strong>. This indicates a lower likelihood of breast cancer. Regular screenings and a healthy lifestyle are recommended to maintain this low risk. Please continue to monitor for any unusual changes and consult your healthcare provider if you have concerns.",
        "description": [
            "With a score of {score}%, your risk of breast cancer is considered low. It is essential to continue regular check-ups and adopt healthy lifestyle habits to keep this risk minimal.",
            "A score of {score}% places you in the low-risk category. Maintaining a balanced diet, regular exercise, and routine medical screenings can help manage this risk effectively.",
        ],
        "next_steps": [
            {
                "title": "Continue Regular Check-Ups",
                "subtitle": "Maintain Routine Screenings",
                "messages": [
                    "Continue regular self-examinations and annual mammograms as recommended by your healthcare provider.",
                    "Maintain a healthy lifestyle, including a balanced diet and regular physical activity.",
                    "Stay informed about breast health and promptly report any changes to your healthcare provider.",
                ],
            },
            {
                "title": "Maintain Healthy Lifestyle",
                "subtitle": "Healthy Habits",
                "messages": [
                    "Maintain a healthy diet rich in fruits, vegetables, and whole grains.",
                    "Engage in regular physical activity, aiming for at least 150 minutes of moderate exercise per week.",
                    "Avoid smoking and limit alcohol consumption to reduce overall cancer risk.",
                ],
            },
        ],
        "resources": [
            {
                "text": "Breast Cancer Screening Guidelines",
                "url": "https://www.cancer.org/cancer/screening/get-screened.html",
            },
            {
                "text": "Healthy Lifestyle Tips",
                "url": "https://www.cancer.org/cancer/risk-prevention/diet-physical-activity/diet-and-physical-activity.html",
            },
        ],
        "recommendations": [
            {
                "title": "Schedule Routine Mammograms",
                "message": "Schedule routine mammograms as recommended by your healthcare provider, typically every 1-2 years for women over 40.",
            },
            {
                "title": "Stay Informed About Breast Health",
                "message": "Stay informed about breast health and perform regular self-examinations to detect any changes early.",
            },
            {
                "title": "Discuss Family History",
                "message": "Discuss any family history of breast cancer with your healthcare provider to ensure appropriate monitoring.",
            },
        ],
    },
    {
        "level": "Moderate",
        "info": "Your risk level based on the assessment is <strong>Moderate</strong>. This suggests an intermediate likelihood of breast cancer. It is important to consult with your healthcare provider to discuss your risk factors in detail. They may recommend more frequent screenings or preventive measures to manage your risk effectively.",
        "description": [
            "With a score of {score}%, your breast cancer risk is moderate. A detailed discussion with your healthcare provider about personalized screening plans and lifestyle adjustments is recommended.",
            "A score of {score}% indicates a moderate risk. Engaging in regular screenings and potentially adopting preventive measures as advised by your healthcare provider can help manage this risk.",
        ],
        "next_steps": [
            {
                "title": "Schedule a Consultation",
                "subtitle": "Discuss Risk Factors",
                "messages": [
                    "Schedule a detailed consultation with your healthcare provider to discuss your risk factors and create a personalized screening plan.",
                    "Consider lifestyle changes that can reduce your risk, such as a healthy diet and regular exercise.",
                    "Stay vigilant about breast health and promptly report any changes to your healthcare provider.",
                ],
            },
            {
                "title": "Lifestyle Adjustments",
                "subtitle": "Reduce Your Risk",
                "messages": [
                    "Increase the frequency of mammograms to annually, or as advised by your healthcare provider.",
                    "Consider lifestyle changes, such as adopting a diet high in antioxidants and omega-3 fatty acids.",
                    "Discuss the possibility of genetic testing if there is a family history of breast cancer.",
                ],
            },
        ],
        "resources": [
            {
                "text": "Understanding Your Risk",
                "url": "https://www.breastcancer.org/risk/understand",
            },
            {
                "text": "Preventive Health Measures",
                "url": "https://www.cdc.gov/chronic-disease/prevention/index.html",
            },
        ],
        "recommendations": [
            {
                "title": "Maintain a Healthy Weight",
                "message": "Maintain a healthy weight through balanced nutrition and regular exercise.",
            },
            {
                "title": "Consider Risk-Reducing Medications",
                "message": "Consider medications such as tamoxifen or raloxifene for risk reduction if recommended by your doctor.",
            },
            {
                "title": "Stay Vigilant for Changes",
                "message": "Stay vigilant for any changes in your breast tissue and report them to your healthcare provider immediately.",
            },
        ],
    },
    {
        "level": "High",
        "info": "Your risk level based on the assessment is <strong>High</strong>. This indicates a higher likelihood of breast cancer. Immediate consultation with your healthcare provider is crucial for a comprehensive evaluation. They will guide you on the next steps, which may include diagnostic tests and potential treatment options to address your risk.",
        "description": [
            "With a score of {score}%, your risk is high. It is crucial to seek immediate medical advice for a comprehensive evaluation and to discuss potential diagnostic tests and treatment options.",
            "A score of {score}% signifies a high risk of breast cancer. Prompt consultation with your healthcare provider is necessary to determine the appropriate next steps, including possible diagnostic procedures and interventions.",
        ],
        "next_steps": [
            {
                "title": "Urgent Consultation",
                "subtitle": "Seek Immediate Advice",
                "messages": [
                    "Arrange an urgent appointment with your healthcare provider for a comprehensive evaluation.",
                    "Be prepared to discuss potential diagnostic tests and treatment options with your healthcare provider.",
                    "Follow your healthcare provider's recommendations closely and stay informed about the latest advancements in breast cancer prevention and treatment.",
                ],
            },
            {
                "title": "Advanced Diagnostic Tests",
                "subtitle": "Detailed Evaluation",
                "messages": [
                    "Schedule an immediate appointment with a breast cancer specialist for a detailed evaluation.",
                    "Undergo advanced diagnostic tests such as MRI or ultrasound in addition to routine mammograms.",
                    "Discuss the potential benefits of risk-reducing medications or prophylactic surgery (e.g., mastectomy) with your healthcare provider.",
                ],
            },
        ],
        "resources": [
            {
                "text": "Steps to Take After a High-Risk Assessment",
                "url": "https://www.uchealth.com/en/media-room/articles/breast-cancer-risk-assessment",
            },
            {
                "text": "Breast Cancer Treatment Options",
                "url": "https://www.breastcancer.org/treatment",
            },
        ],
        "recommendations": [
            {
                "title": "Genetic Counseling and Testing",
                "message": "Consider genetic counseling and testing, especially if there is a significant family history of breast cancer.",
            },
            {
                "title": "Personalized Monitoring Plan",
                "message": "Develop a personalized monitoring plan with frequent clinical breast exams and imaging tests.",
            },
            {
                "title": "Stay Informed About Advances",
                "message": "Stay informed about the latest research and advances in breast cancer prevention and treatment.",
            },
            {
                "title": "Engage in Support Groups",
                "message": "Engage in support groups or counseling to address any emotional or psychological impacts of a high-risk diagnosis.",
            },
        ],
    },
]
FAQS = [
    {
        "heading": "General Information",
        "questions": [
            {
                "question": "What is the Breast Cancer Prediction Project?",
                "answer": "The Breast Cancer Prediction Project is an initiative designed to develop and implement machine learning models to predict the likelihood of breast cancer in individuals based on various risk factors.",
            },
            {
                "question": "What types of data are used in the prediction models?",
                "answer": "The models use data such as demographic information, medical history, genetic factors, lifestyle habits, and results from medical tests (e.g., mammograms, biopsies).",
            },
            {
                "question": "How does machine learning improve breast cancer prediction?",
                "answer": "Machine learning algorithms can analyze large datasets to identify patterns and correlations that might not be apparent through traditional analysis, leading to more accurate and personalized risk assessments.",
            },
            {
                "question": "Who can benefit from this project?",
                "answer": "This project is beneficial for women at risk of breast cancer, healthcare providers seeking to improve early detection, and researchers looking to enhance predictive models for breast cancer.",
            },
            {
                "question": "How accurate are the machine learning models used in the project?",
                "answer": "The accuracy of the models depends on the quality and quantity of the data used for training. While machine learning models can provide high accuracy, they are not infallible and should be used in conjunction with professional medical advice.",
            },
            {
                "question": "What are the primary goals of this project?",
                "answer": "The main goals are to improve early detection of breast cancer, provide personalized risk assessments, and support healthcare providers in making informed decisions about patient care.",
            },
            {
                "question": "How is patient privacy maintained in this project?",
                "answer": "Patient data is anonymized and stored securely. Only authorized personnel have access to the data, and strict protocols are in place to ensure confidentiality and compliance with data protection regulations.",
            },
            {
                "question": "Can the prediction models be integrated into existing healthcare systems?",
                "answer": "Yes, the models are designed to be compatible with existing electronic health record (EHR) systems and can be integrated to enhance clinical decision support tools.",
            },
            {
                "question": "What challenges does the project face?",
                "answer": "Challenges include ensuring the diversity and quality of the data, maintaining patient privacy, addressing ethical considerations, and continuously updating models to reflect new research findings.",
            },
            {
                "question": "How can healthcare providers use the predictions?",
                "answer": "Healthcare providers can use the predictions to identify high-risk individuals, recommend appropriate screenings, and discuss preventive measures or treatment options with their patients.",
            },
            {
                "question": "What is the significance of using AI in breast cancer prediction?",
                "answer": "AI can process vast amounts of data quickly and accurately, leading to earlier detection and potentially better outcomes for patients by enabling timely intervention.",
            },
            {
                "question": "How does the project address false positives and false negatives?",
                "answer": "The models are continuously refined to minimize false positives and negatives. Cross-validation, rigorous testing, and feedback loops with clinical data help improve model accuracy and reliability.",
            },
            {
                "question": "What are the future directions of this project?",
                "answer": "Future directions include expanding the dataset, incorporating new risk factors, improving model algorithms, and exploring collaborations with healthcare institutions for real-world implementation.",
            },
            {
                "question": "How can individuals participate in this project?",
                "answer": "Individuals can participate by contributing their data through clinical trials or registries, and by engaging with healthcare providers who use the prediction tools developed by the project.",
            },
            {
                "question": "What impact does this project aim to have on public health?",
                "answer": "The project aims to reduce the incidence of late-stage breast cancer diagnoses, improve survival rates, and contribute to the overall knowledge and management of breast cancer through advanced predictive analytics.",
            },
        ],
    },
    {
        "heading": "Results Interpretation",
        "questions": [
            {
                "question": "How should I interpret the risk score provided by the model?",
                "answer": "The risk score indicates the likelihood of developing breast cancer based on the input data. Higher scores suggest a higher risk, but it is important to discuss the results with a healthcare provider for a comprehensive interpretation.",
            },
            {
                "question": "What do the terms 'benign' and 'malignant' mean in the results?",
                "answer": "'Benign' indicates non-cancerous conditions, while 'malignant' indicates cancerous growths. The model provides probabilities for both to help assess the risk.",
            },
            {
                "question": "How can I understand the probabilities provided in the prediction?",
                "answer": "The probabilities for benign and malignant conditions are expressed as percentages. These indicate the likelihood of each condition based on the input data.",
            },
            {
                "question": "What should I do if my prediction indicates a high risk of breast cancer?",
                "answer": "If the prediction indicates a high risk, it is important to consult with a healthcare provider to discuss further diagnostic tests, preventive measures, and possible treatment options.",
            },
            {
                "question": "Can the prediction results change over time?",
                "answer": "Yes, prediction results can change as new data becomes available or if there are changes in risk factors such as age, lifestyle, or medical history.",
            },
            {
                "question": "Are the prediction results definitive?",
                "answer": "No, the results are not definitive. They are probabilistic estimates based on the input data and should be used as part of a broader diagnostic process involving healthcare professionals.",
            },
            {
                "question": "How often should I use the prediction tool?",
                "answer": "The frequency of use depends on individual risk factors and recommendations from healthcare providers. Regular updates to the data can help maintain accurate predictions.",
            },
        ],
    },
    {
        "heading": "Data Privacy and Security",
        "questions": [
            {
                "question": "How is my personal data protected in this project?",
                "answer": "Personal data is anonymized and encrypted to protect privacy. Strict access controls and data protection protocols are in place to ensure confidentiality.",
            },
            {
                "question": "Who has access to my data?",
                "answer": "Only authorized personnel involved in the project have access to the data. Access is granted based on the need to know and in compliance with data protection regulations.",
            },
            {
                "question": "Can I withdraw my data from the project?",
                "answer": "Yes, participants can request to withdraw their data from the project at any time. Procedures are in place to handle such requests while maintaining data integrity.",
            },
            {
                "question": "What measures are taken to ensure data security?",
                "answer": "Data security measures include encryption, secure storage, access controls, and regular security audits to protect against unauthorized access and data breaches.",
            },
            {
                "question": "Will my data be shared with third parties?",
                "answer": "Data may be shared with research collaborators or healthcare providers only with explicit consent from participants and under strict confidentiality agreements.",
            },
        ],
    },
    {
        "heading": "Technical Aspects",
        "questions": [
            {
                "question": "What machine learning algorithms are used in the project?",
                "answer": "The project employs various algorithms such as logistic regression, decision trees, random forests, support vector machines, and neural networks.",
            },
            {
                "question": "How is the model trained and validated?",
                "answer": "The model is trained using historical data and validated through cross-validation techniques to ensure accuracy and generalizability.",
            },
            {
                "question": "What programming languages and tools are used in the project?",
                "answer": "Common programming languages and tools used include Python, R, TensorFlow, Scikit-learn, and Pandas.",
            },
            {
                "question": "How are the models updated and maintained?",
                "answer": "Models are regularly updated with new data and retrained to improve performance. Continuous monitoring and evaluation ensure they remain accurate and relevant.",
            },
            {
                "question": "Can the model be customized for different populations?",
                "answer": "Yes, the model can be adapted to account for demographic and genetic variations across different populations to improve accuracy and relevance.",
            },
        ],
    },
    {
        "heading": " Clinical Applications",
        "questions": [
            {
                "question": "How can healthcare providers integrate the prediction tool into their practice?",
                "answer": "Healthcare providers can integrate the tool into their electronic health records (EHR) systems and use it as part of routine screenings and risk assessments.",
            },
            {
                "question": "What benefits does the prediction tool offer to clinicians?",
                "answer": "The tool provides clinicians with additional insights into patient risk profiles, helping them make more informed decisions about screening and preventive measures.",
            },
            {
                "question": "How can the prediction tool support early detection of breast cancer?",
                "answer": "By identifying high-risk individuals early, the tool can prompt timely screenings and interventions, potentially leading to earlier detection and better outcomes.",
            },
            {
                "question": "What training is required for healthcare providers to use the tool?",
                "answer": "Minimal training is required, focusing on understanding the results and integrating the tool into clinical workflows. Detailed user guides and support are provided.",
            },
            {
                "question": "Can the tool be used in conjunction with other diagnostic methods?",
                "answer": "Yes, the tool is designed to complement other diagnostic methods such as mammograms and biopsies, providing a more comprehensive assessment of breast cancer risk.",
            },
        ],
    },
    {
        "heading": "Research Development",
        "questions": [
            {
                "question": "What are the key research objectives of the project?",
                "answer": "Key objectives include improving model accuracy, expanding the dataset, and exploring new risk factors and biomarkers for breast cancer prediction.",
            },
            {
                "question": "How can researchers contribute to the project?",
                "answer": "Researchers can contribute by providing data, collaborating on model development, and conducting studies to validate and refine the prediction models.",
            },
            {
                "question": "What advancements have been made since the project's inception?",
                "answer": "Significant advancements include the development of more accurate models, integration with healthcare systems, and publication of research findings.",
            },
            {
                "question": "How is the project funded?",
                "answer": "The project is funded through a combination of grants, institutional support, and contributions from research collaborators and healthcare organizations.",
            },
            {
                "question": "What are the long-term goals of the project?",
                "answer": "Long-term goals include widespread adoption of the prediction tool in clinical practice, continuous improvement of model performance, and significant contributions to breast cancer research and prevention.",
            },
        ],
    },
]
RATE_CHOICES = [
    (1, "Very Poor"),
    (2, "Poor"),
    (3, "Average"),
    (4, "Good"),
    (5, "Excellent"),
]
SLIDER_LABELS = [
    ("Radius (mean)", "radius_mean"),
    ("Texture (mean)", "texture_mean"),
    ("Perimeter (mean)", "perimeter_mean"),
    ("Area (mean)", "area_mean"),
    ("Smoothness (mean)", "smoothness_mean"),
    ("Compactness (mean)", "compactness_mean"),
    ("Concavity (mean)", "concavity_mean"),
    ("Concave points (mean)", "concave points_mean"),
    ("Symmetry (mean)", "symmetry_mean"),
    ("Fractal dimension (mean)", "fractal_dimension_mean"),
    ("Radius (se)", "radius_se"),
    ("Texture (se)", "texture_se"),
    ("Perimeter (se)", "perimeter_se"),
    ("Area (se)", "area_se"),
    ("Smoothness (se)", "smoothness_se"),
    ("Compactness (se)", "compactness_se"),
    ("Concavity (se)", "concavity_se"),
    ("Concave points (se)", "concave points_se"),
    ("Symmetry (se)", "symmetry_se"),
    ("Fractal dimension (se)", "fractal_dimension_se"),
    ("Radius (worst)", "radius_worst"),
    ("Texture (worst)", "texture_worst"),
    ("Perimeter (worst)", "perimeter_worst"),
    ("Area (worst)", "area_worst"),
    ("Smoothness (worst)", "smoothness_worst"),
    ("Compactness (worst)", "compactness_worst"),
    ("Concavity (worst)", "concavity_worst"),
    ("Concave points (worst)", "concave points_worst"),
    ("Symmetry (worst)", "symmetry_worst"),
    ("Fractal dimension (worst)", "fractal_dimension_worst"),
]
PROBABILITY_SUMMARIES = [
    {
        "range": "0% - 10% Malignancy (90% - 100% Benign)",
        "summary": (
            "According to medical analysis, the tumor is highly likely to be benign. As a result, the necessity for additional invasive diagnostic procedures is minimal. It is recommended to consider routine follow-up imaging, such as mammography or ultrasound, to monitor any potential changes in the tumor."
        ),
        "recommendation": "Scheduled monitoring and regular check-ups are recommended. No immediate treatment is necessary.",
    },
    {
        "range": "11% - 20% Malignancy (80% - 89% Benign)",
        "summary": (
            "The tumor is highly likely to be benign. Although the probability of malignancy is low, it is advisable to conduct a confirmatory test, such as a core needle biopsy or advanced imaging, in order to rule out malignancy. Subsequent steps should be determined based on the results of the imaging."
        ),
        "recommendation": "Kindly consider arranging a follow-up appointment for a biopsy or advanced imaging to confirm the diagnosis.",
    },
    {
        "range": "21% - 30% Malignancy (70% - 79% Benign)",
        "summary": (
            "The observed tumor presents a relatively high probability of being benign. However, the moderate likelihood of malignancy indicates the necessity for further assessment. It is recommended to proceed with diagnostic investigations, including a biopsy, to establish the benign nature of the tumor or identify potential early-stage malignancy."
        ),
        "recommendation": "Proceed with the biopsy and follow-up with imaging for a more definitive diagnosis.",
    },
    {
        "range": "31% - 40% Malignancy (60% - 69% Benign)",
        "summary": (
            "There is a discernible equilibrium between the probability of benign and malignant conditions, underscoring the need for a comprehensive evaluation. A biopsy is recommended to ascertain the nature of the lesion, and an exploration of treatment options is warranted in the event of confirmed malignancy."
        ),
        "recommendation": "Please ensure comprehensive diagnostic testing is conducted, which includes biopsy and staging.",
    },
    {
        "range": "41% - 50% Malignancy (50% - 59% Benign)",
        "summary": (
            "The tumor presents a near-equal probability of being either benign or malignant. This nuanced situation necessitates prompt diagnostic assessment, including a biopsy. Decisions regarding the clinical course should be made in accordance with the biopsy results and may involve intervention based on subsequent findings."
        ),
        "recommendation": "Immediate diagnostic evaluation, including a biopsy, and potential early intervention are recommended.",
    },
    {
        "range": "51% - 60% Malignancy (40% - 49% Benign)",
        "summary": (
            "The tumor exhibits a slightly higher likelihood of being malignant. It is imperative to promptly undertake diagnostic procedures, including imaging and biopsy, to definitively determine the malignancy status. Subsequent treatment options, such as surgery or chemotherapy, may be necessary, contingent upon the confirmed diagnosis."
        ),
        "recommendation": "Please proceed with conducting a diagnostic workup and carefully consider the available treatment options.",
    },
    {
        "range": "61% - 70% Malignancy (30% - 39% Benign)",
        "summary": (
            "The findings indicate a high probability of malignancy. Prompt diagnostic testing is essential for early detection. It is imperative to promptly consider a comprehensive treatment plan, which may include surgical intervention, chemotherapy, or radiation therapy."
        ),
        "recommendation": "Urgent oncology consultation and immediate treatment preparation.",
    },
    {
        "range": "71% - 80% Malignancy (20% - 29% Benign)",
        "summary": (
            "The findings indicate a high probability of malignancy, necessitating immediate intervention. The recommended course of action typically involves surgical excision, followed by adjunctive therapies such as chemotherapy or radiation. Prioritizing a comprehensive diagnostic assessment and staging is imperative."
        ),
        "recommendation": "Make the comprehensive oncological intervention a top priority and proceed with the development of a treatment plan.",
    },
    {
        "range": "81% - 90% Malignancy (10% - 19% Benign)",
        "summary": (
            "The initial assessment indicates a high probability of malignancy. We recommend pursuing aggressive management strategies which may include surgical resection and systemic therapies. Additionally, consideration should be given to incorporating adjuvant therapies to address potential metastatic spread."
        ),
        "recommendation": "Aggressive treatment, including surgery and systemic therapy, is necessary.",
    },
    {
        "range": "91% - 100% Malignancy (0% - 9% Benign)",
        "summary": (
            "Based on the diagnosis, the tumor is highly likely to be malignant, necessitating prompt intervention such as surgical excision, chemotherapy, radiation, or other targeted treatments. It is imperative to involve a multidisciplinary team to ensure comprehensive care."
        ),
        "recommendation": "Urgent and aggressive intervention with a comprehensive oncological management plan.",
    },
]
FEATURE_EXPLANATIONS = [
    {
        "feature": "radius_mean",
        "explanation": "The average distance from the center of the tumor to its edge. Larger values typically indicate a larger tumor.",
    },
    {
        "feature": "texture_mean",
        "explanation": "The average variation in the grayscale values of the tumor's pixels. Higher values suggest a rougher texture.",
    },
    {
        "feature": "perimeter_mean",
        "explanation": "The average length around the boundary of the tumor. Larger values may suggest a larger or more irregularly shaped tumor.",
    },
    {
        "feature": "area_mean",
        "explanation": "The average size of the tumor's cross-sectional area. Larger values indicate a larger tumor.",
    },
    {
        "feature": "smoothness_mean",
        "explanation": "The average smoothness of the tumor's surface. Lower values indicate a smoother surface, while higher values suggest more irregularity.",
    },
    {
        "feature": "compactness_mean",
        "explanation": "The ratio of the tumor's perimeter squared to its area, adjusted for the shape's compactness. Higher values suggest a less compact and more irregular shape.",
    },
    {
        "feature": "concavity_mean",
        "explanation": "The extent to which the tumor's contour is concave {i.e., has inward-curving parts). Higher values suggest more concave areas.",
    },
    {
        "feature": "concave_points_mean",
        "explanation": "The number of concave parts of the tumor's boundary. Higher values indicate more pronounced inward curves.",
    },
    {
        "feature": "symmetry_mean",
        "explanation": "The symmetry of the tumor's shape. Higher values suggest less symmetry.",
    },
    {
        "feature": "fractal_dimension_mean",
        "explanation": "A measure of the tumor's boundary complexity. Higher values indicate a more irregular and complex boundary.",
    },
    {
        "feature": "radius_se",
        "explanation": "The standard error of the radius measurement. Higher values suggest more variation in the tumor's radius.",
    },
    {
        "feature": "texture_se",
        "explanation": "The standard error of the texture measurement. Higher values indicate more variation in the tumor's texture.",
    },
    {
        "feature": "perimeter_se",
        "explanation": "The standard error of the perimeter measurement. Higher values suggest more variation in the tumor's boundary.",
    },
    {
        "feature": "area_se",
        "explanation": "The standard error of the area measurement. Higher values indicate more variation in the tumor's size.",
    },
    {
        "feature": "smoothness_se",
        "explanation": "The standard error of the smoothness measurement. Higher values suggest more variation in the tumor's surface smoothness.",
    },
    {
        "feature": "compactness_se",
        "explanation": "The standard error of the compactness measurement. Higher values indicate more variation in the tumor's compactness.",
    },
    {
        "feature": "concavity_se",
        "explanation": "The standard error of the concavity measurement. Higher values suggest more variation in the tumor's concave areas.",
    },
    {
        "feature": "concave_points_se",
        "explanation": "The standard error of the concave points measurement. Higher values indicate more variation in the number of concave points.",
    },
    {
        "feature": "symmetry_se",
        "explanation": "The standard error of the symmetry measurement. Higher values suggest more variation in the tumor's symmetry.",
    },
    {
        "feature": "fractal_dimension_se",
        "explanation": "The standard error of the fractal dimension measurement. Higher values indicate more variation in the boundary complexity.",
    },
    {
        "feature": "radius_worst",
        "explanation": "The largest value of the radius across all cells in the image. Higher values typically indicate a larger tumor.",
    },
    {
        "feature": "texture_worst",
        "explanation": "The roughest texture observed in the tumor. Higher values suggest a rougher surface.",
    },
    {
        "feature": "perimeter_worst",
        "explanation": "The longest boundary measurement observed in the tumor. Higher values indicate a larger or more irregularly shaped tumor.",
    },
    {
        "feature": "area_worst",
        "explanation": "The largest area observed for the tumor. Higher values indicate a larger tumor.",
    },
    {
        "feature": "smoothness_worst",
        "explanation": "The least smooth surface observed in the tumor. Higher values suggest a more irregular surface.",
    },
    {
        "feature": "compactness_worst",
        "explanation": "The most compact (or least compact) shape observed for the tumor. Higher values suggest a less compact and more irregular shape.",
    },
    {
        "feature": "concavity_worst",
        "explanation": "The most concave shape observed in the tumor. Higher values suggest deeper inward curves.",
    },
    {
        "feature": "concave_points_worst",
        "explanation": "The highest number of concave points observed in the tumor. Higher values indicate more pronounced inward curves.",
    },
    {
        "feature": "symmetry_worst",
        "explanation": "The least symmetrical shape observed in the tumor. Higher values suggest less symmetry.",
    },
    {
        "feature": "fractal_dimension_worst",
        "explanation": "The most complex boundary observed in the tumor. Higher values indicate a more irregular and complex boundary.",
    },
]
FEATURE_ABBRI = [
    {
        "feature": "Tumor",
        "explanation": "An abnormal growth of cells that can be benign (non-cancerous) or malignant (cancerous).",
    },
    {
        "feature": "Radius",
        "explanation": "The distance from the center of the tumor to its edge.",
    },
    {
        "feature": "Texture",
        "explanation": "The variation in grayscale values of the tumor's pixels.",
    },
    {
        "feature": "Perimeter",
        "explanation": "The length around the boundary of the tumor.",
    },
    {"feature": "Area", "explanation": "The size of the tumor's cross-sectional area."},
    {
        "feature": "Smoothness",
        "explanation": "How smooth or irregular the tumor's surface is.",
    },
    {
        "feature": "Compactness",
        "explanation": "How closely packed or dense the tumor is.",
    },
    {
        "feature": "Concavity",
        "explanation": "The extent to which the tumor's contour is concave.",
    },
    {
        "feature": "Concave Points",
        "explanation": "The number of concave parts of the tumor's boundary.",
    },
    {
        "feature": "Symmetry",
        "explanation": "How evenly balanced or identical the tumor's shape is.",
    },
    {
        "feature": "Fractal Dimension",
        "explanation": "A measure of the tumor's boundary complexity.",
    },
]
import pandas as pd
from PaulVideoPlatform import settings


class HelpResponse:

    categories = [
        "Radius",
        "Texture",
        "Perimeter",
        "Area",
        "Smoothness",
        "Compactness",
        "Concavity",
        "Concave Points",
        "Symmetry",
        "Fractal Dimension",
    ]

    def generate_key(self, category, key_type):
        if category == "Concave Points":
            return f"concave points_{key_type}"
        return f"{category.lower().replace(' ', '_')}_{key_type}"

    def get_clean_data(self):
        data = pd.read_csv(f"{settings.STATICFILES_DIRS[0]}/model/data.csv")
        data = data.drop(["Unnamed: 32", "id"], axis=1)
        data["diagnosis"] = data["diagnosis"].map({"M": 1, "B": 0})
        return data

    def add_predictions(self, input_data):
        dir = settings.STATICFILES_DIRS[0]
        model_file_path = self.request.trained_model.model_file_path
        scaler_file_path = self.request.trained_model.scaler_file_path
        model = pickle.load(open(model_file_path, "rb"))
        scaler = pickle.load(open(scaler_file_path, "rb"))

        input_df = pd.DataFrame([input_data])
        input_array_scaled = scaler.transform(input_df)
        prediction = model.predict(input_array_scaled)
        probabilities = model.predict_proba(input_array_scaled)
        return probabilities, prediction

    def get_scaled_values(self, input_dict):
        data = self.get_clean_data()
        X = data.drop(["diagnosis"], axis=1)
        scaled_dict = {}
        for key, value in input_dict.items():
            max_val = X[key].max()
            min_val = X[key].min()
            scaled_value = (value - min_val) / (max_val - min_val)
            scaled_dict[key] = scaled_value
        return scaled_dict

    def fetchRespondedQuestions(self, response_instance):
        grouped_questions = {header: [] for header in section_headers}
        for response in response_instance.responses.all():
            question = next(q for q in QUESTIONS if q[1] == response.question_key)
            index = QUESTIONS.index(question) // 6
            section_header = section_headers[index]
            grouped_questions[section_header].append(question[0])

        grouped_questions = {k: v for k, v in grouped_questions.items() if v}
        return grouped_questions

    def make_prediction(self, probabilities=None, risk_score=None):
        # Get the probability of the positive class (malignant)
        risk_score = risk_score if risk_score else probabilities[0][1]
        risk_level = self.get_risk_level_from_score(risk_score)
        return risk_level, risk_score

    def get_risk_level_from_score(self, score):
        formatted_score = f"{score * 100:.2f}"
        if score > 1:
            score /= 100
        if score < 0.33:
            risk_level = RISK_LEVEL[0]
        elif score < 0.66:
            risk_level = RISK_LEVEL[1]
        else:
            risk_level = RISK_LEVEL[2]
        description = risk_level["description"][0].format(score=formatted_score)
        return {
            "level": risk_level["level"],
            "info": risk_level["info"],
            "score": description,
            "next": risk_level["next_steps"][0]["messages"][0],
            "next_steps": risk_level["next_steps"],
            "resources": risk_level["resources"],
            "recommendations": risk_level["recommendations"],
        }
