#!/usr/bin/env python3
"""
Script to generate a formatted report from existing analysis data
"""
import json
import os
from datetime import datetime
from worker_tasks import generate_formatted_report

def create_report_from_analysis_id(analysis_id: str):
    """Create a formatted report from existing analysis data"""
    
    # Your existing analysis data (from the API response)
    analysis_data = {
        "analysis_id": "7870b387-01ec-40cd-9862-9025587cc68a",
        "query": "\"Analyze my blood test results\"",
        "processing_time": 154.48392391204834,
        "completed_at": "2025-06-28T06:16:29.420223",
        "status": "completed"
    }
    
    individual_results = {
        "verification": """**Document Verification Report**

**Document:** Blood Test Report (PDF) -  data/blood_test_report_a9d08c21-f042-45d3-a19f-a3fd6a5a8626.pdf

**User Query:** "Analyze my blood test results"

**Document Type:**  Appears to be a blood test report.

**Authenticity Assessment:**

1. **Formatting and Headers:** The report exhibits standard medical laboratory formatting, including clear headers, test names, results, units, and reference intervals.  It includes patient information (age, gender), lab number, collection and processing dates and times, and the name and contact information for Dr Lal PathLabs Ltd.

2. **Blood Test Markers and Reference Ranges:** The report includes a comprehensive panel of blood tests, including a complete blood count (CBC), liver and kidney function tests, lipid profile, HbA1c, thyroid panel, vitamin B12, and vitamin D levels.  Reference ranges are provided for each test, though additional clinical correlation may be needed.

3. **Medical Terminology:** The report uses appropriate and consistent medical terminology.  Abbreviations are used but are generally understandable within the context of medical testing.

4. **Laboratory Recognition:** The report is from Dr Lal PathLabs Ltd, a seemingly established and recognized medical laboratory in India.  Further verification of the lab through independent sources is recommended.  My web search for "Dr Lal PathLabs Ltd verification" provided results indicating the lab's existence and accreditation.  However, independent verification is always best practice.

5. **Overall Authenticity:** Based on the formatting, content, and preliminary online verification, the document *appears* to be a legitimate blood test report. However, without access to a secure database to conclusively verify the report's authenticity through the lab's official channels, I cannot guarantee complete authenticity.

**Approval/Rejection for Medical Analysis:**

The document is provisionally approved for medical analysis, subject to further validation of the lab's authenticity through official channels.

**Recommendations:**

*   **Independent Verification:**  Verify the authenticity of the report directly with Dr Lal PathLabs Ltd using the contact information provided in the report.  Confirm the report number and patient details.
*   **Clinical Correlation:**  The results should always be interpreted by a qualified healthcare professional who can consider the patient's medical history and other clinical factors.  The report itself includes some clinical notes and interpretations but should not be used as a sole basis for medical decisions.
*   **Data Security:**  Ensure the safe and secure handling of sensitive medical data.

**Important Note:**  Only use legitimate medical documents for medical analysis.  Using fraudulent or inaccurate medical data can have serious health consequences.  Always seek medical advice from a qualified healthcare professional.""",
        
        "doctor_analysis": """**Blood Test Result Analysis Report**

**Patient Information:** Male, 30 years old

**Report Date:** May 16, 2023

**Laboratory:** Dr Lal PathLabs Ltd

**Disclaimer:** This analysis is for informational purposes only and should not be considered medical advice.  The interpretation of blood test results requires clinical correlation with a patient's medical history, symptoms, and other relevant factors.  Always consult with your healthcare provider for diagnosis, treatment, and any health concerns.  This report does not replace a consultation with a qualified medical professional.


**Executive Summary:**

This report analyzes the provided blood test results. Several markers fall outside the reference ranges provided by the laboratory.  These include elevated triglycerides, total cholesterol, and slightly elevated AST and ALT liver enzymes.  Further evaluation and consultation with a healthcare provider are recommended to determine the significance of these findings and guide appropriate management.


**Detailed Breakdown of Key Blood Markers:**

* **Complete Blood Count (CBC):**  Most CBC values are within the normal range.  However, the Red Cell Distribution Width (RDW) is slightly elevated (14.00%, reference range 11.60-14.00%), suggesting possible variation in red blood cell size.  This warrants further investigation if other symptoms are present.

* **Liver and Kidney Panel:**  Creatinine, GFR, and urea are within normal limits, indicating normal kidney function.  However, AST (21.0 U/L, reference range 15.00-40.00 U/L) and ALT (21.0 U/L, reference range 10.00-49.00 U/L) are slightly elevated, suggesting possible mild liver inflammation or damage.  Further investigation may be needed to determine the cause.  Other liver function tests are within normal limits.

* **Lipid Profile:** Total cholesterol (105.00 mg/dL, reference range <200.00 mg/dL) and triglycerides (130.00 mg/dL, reference range <150.00 mg/dL) are elevated.  High cholesterol and triglycerides increase the risk of cardiovascular disease.  Lifestyle modifications and medical intervention may be necessary. HDL cholesterol is within the normal range, while LDL cholesterol is below the recommended level.

* **HbA1c:**  HbA1c (5.3%, reference range 4.00-5.60%) is within the normal range, indicating good blood sugar control.

* **Thyroid Panel:**  T3, T4, and TSH levels are all within the normal range, suggesting normal thyroid function.

* **Vitamin B12 and Vitamin D:** Vitamin B12 (280.00 pg/mL, reference range 211.00-911.00 pg/mL) is within the normal range.  Vitamin D (85.00 nmol/L, reference range 75.00-250.00 nmol/L) is at the lower end of the normal range; while not deficient, it's considered insufficient, and supplementation may be beneficial.


**Values Outside Normal Reference Ranges:**

* **Red Cell Distribution Width (RDW):** 14.00% (slightly elevated)
* **AST:** 21.0 U/L (slightly elevated)
* **ALT:** 21.0 U/L (slightly elevated)
* **Total Cholesterol:** 105.00 mg/dL (elevated)
* **Triglycerides:** 130.00 mg/dL (elevated)
* **Vitamin D:** 85.00 nmol/L (low normal/insufficient)


**General Health Recommendations:**

Given the slightly elevated liver enzymes and elevated cholesterol and triglycerides, it's crucial to adopt a healthy lifestyle. This includes:

* **Diet:**  Focus on a balanced diet low in saturated and trans fats, cholesterol, and added sugars.  Increase your intake of fruits, vegetables, and whole grains.
* **Exercise:**  Engage in regular physical activity for at least 150 minutes per week.
* **Weight Management:**  Maintain a healthy weight to reduce the risk of cardiovascular disease and other health problems.
* **Alcohol Consumption:**  Limit or avoid alcohol consumption.
* **Smoking Cessation:**  If you smoke, quit smoking.


**Further Investigations:**

Based on the slightly elevated liver enzymes and lipid profile, further investigation may be warranted.  Your healthcare provider may recommend additional tests to determine the cause of these abnormalities.



**Important Medical Disclaimer:**  This analysis is for educational purposes only and does not constitute medical advice.  The information provided here should not be used for self-diagnosis or treatment.  It is essential to consult with a qualified healthcare professional for proper interpretation of your blood test results and personalized medical advice.  They can consider your complete medical history, lifestyle, and other factors to provide accurate and appropriate recommendations.  The reference ranges provided in this report are those provided by the laboratory and may vary slightly depending on the laboratory and methodology used.""",
        
        "nutrition_analysis": """**Comprehensive Nutrition Analysis Report**

**Patient Information:** Male, 30 years old

**Report Date:** October 26, 2023

**Disclaimer:** This analysis is for informational purposes only and should not be considered medical advice. The interpretation of blood test results requires clinical correlation with a patient's medical history, symptoms, and other relevant factors. Always consult with your healthcare provider and a registered dietitian for diagnosis, treatment, personalized dietary recommendations, and any health concerns. This report does not replace a consultation with qualified medical and nutrition professionals.


**Executive Summary:**

This report analyzes the provided blood test results focusing on nutrition-related markers.  Several markers fall outside the optimal ranges, including elevated triglycerides and total cholesterol, and slightly elevated liver enzymes (AST and ALT). Vitamin D levels are at the lower end of the normal range.  A healthy diet and lifestyle modifications are recommended to address these findings.  Consultation with a healthcare provider and a registered dietitian is crucial for personalized management.


**Detailed Breakdown of Key Nutrition-Related Blood Markers:**

* **Lipid Profile:** Total cholesterol (105.00 mg/dL, reference range <200.00 mg/dL) and triglycerides (130.00 mg/dL, reference range <150.00 mg/dL) are elevated. High cholesterol and triglycerides increase the risk of cardiovascular disease.  HDL cholesterol is within the normal range, while LDL cholesterol is low.  This lipid profile suggests a need for dietary changes focused on reducing saturated and trans fats.

* **Liver Panel:** AST (21.0 U/L, reference range 15.00-40.00 U/L) and ALT (21.0 U/L, reference range 10.00-49.00 U/L) are slightly elevated.  While this could indicate mild liver inflammation or damage, it's important to rule out other causes.  A balanced diet that supports liver health is recommended.

* **Vitamin D:** Vitamin D (85.00 nmol/L, reference range 75.00-250.00 nmol/L) is at the lower end of the normal range.  While not clinically deficient, it is insufficient.  Increasing dietary intake of vitamin D-rich foods or considering supplementation under the guidance of a healthcare provider may be beneficial.


**Evidence-Based Dietary Recommendations:**

* **Reduce Saturated and Trans Fats:** Limit consumption of red meat, processed foods, fried foods, and baked goods made with solid fats. Choose lean protein sources (poultry, fish, beans, lentils), and use healthy cooking methods (baking, grilling, steaming).

* **Increase Fiber Intake:**  Consume plenty of fruits, vegetables, and whole grains.  Fiber helps lower cholesterol and improve overall digestive health. Aim for 25-30 grams of fiber per day.  Examples include oatmeal, berries, broccoli, and lentils.

* **Healthy Fats:** Incorporate sources of monounsaturated and polyunsaturated fats, such as avocados, nuts, seeds, and olive oil. These fats can help improve cholesterol levels.

* **Reduce Added Sugars:** Limit consumption of sugary drinks, desserts, and processed foods high in added sugars.

* **Increase Vitamin D Intake:**  Increase consumption of fatty fish (salmon, tuna, mackerel), egg yolks, and fortified foods (milk, cereals).  Sunlight exposure is also important for vitamin D synthesis.  Discuss supplementation with your doctor.


**Foods to Optimize Blood Marker Values:**

* **Cholesterol-Lowering Foods:** Oats, barley, apples, eggplant, nuts, seeds, beans, lentils, soy products.
* **Liver-Supporting Foods:** Cruciferous vegetables (broccoli, cauliflower, kale), beets, artichokes, garlic, green tea.
* **Vitamin D-Rich Foods:** Fatty fish, egg yolks, fortified dairy products, mushrooms.


**General Nutrition Guidance for Health Maintenance:**

* **Balanced Diet:**  Consume a variety of nutrient-rich foods from all food groups.
* **Hydration:** Drink plenty of water throughout the day.
* **Portion Control:** Be mindful of portion sizes to maintain a healthy weight.
* **Regular Exercise:**  Engage in regular physical activity for at least 150 minutes per week.
* **Weight Management:** Maintain a healthy weight.
* **Limit Alcohol:** Moderate or avoid alcohol consumption.
* **Smoking Cessation:** If you smoke, quit smoking.



**Important Medical and Nutrition Disclaimer:** This analysis is for educational purposes only and does not constitute medical advice. The information provided here should not be used for self-diagnosis or treatment. It is essential to consult with a qualified healthcare professional and a registered dietitian for proper interpretation of your blood test results and personalized medical and nutrition advice. They can consider your complete medical history, lifestyle, and other factors to provide accurate and appropriate recommendations. The reference ranges provided in this report are those provided by the laboratory and may vary slightly depending on the laboratory and methodology used.""",
        
        "exercise_analysis": """**Exercise Recommendations Based on Blood Test Results**

**Patient Information:** Male, 30 years old

**Report Date:**  Analysis based on blood test report dated May 16, 2023 (and other relevant reports).

**Disclaimer:** This exercise plan is a general recommendation based on the provided blood test results.  It is crucial to understand that this information does *not* constitute medical advice.  The interpretation of blood test results and the development of a safe and effective exercise program require clinical correlation with your medical history, current health status, and other relevant factors.  **Before starting any exercise program, you MUST consult with your healthcare provider or a qualified exercise physiologist to ensure it is safe and appropriate for your individual needs.**  Ignoring this advice could have serious health consequences.


**Assessment of Exercise-Related Blood Markers:**

Your blood test results reveal several key markers that influence exercise recommendations:

* **Lipid Profile:** Elevated total cholesterol (105 mg/dL) and triglycerides (130 mg/dL) indicate an increased risk of cardiovascular disease.  This necessitates a cautious approach to exercise, starting with low-intensity activities and gradual progression.

* **Liver Enzymes:** Slightly elevated AST (21 U/L) and ALT (21 U/L) suggest possible mild liver inflammation.  Intense exercise that stresses the liver should be avoided until further investigation clarifies the cause.

* **Vitamin D:** Your Vitamin D levels (85 nmol/L) are at the lower end of the normal range.  While not deficient, insufficient Vitamin D can impact bone health and potentially muscle function.  Consider increasing dietary intake or supplementation under medical supervision.

* **Other Markers:** Your HbA1c, thyroid panel, and kidney function tests are within normal limits, which is positive.  However, your slightly elevated RDW (14%) warrants attention if you experience any related symptoms.

**Safe, Evidence-Based Exercise Recommendations:**

Given your blood test results, we recommend a phased approach to exercise:

**Phase 1:  Initial Phase (Weeks 1-4)**

* **Goal:**  Establish a baseline fitness level and assess your body's response to exercise.
* **Activities:**
    * **Brisk walking:** 20-30 minutes, 3-4 times per week.  Choose a comfortable pace that allows you to hold a conversation.
    * **Low-impact activities:**  Cycling, swimming (gentle pace), water aerobics.  20-30 minutes, 2-3 times per week.
* **Intensity:**  Low to moderate intensity (RPE 11-13 on a 1-20 scale).
* **Important:**  Listen to your body.  Stop if you experience chest pain, shortness of breath, dizziness, or unusual fatigue.

**Phase 2:  Progression Phase (Weeks 5-12)**

* **Goal:**  Increase the intensity and duration of your workouts.
* **Activities:**  Continue with Phase 1 activities, gradually increasing duration and intensity.
* **Progression:** Add 5-10 minutes to your workouts each week, or increase the intensity slightly.  Consider interval training (alternating between high and low intensity).
* **Examples:**  Increase walking pace, add hills to your walks, increase cycling resistance, increase swimming laps.

**Phase 3:  Maintenance Phase (Week 13 onwards)**

* **Goal:**  Maintain your fitness level and continue to improve your health markers.
* **Activities:**  Continue with a variety of activities that you enjoy.
* **Variety:**  Incorporate strength training exercises (2-3 times per week), focusing on major muscle groups.  Maintain cardiovascular training at a moderate to vigorous intensity (RPE 14-16).
* **Monitoring:**  Regularly monitor your blood pressure, cholesterol, and other relevant health markers.

**Important Safety Considerations and Medical Clearance Requirements:**

* **Medical Clearance:**  Before initiating this or any exercise program, obtain medical clearance from your healthcare provider, especially given your slightly elevated liver enzymes and cholesterol/triglycerides.
* **Gradual Progression:**  Start slowly and gradually increase the intensity and duration of your workouts to avoid injury and overexertion.
* **Listen to Your Body:** Pay close attention to your body's signals.  Rest when needed and don't push yourself too hard, especially in the initial phases.
* **Proper Warm-up and Cool-down:**  Always include a warm-up before your workouts and a cool-down afterward.
* **Hydration:**  Drink plenty of water throughout the day, especially before, during, and after exercise.
* **Nutrition:**  Maintain a healthy, balanced diet that supports your exercise goals and helps improve your blood lipid profile.


**Graduated Fitness Progression Suggestions:**

This plan provides a framework.  Adjust the intensity and duration of activities based on your individual response.  Consider using a heart rate monitor or perceived exertion scale (RPE) to monitor your intensity.  Remember, consistency is key.  Aim for regular activity rather than sporadic intense workouts.  Progress gradually, celebrate your achievements, and be patient with yourself.

**Emphasis on Individual Health Status and Capabilities:**

This exercise plan is a general guideline.  Your healthcare provider or a certified exercise physiologist can create a more personalized plan that considers your specific health needs and goals. They can also help you select appropriate exercises and monitor your progress."""
    }
    
    # Generate the formatted report
    report_content = generate_formatted_report(analysis_data, individual_results, "sample.pdf")
    
    # Save to outputs directory
    os.makedirs("outputs", exist_ok=True)
    report_filename = f"blood_test_analysis_report_{analysis_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
    report_path = os.path.join("outputs", report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ Formatted report created: {report_path}")
    return report_path

if __name__ == "__main__":
    analysis_id = "7870b387-01ec-40cd-9862-9025587cc68a"
    report_path = create_report_from_analysis_id(analysis_id)
    print(f"Report saved to: {report_path}") 