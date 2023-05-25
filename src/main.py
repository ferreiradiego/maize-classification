from tools.functions import *

base_path       = '..\img'
dataset_path    = f'{base_path}/dataset/gray/'
train_ratio     = [0.75, 0.8, 0.85, 0.9]
thresh_normalization = 0.500

thresh_good     = [0.00, 0.10, 0.15]
iterations      = range(1, 6)

classification_types = {'n_grains': ['50', '60', '70', '80', '90', '100'], 'defect_stratified': ['0%', '10%', '15%', '20%', '25%', '30%'], 'defect_thresholded': ['With defects', 'Healthy']}

x_label = 'Predicted'
y_label = 'True'





# Read all image filenames in the directory specified in dataset_path
image_filenames = read_all_images_filenames(dataset_path)

df_train                    = pd.DataFrame()
df_test                     = pd.DataFrame()
df_train_model              = pd.DataFrame()
classification_results_df   = pd.DataFrame()

classification_metrics_results = {
    ratio: {
        thresh: {
            classification_type: {} for classification_type in classification_types
        } for thresh in thresh_good
    } for ratio in train_ratio
}

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

            # Normalize the 'ratio_80a255_por_1a80' feature in the train and test datasets. The normalization threshold is specified
            df_train, df_test = normalize_dataset(df_train, df_test, 'ratio_80a255_por_1a80', thresh_normalization)

            # Summarize the train dataframe by grouping it by qtde_graos and percentual_defeitos and calculating summary statistics to generate the model
            df_train_model = summarize_train_data(df_train)

            # Call the function to calculate the average number of pixels per grain for the training dataset
            avg_pixels_1a255_per_grain = calculate_avg_pixels_per_grain(df_train)

            # Calculate number of grains
            df_test['qtde_graos_calculado'] = df_test['npixels_1a255'].apply(calculate_number_of_grains, grain_avg = avg_pixels_1a255_per_grain)

            # Estimate number of grains (in discrete values predefined)
            df_test['qtde_graos_estimado'] = df_test['qtde_graos_calculado'].apply(estimate_number_of_grains)

            # Calculate the error between the actual and estimated values for the quantity of grains
            df_test['erro_graos'] = df_test['qtde_graos_estimado'] - df_test['qtde_graos']

            # Estimate the percentage of defects in the test dataset based on the number of grains and ratio
            df_test['percentual_defeitos_estimado'] = df_test.apply(lambda row: estimate_defect_percentage(row['qtde_graos'], 
                                                                                                           row['ratio_80a255_por_1a80_normalizado'], df_train_model), axis=1)

            # Calculate the error in the estimated defect percentage
            df_test['erro_defeitos'] = df_test['percentual_defeitos_estimado'] - df_test['percentual_defeitos']

            # Select only the columns of interest to create a summarized dataframe with the classification results
            classification_results_df = df_test[['qtde_graos', 'percentual_defeitos', 'qtde_graos_estimado', 'percentual_defeitos_estimado', 'erro_graos']].copy()

            # Check the quality (healthy or defective) according to the parameterized threshold
            classification_results_df['qualidade'] = (classification_results_df['percentual_defeitos'].apply(check_quality, thresh)).astype(int)
            classification_results_df['qualidade_estimado'] = (classification_results_df['percentual_defeitos_estimado'].apply(check_quality, thresh)).astype(int)
            
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