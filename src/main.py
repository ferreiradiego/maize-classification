## --- Import the packages and functions
from tools.functions import *
import pickle

## --- Definitions, parameters and directory paths
# Define the base path for your images
base_path       = '../img'

# Define the path to your dataset within the base path and using gray images
dataset_path    = f'{base_path}/dataset/gray/'

# List of ratios to be used for splitting the dataset into training and testing sets
train_ratio     = [0.75, 0.8, 0.85, 0.9]

# Threshold for normalizing the image data
thresh_normalization = 0.500

# List of thresholds to be considered 'good' in evaluation
thresh_good     = [0.00, 0.10, 0.15]

# Range of iterations to be performed during model training
iterations      = range(1, 6)

# Define different classification types for the model to learn. Each type is associated with a list of categories.
classification_types = {'n_grains': ['50', '60', '70', '80', '90', '100'], 
                        'defect_stratified': ['0%', '10%', '15%', '20%', '25%', '30%'], 
                        'defect_thresholded': ['With defects', 'Healthy']}

# Define labels for the x and y axes in plotting
x_label = 'Predicted'
y_label = 'True'

## ---

# Read all image filenames in the directory specified in dataset_path
image_filenames = read_all_images_filenames(dataset_path)

# Initialize an empty DataFrame for storing training data
df_train                    = pd.DataFrame()

# Initialize an empty DataFrame for storing testing data
df_test                     = pd.DataFrame()

# Initialize an empty DataFrame for storing model's training data
df_train_model              = pd.DataFrame()

# Initialize an empty DataFrame for storing classification results
classification_results_df   = pd.DataFrame()

# Initialize a nested dictionary for storing classification metrics results. 
# The structure is organized first by training ratio, then by threshold, and finally by classification type
classification_metrics_results = {
    ratio: {
        thresh: {
            classification_type: {} for classification_type in classification_types
        } for thresh in thresh_good
    } for ratio in train_ratio
}

# Initialize a nested dictionary for storing confusion matrices. 
# The structure is similar to that of classification_metrics_results
confusion_matrices = {
    ratio: {
        thresh: {
            classification_type: {} for classification_type in classification_types
        } for thresh in thresh_good
    } for ratio in train_ratio
}


# Perform the procedure for all specified training/testing percentages, thresholds to consider good grains, and the number of iterations for each set
for ratio in train_ratio:           
    for thresh in thresh_good:
        for iteration in iterations:

            df_train                    = pd.DataFrame()
            df_test                     = pd.DataFrame()
            df_train_model              = pd.DataFrame()

            # Divide the dataset into train and test sets with the specified ratio
            train_filenames, test_filenames = divide_dataset(image_filenames, ratio)

            # Create dataframes for the train and test sets using the filenames and images in the specified directory
            df_train = create_dataframes(train_filenames, dataset_path)
            df_test = create_dataframes(test_filenames, dataset_path)

            # Normalize the 'ratio_80to255_by_1to80' feature in the train and test datasets. The normalization threshold is specified
            df_train, df_test = normalize_dataset(df_train, df_test, 'ratio_80to255_by_1to80', thresh_normalization)

            # Summarize the train dataframe by grouping it by grain_quantity and defect_percentage and calculating summary statistics to generate the model
            df_train_model = summarize_train_data(df_train)

            # Call the function to calculate the average number of pixels per grain for the training dataset
            avg_pixels_1a255_per_grain = calculate_avg_pixels_per_grain(df_train)

            # Calculate number of grains
            df_test['calculated_grain_quantity'] = df_test['npixels_1to255'].apply(calculate_number_of_grains, grain_avg = avg_pixels_1a255_per_grain)

            # Estimate number of grains (in discrete values predefined)
            df_test['estimated_grain_quantity'] = df_test['calculated_grain_quantity'].apply(estimate_number_of_grains)

            # Calculate the error between the actual and estimated values for the quantity of grains
            df_test['error_grain'] = df_test['estimated_grain_quantity'] - df_test['grain_quantity']

            # Estimate the percentage of defects in the test dataset based on the number of grains and ratio
            df_test['estimated_defect_percentage'] = df_test.apply(lambda row: estimate_defect_percentage(row['grain_quantity'], 
                                                                                                           row['normalized_ratio_80to255_by_1to80'], df_train_model), axis=1)

            # Calculate the error in the estimated defect percentage
            df_test['error_defects'] = df_test['estimated_defect_percentage'] - df_test['defect_percentage']

            # Select only the columns of interest to create a summarized dataframe with the classification results
            classification_results_df = df_test[['grain_quantity', 'defect_percentage', 'estimated_grain_quantity', 'estimated_defect_percentage', 'error_grain']].copy()

            # Check the quality (healthy or defective) according to the parameterized threshold
            classification_results_df['quality'] = classification_results_df['defect_percentage'].apply(check_quality, args=(thresh,)).astype(int)
            classification_results_df['estimated_quality'] = classification_results_df['estimated_defect_percentage'].apply(check_quality, args=(thresh,)).astype(int)
            
            # Iterate over each classification type and get the classification results
            for classification_type in classification_types:

                cm, cr = generate_confusion_matrix_and_classification_metrics(classification_results_df, classification_types[classification_type], classification_type)
                
                # Update the confusion matrix and classification metrics dictionaries
                confusion_matrices[ratio][thresh][classification_type].update({iteration: cm})
                classification_metrics_results[ratio][thresh][classification_type].update({iteration: cr})

# Apply a cross-validation by taking the average of the results obtained in each iteration
classification_metrics_results, confusion_matrices = cross_validation(train_ratio, thresh_good, classification_types, 
                                                                      iterations, classification_metrics_results, confusion_matrices)

# export_all_confusion_matrices_images(train_ratio, thresh_good, classification_types, iterations, confusion_matrices, base_path, [x_label, y_label])


# --- Export the results
with open("../resources/classification_metrics_results.pickle", "wb") as f:
    pickle.dump(classification_metrics_results, f)

with open("../resources/confusion_matrices.pickle", "wb") as f:
    pickle.dump(confusion_matrices, f)

df_test.to_pickle('../resources/df_test.pkl')
df_train.to_pickle('../resources/df_train.pkl')
df_train_model.to_pickle('../resources/df_train_model.pkl')
# ---