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





