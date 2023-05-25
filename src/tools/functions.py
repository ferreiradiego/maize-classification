import os
import cv2
import numpy as np
import pandas as pd
import random
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, ConfusionMatrixDisplay, accuracy_score
import matplotlib.pyplot as plt


def remove_background_hsv(img_hsv):
    # Create a mask where the H channel is less than 50
    mask = img_hsv[:, :, 0] < 50
    # Multiply all channels by the mask to remove the background
    img_hsv *= mask[:, :, np.newaxis]

    return img_hsv

def crop_image(img, x_start, x_end, y_start, y_end):
    
    if x_start < 0:
        x_start = 0
    if y_start < 0:
        y_start = 0

    return img[x_start:x_end, y_start:y_end, :]

def convert_images(bgr_img, flag_remove_background = False):
    
    hsv_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV) 

    if flag_remove_background:
        hsv_img = remove_background_hsv(hsv_img)
        bgr_img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)

    gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)

    return bgr_img, hsv_img, gray

def read_all_images_filenames(path):
    image_filenames = [filename for filename in os.listdir(path) if filename.endswith('.jpg')]
    return image_filenames

def divide_dataset(image_filenames, train_ratio):

    random.shuffle(image_filenames)

    train_filenames = image_filenames[:int(train_ratio * len(image_filenames))]
    test_filenames = image_filenames[int(train_ratio * len(image_filenames)):]

    return train_filenames, test_filenames

def create_dataframes(filenames, path_to_images):
    
    dfs_gray = []
    for file_name in filenames:
        img_gray = cv2.imread(path_to_images + file_name, cv2.IMREAD_GRAYSCALE)

        defect_percentage = {'a1_': 0.30, 'a2_': 0.25, 'a3_': 0.20, 'a4_': 0.15, 'a5_': 0.10}.get(file_name[:3], 0.00)

        mask1 = cv2.inRange(img_gray, 1, 80)
        mask2 = cv2.inRange(img_gray, 80, 256)

        npixels_1to255, npixels_1to80, npixels_80to255 = cv2.countNonZero(mask1 | mask2), cv2.countNonZero(mask1), cv2.countNonZero(mask2)

        grain_quantity = int(file_name.split("_")[1])

        new_row_gray = {'image_name': file_name, 'grain_quantity': grain_quantity, 'defect_percentage': defect_percentage,
                        'npixels_1to255': npixels_1to255, 'npixels_1to80': npixels_1to80, 'npixels_80to255': npixels_80to255}
        dfs_gray.append(pd.DataFrame(new_row_gray, index=[0]))

    df_gray = pd.concat(dfs_gray, ignore_index=True)

    df_gray['ratio_80to255_by_1to80'] = df_gray['npixels_80to255']/df_gray['npixels_1to80']
    ratio_good = df_gray.loc[df_gray['defect_percentage'] == 0.00, 'ratio_80to255_by_1to80'].mean()
    df_gray['ratio_80to255_by_1to80'] /= ratio_good

    df_gray['npixels_1to255_per_grain'] = (df_gray['npixels_1to255']/df_gray['grain_quantity']).astype(int)

    return df_gray

def normalize_dataset(df_train, df_test, feature_name, ratio_to_be_filtered = 0.0):

    good_grain_stats = df_train.query('defect_percentage == 0.0')[feature_name].agg(['mean', 'std'])

    df_train[f'normalized_{feature_name}'] = abs(good_grain_stats['mean'] - df_train[feature_name])/good_grain_stats['std']
    df_test[f'normalized_{feature_name}'] = abs(good_grain_stats['mean'] - df_test[feature_name])/good_grain_stats['std']
    
    if ratio_to_be_filtered != 0.0:
        df_train.loc[df_train['defect_percentage'] == 0, :] = df_train.query(f'normalized_{feature_name} < {ratio_to_be_filtered}')
        df_test.loc[df_test['defect_percentage'] == 0, :] = df_test.query(f'normalized_{feature_name} < {ratio_to_be_filtered}')

        df_train = df_train.dropna()
        df_test = df_test.dropna()

    return df_train, df_test

def summarize_train_data(df_train, groupby_cols=['grain_quantity', 'defect_percentage'], summary_col='normalized_ratio_80to255_by_1to80'):
    return df_train.groupby(groupby_cols)[summary_col].describe()[['mean', 'std']].reset_index()

# Define a function to calculate the average number of pixels with values between 1 and 255 per grain
def calculate_avg_pixels_per_grain(df):
    # Query the DataFrame to get only the grains with 0% defects
    df_good_grains = df.query('defect_percentage == 0.0')
    # Calculate the mean number of pixels with values between 1 and 255 per grain
    avg_pixels_1a255_per_grain = df_good_grains['npixels_1to255_per_grain'].mean()
    # Return the result
    return avg_pixels_1a255_per_grain

