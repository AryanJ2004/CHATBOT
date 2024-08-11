import json

# Step 1: Load JSON data
with open('predefined_answers.json', 'r') as file:
    data = json.load(file)

# Step 2: Prepare SQL file
sql_filename = 'predefined_answers.sql'

with open(sql_filename, 'w') as sql_file:
    sql_file.write("USE your_database;\n")  # Replace with your database name

    # Step 3: Generate SQL INSERT statements
    for question in data['questions']:
        patterns = question['patterns']
        responses = question['responses']
        
        for pattern in patterns:
            for response in responses:
                # Generate the SQL INSERT statement
                sql_statement = (
                    f"INSERT INTO predefined_answers (pattern, response) VALUES "
                    f"('{pattern}', '{response}');\n"
                )
                # Write the SQL statement to the file
                sql_file.write(sql_statement)

print(f"SQL file '{sql_filename}' generated successfully.")
 