import ee
import geemap

# Initialize the Earth Engine API
# Uncomment ee.Authenticate() if this is your first time running GEE on this machine
# ee.Authenticate()
ee.Initialize()

Map = geemap.Map()
Map.add_basemap("Satellite")

# 1. Define the Region of Interest (Kolkata)
dataset = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level2")
roi = dataset.filter(ee.Filter.eq('ADM2_NAME', 'Kolkata'))
Map.centerObject(roi, 11)

# =====================================================================
# 2. AUTOMATED TRAINING DATA GENERATION (CORRECTED)
# =====================================================================

# Load the highly accurate ESA WorldCover dataset (2021)
esa = ee.ImageCollection("ESA/WorldCover/v200").first().clip(roi)

# Grouping ESA classes into our 4 categories:
# Vegetation (10:Trees, 20:Shrub, 30:Grass, 40:Crop) -> 0
# Urban (50:Built-up) -> 1
# Soil (60:Bare) -> 2
# Water (80:Water) -> 3
esa_remapped = esa.remap(
    [10, 20, 30, 40, 50, 60, 80], 
    [ 0,  0,  0,  0,  1,  2,  3]
).rename('class')

# Drop 1,500 random coordinate points inside Kolkata
random_points = ee.FeatureCollection.randomPoints(region=roi, points=1500)

# Extract the land cover class. 
training_points = esa_remapped.sampleRegions(
    collection=random_points,
    scale=10,            
    geometries=True      
)

# =====================================================================
# 3. LANDSAT PROCESSING, TRAINING, AND VALIDATION
# =====================================================================

bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'NDVI']

def prep_image(image):
    ndvi = image.normalizedDifference(['B5', 'B4']).rename('NDVI')
    qa = image.select('QA_PIXEL')
    cloud_mask = qa.bitwiseAnd(1 << 3).eq(0)
    return image.addBands(ndvi).updateMask(cloud_mask)

def process_and_validate(start_date, end_date, year_label):
    # Fetch and preprocess Landsat image
    img = (ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA')
           .filterDate(start_date, end_date)
           .filterBounds(roi)
           .map(prep_image)
           .median()
           .select(bands))

    # Sample the Landsat imagery at our automated training points
    sampled_data = img.sampleRegions(
        collection=training_points,
        properties=['class'],
        scale=30
    )

    # Split the data into 80% Training / 20% Testing
    sampled_data_with_random = sampled_data.randomColumn('random')
    split_ratio = 0.8
    
    training_set = sampled_data_with_random.filter(ee.Filter.lt('random', split_ratio))
    testing_set = sampled_data_with_random.filter(ee.Filter.gte('random', split_ratio))

    # Train classifier ONLY on the training set
    classifier = ee.Classifier.smileRandomForest(50).train(training_set, 'class', bands)

    # Validate accuracy by classifying the UNSEEN testing set
    test_classified = testing_set.classify(classifier)
    error_matrix = test_classified.errorMatrix('class', 'classification')

    # Force execution to pull the matrix down to Python terminal
    print(f"--- {year_label} Validation Results ---")
    print("Confusion Matrix:")
    print(error_matrix.getInfo())
    print(f"Overall Accuracy: {error_matrix.accuracy().getInfo():.4f}\n")

    # Classify the entire image for the map
    classified_img = img.classify(classifier)

    # Visualization Layer Configs
    class_palette = {'min': 0, 'max': 3, 'palette': ['green', 'red', 'saddlebrown', 'blue']}
    ndvi_palette = {'min': 0, 'max': 1, 'palette': ['red', 'yellow', 'green']}
    
    Map.addLayer(img.select('NDVI'), ndvi_palette, f'NDVI {year_label}')
    Map.addLayer(classified_img, class_palette, f'Land Cover {year_label}')
    return classified_img

# Execute pipeline for both target years
classified22 = process_and_validate('2016-10-01', '2016-12-31', '2016')
classified23 = process_and_validate('2022-10-01', '2022-12-31', '2022')

Map.addLayerControl()

# =====================================================================
# 4. EXPORT RESULTS TO GOOGLE DRIVE
# =====================================================================

def export_to_drive(image, description, region):
    task = ee.batch.Export.image.toDrive(
        image=image.clip(region), 
        description=description,
        folder='GEE_Exports',
        fileNamePrefix=description,
        region=region.geometry(),
        scale=30,
        maxPixels=1e13
    )
    task.start()
    print(f"✅ Export task started for: {description}")

# Trigger asynchronous background tasks on the GEE servers
export_to_drive(classified22.toUint8(), 'Kolkata_LC_2016', roi)
export_to_drive(classified23.toUint8(), 'Kolkata_LC_2022', roi)