def calculate_number_of_grains(npixels, grain_avg):
    return int(npixels / grain_avg)

def estimate_number_of_grains(calculated):

    if calculated < 54:
        return 50
    if calculated < 64:
        return 60
    if calculated < 74:
        return 70
    if calculated < 84:
        return 80
    if calculated < 94:
        return 90

    return 100

def estimate_defect_percentage(grain_quantity, ratio, model):

    diff = abs(model.query(f'grain_quantity == {grain_quantity}')['mean'] - ratio)
    min_index = diff.idxmin()

    return model.loc[min_index, 'defect_percentage']

def check_quality(percent, threshold = 0.15):
    if percent <= threshold:
        # bom
        return 1 
    
    # ruim
    return 0

def generate_confusion_matrix_and_classification_metrics(classification_results_df: pd.DataFrame, class_names: str, classification_type='n_grains'):

    if classification_type == 'n_grains':
        # Obtain the actual and predicted values for grains
        y_true = classification_results_df['grain_quantity'].copy()
        y_pred = classification_results_df['estimated_grain_quantity'].copy()

    elif classification_type == 'defect_stratified':

        df = classification_results_df.loc[classification_results_df['error_grain'] == 0.0, :].copy()
        
        # Obtain the actual and predicted values for defects percentage
        y_true = (df['defect_percentage'] * 100).copy().astype(int)
        y_pred = (df['estimated_defect_percentage'] * 100).copy().astype(int)

    elif classification_type == 'defect_thresholded':

        df = classification_results_df.loc[classification_results_df['error_grain'] == 0.0, :].copy()

        y_true = df['quality'].copy()
        y_pred = df['estimated_quality'].copy()
        
    else:
        raise ValueError("Invalid classification_type parameter. Must be 'grains' or 'defects'.")

    cm = confusion_matrix(y_true, y_pred, normalize='true')

    classification_report_dict = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)

    return cm, classification_report_dict


def export_classification_report_latex_style(classification_metrics_results):
    df = pd.DataFrame(classification_metrics_results).transpose()
    df.loc[:, 'precision':'f1-score'] = df.loc[:, 'precision':'f1-score'].round(2)
    df['support'] = df['support'].astype(int)

    print(df.to_latex(index=False))
    print(df.style.to_latex())
    # display(df)

def export_confusion_matrix_as_image(confusion_matrix: np.ndarray, class_names: list, image_name: str, labels: list):

    cm_df = pd.DataFrame(confusion_matrix, columns=class_names, index=class_names)

    cm_df = cm_df.round(2)

    # plot confusion matrix using seaborn heatmap
    plt.figure(figsize=(6,4))
    sns.set(font_scale=1.2)
    # Values for cmap: plasma, viridis, inferno, magma, coolwarm, YlGnBu, Greens, Reds, Oranges
    sns.heatmap(cm_df, annot=True, fmt='g', cmap='YlGnBu', cbar=False)
    plt.xlabel(labels[0])
    plt.ylabel(labels[1])

    plt.savefig(f'{image_name}', dpi=300, bbox_inches='tight')

    plt.close()

def cross_validation(train_ratio: list, thresh_good: list, classification_types: dict, iterations: range, classification_metrics_results: dict, confusion_matrices: dict):

    for ratio in train_ratio:    
        for thresh in thresh_good:
            for classification_type in classification_types:

                sum_cmr_df = pd.DataFrame()
                sum_cm = 0

                for iteration in iterations:

                    sum_cmr_df = sum_cmr_df.add(pd.DataFrame(classification_metrics_results[ratio][thresh][classification_type][iteration]), fill_value=0)

                    sum_cm += confusion_matrices[ratio][thresh][classification_type][iteration]

                classification_metrics_results[ratio][thresh][classification_type].update({'mean': (sum_cmr_df/len(iterations)).to_dict()})

                confusion_matrices[ratio][thresh][classification_type].update({'mean': (sum_cm/len(iterations))})

    return classification_metrics_results, confusion_matrices


def export_all_confusion_matrices_images(train_ratio: list, thresh_good: list, classification_types: dict, iterations: range, confusion_matrices: dict, base_path: str, labels: list):
    for ratio in train_ratio:    
        for thresh in thresh_good:
            for classification_type in classification_types:
                for iteration in iterations:
                    image_name = f'{base_path}/confusion_matrix/{classification_type}/{int(ratio*100)}_{int(thresh*100)}_{iteration}.png'
                    cm = confusion_matrices[ratio][thresh][classification_type][iteration]
                    export_confusion_matrix_as_image(cm, classification_types[classification_type], image_name, labels)
