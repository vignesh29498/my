import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import os
import joblib

# Define file paths
handoff_folder = '/content/drive/MyDrive/CITI/New1/Handoff'
icd_folder = '/content/drive/MyDrive/CITI/New1/ICD'
label_file_path = '/content/drive/MyDrive/CITI/New1/label_file.csv'

# Load label file
label_df = pd.read_csv(label_file_path)

def load_and_preprocess_data(handoff_file, icd_file, handoff_columns, icd_columns):
    # Load Handoff and ICD files
    handoff_df = pd.read_csv(handoff_file)
    icd_df = pd.read_csv(icd_file)
    
    # Select relevant columns
    handoff_df = handoff_df[handoff_columns]
    icd_df = icd_df[icd_columns]
    
    # Convert to string to handle alphanumeric values
    handoff_df = handoff_df.applymap(str)
    icd_df = icd_df.applymap(str)
    
    # Merge on Text_ID
    merged_df = pd.merge(handoff_df, icd_df, on='Text_ID', how='inner')
    
    # Separate features and target
    X = merged_df[handoff_columns[1:]]  # All handoff columns except Text_ID
    y = merged_df[icd_columns[1:]]  # All ICD columns except Text_ID
    
    # Flatten y for a simple model
    y = y.apply(lambda row: ' '.join(row.values), axis=1)
    
    return X, y

def train_model():
    X_train = pd.DataFrame()
    y_train = pd.Series(dtype=str)

    for index, row in label_df.iterrows():
        handoff_file = os.path.join(handoff_folder, row['Handoff_File'])
        icd_file = os.path.join(icd_folder, row['ICD_File'])
        handoff_columns = row['Handoff_Columns'].split()
        icd_columns = row['ICD_Columns'].split()
        
        X, y = load_and_preprocess_data(handoff_file, icd_file, handoff_columns, icd_columns)
        X_train = pd.concat([X_train, X], ignore_index=True)
        y_train = pd.concat([y_train, y], ignore_index=True)
    
    # Encode categorical variables
    le = LabelEncoder()
    X_train = X_train.apply(le.fit_transform)
    
    # Define model pipeline
    model = make_pipeline(TfidfVectorizer(), LogisticRegression())
    
    # Train model
    model.fit(X_train.astype(str).apply(lambda x: ' '.join(x), axis=1), y_train)
    
    
    # Save model
    joblib.dump(model, 'text_pattern_model.pkl')
    print("Model trained and saved as 'text_pattern_model.pkl'")

def predict_meanings(model, new_raw_file, output_file):
    # Load new raw file
    new_raw_df = pd.read_csv(new_raw_file)
    
    # Convert to string to handle alphanumeric values
    new_raw_df = new_raw_df.applymap(str)
    
    # Encode categorical variables
    le = LabelEncoder()
    X_test = new_raw_df.apply(le.fit_transform)
    
    # Predict
    predictions = model.predict(X_test.astype(str).apply(lambda x: ' '.join(x), axis=1))
    
    # Save predictions
    result_df = pd.DataFrame({
        'Text_ID': new_raw_df['Text_ID'],
        'Predicted_Meaning': predictions
    })
    result_df.to_csv(output_file, index=False)
    print(f"Predictions saved to '{output_file}'")

# Train the model
train_model()

# Example prediction
#model = joblib.load('text_pattern_model.pkl')
#predict_meanings(model, 'AIML/Handoff/Handoff_1.csv', 'AIML/Handoff/Handoff_1_predictions.csv')




model = joblib.load('text_pattern_model.pkl')
predict_meanings(model, '/content/drive/MyDrive/CITI/New1/Handoff/Handoff_1.csv', '/content/drive/MyDrive/CITI/New1/predictions.csv')
