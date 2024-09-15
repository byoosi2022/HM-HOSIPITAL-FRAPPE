import frappe
from collections import defaultdict

@frappe.whitelist()
def fetch_patient_labtest(patient):
    # List of lab test templates to filter on
    test_templates = [
        "H pylori Antigen test", "Hepatitis C Test", "URINE TB LAM", "Blood grouping-Test",
        "Blood slide(B/S) for Mps -Test", "Brucella Agglutination Test(BAT)-Test", "H. Pylori Antibody Test",
        "Hb Estimation-Test", "HBA1C- Test", "HBsAg-Test", "HIV test", "Malaria-MRDT Test",
        "Pregnancy test (Serum HCG)- Test", "Pregnancy test (urine HCG)-Test", "Prostate Specific Antigen (PSA)-Test",
        "Random blood sugar (RBS)-Test", "Rheumatoid Factor-Test", "RPR/VDRL-Test", "Sickle scan-Test", "Typhoid test"
    ]
    
    # Fetch the patient document
    patient_doc = frappe.get_doc('Patient', patient)
    
    if not patient_doc:
        return {"message": "Patient not found."}
    
    # Fetch the patient registration details (assuming you have a custom link field for MRN)
    patient_reg = frappe.get_doc('Patient Registration Identification', patient_doc.custom_patient_mrno)
    
    if not patient_reg:
        return {"message": "Patient Registration not found."}

    # Fetch all lab tests associated with the patient and filter by the specified templates
    lab_tests = frappe.get_all('Lab Test', 
                                filters={'patient': patient, 'template': ['in', test_templates]}, 
                                fields=['name', 'practitioner_name', 'employee','employee_name', 'template', 'creation'])

    # Dictionary to group tests by date, practitioner, employee, and template
    grouped_tests = defaultdict(lambda: defaultdict(lambda: {
        "normal_tests": [],
        "descriptive_tests": [],
        "organism_tests": []
    }))

    # Iterate through the fetched lab tests
    for test in lab_tests:
        lab_test_doc = frappe.get_doc('Lab Test', test['name'])
        test_date = test['creation'].date()  # Extract date from 'creation' timestamp

        # Group by date, practitioner_name, employee, and template
        key = f"{test_date}-{test['practitioner_name']}-{test['employee']}-{test['template']}"

        # Fetch normal test items
        for normal_test in lab_test_doc.get('normal_test_items', []):
            grouped_tests[str(test_date)][key]["normal_tests"].append({
                "lab_test_name": normal_test.lab_test_name,
                "result_value": normal_test.result_value,
                "practitioner_name": test.get('practitioner_name'),
                "employee": test.get('employee'),
                "employee_name": test.get('employee_name'),
                "template": test.get('template')
            })
        
        # Fetch descriptive test items
        for descriptive_test in lab_test_doc.get('descriptive_test_items', []):
            grouped_tests[str(test_date)][key]["descriptive_tests"].append({
                "lab_test_particulars": descriptive_test.lab_test_particulars,
                "result_value": descriptive_test.result_value,
                "practitioner_name": test.get('practitioner_name'),
                "employee": test.get('employee'),
                "employee_name": test.get('employee_name'),
                "template": test.get('template')
            })

        # Fetch organism test items
        for organism_test in lab_test_doc.get('organism_test_items', []):
            grouped_tests[str(test_date)][key]["organism_tests"].append({
                "organism": organism_test.organism,
                "colony_population": organism_test.colony_population,
                "practitioner_name": test.get('practitioner_name'),
                "employee": test.get('employee'),
                "employee_name": test.get('employee_name'),
                "template": test.get('template')
            })

    # Compile the result, grouping by patient and then by date, practitioner, employee, and template
    result = {
        "patient_details": {
            "age": patient_reg.age_summary,
            "name": patient_doc.patient_name,
            "sex": patient_doc.sex,
        },
        "lab_tests_grouped": grouped_tests
    }

    return result
