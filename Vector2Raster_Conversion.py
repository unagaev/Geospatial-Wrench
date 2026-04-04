#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import glob
#import matplotlib.pyplot as plt
from osgeo import gdal, ogr, osr


# In[ ]:


md_folder = r'path_to_your_images/'
if not os.path.exists(md_folder):
    os.makedirs(img_folder)
shp_chunk_folder = md_folder + 'shp_chunks/'
if not os.path.exists(shp_chunk_folder):    
    os.makedirs(shp_chunk_folder)
img_folder = md_folder + 'img/'
if not os.path.exists(img_folder):
    os.makedirs(img_folder)
tif_folder = md_folder +  'tif/'
if not os.path.exists(tif_folder):
    os.makedirs(tif_folder)
png_folder = md_folder +  'png/'
if not os.path.exists(png_folder):
    os.makedirs(png_folder)


# In[8]:


md_folder


# In[ ]:


img_path = md_folder
shape = glob.glob(md_folder)[0]
input_shp = ogr.Open(r'path_to_your_shapefile_with_drawings.shp')
in_layer = input_shp.GetLayer()
in_layer_defn = in_layer.GetLayerDefn()
in_layer.GetFeatureCount()


# In[ ]:


img_path = r'path_to_your_output_tif_files'


# In[ ]:


gdal.UseExceptions()

img = gdal.Open(img_path+'name_of_the_black_white_mask.tif', gdal.GA_ReadOnly)
img_arr = img.ReadAsArray()


# In[92]:


img_name = os.path.split(img.GetDescription())[1]

nm = img_name[0:2]
try:
    if isinstance(int(nm), int) == True:
        counter = nm[:]
    else:
        counter = nm[1]
except:
    counter = nm[0]
print('Image number is: ', counter)


# In[93]:


img_name


# In[16]:


# Extract the SRS, coordinates and spatial resolution
proj = img.GetProjectionRef()
ext  = img.GetGeoTransform()
proj


# In[95]:


ext


# In[96]:


ext1  = ext[0], ext[1], ext[2], ext[3], ext[4], ext[5]
#ext1  = ext[0], ext[1]/10, ext[2], ext[3], ext[4], ext[5]/10,


# In[97]:


ext1


# In[98]:


img_name


# In[99]:


img_ncol = img_arr.shape[2]
img_nrow = img_arr.shape[1]


# In[100]:


# Usage: set the path to your shp folder, either "shp_chunks_folder" or "input_shp"
def vector2raster(input_shp, tree):
    
    
    shp_name = os.path.split(input_shp.GetDescription())[1]
    print(shp_name)
    print(img_name)
    # Let's open the shapefile with masked objects
   
    in_layer = input_shp.GetLayer()
    in_layer_defn = in_layer.GetLayerDefn()
    
    if tree != 'ALL':
        in_layer.SetAttributeFilter(f"Class = '{tree}'") # filter drawn shapefile objects by tree type if it is 'F' or 'NF'
    else:
        in_layer.SetAttributeFilter(f"Type = '{tree}'") # just create a mask for all trees
    print(in_layer.GetFeatureCount())
    
    # Set the need pixel extent of your future raster mask, according to the image resolution
    ulx, xres, uly, yres = ext[0], ext[1], ext[3], ext[5]
    # Set the upper-left corner coordinates and a resolution of your future raster mask: y with minus sign

    lrx = ulx + (img_ncol * xres)
    lry = uly + (img_nrow * yres)
    
    bbox = (ulx, uly, lrx, lry)
    
    ext1  = ext[0], ext[1], ext[2], ext[3], ext[4], ext[5],
    # Create an image subset
    img_mask = gdal.Translate(img_folder + f'img_{shp_name[:-4]}_{counter}.tif', img, projWin = bbox)
    # Create the template for the output mask geotif image
    driver = gdal.GetDriverByName('GTiff')
    out_raster_ds = driver.Create(tif_folder + f'mask_{shp_name[:-4]}_{tree}_{counter}.tif', img_ncol, img_nrow, 1, gdal.GDT_Byte)
    out_raster_ds.SetProjection(proj)
    out_raster_ds.SetGeoTransform(ext1)
    nodata = out_raster_ds.GetRasterBand(1)
    nodata.Fill(0)
    # Rasterise our shapefile. It requires 1 and 0 values in Id_Copy column inside shapefile's attribute.
    gdal.RasterizeLayer(out_raster_ds, [1], in_layer, None, None, [0], ['ALL_TOUCHED=False', 'ATTRIBUTE=Id_Copy'])
    mask_coords = out_raster_ds.GetGeoTransform()
    mask_raster = out_raster_ds
    out_raster_ds = None
    # Convert tif to 1-bit png mask
    options_list = ['-co NBITS=1', '-ot Byte', '-of PNG']
    options_string = " ".join(options_list)
    mask_png = gdal.Translate(png_folder + f'mask_{shp_name[:-4]}_{tree}_{counter}.png', mask_raster, options=options_string)
    mask_raster = None
    img_mask_name = os.path.split(img_mask.GetDescription())[1]
    print(img_mask_name)
    # Write the metadata for the png
    with open(md_folder + 'MD.txt', 'a+') as md:
        md.write("###\nX, Y Coordinates and res in dd\n\n")
        md.write('###\n'+f'mask_{shp_name[:-4]}_{tree}_{counter}.png'+'\n')
        md.write('\n'+f'Covers the image {img_mask_name}'+'\n\n')
        md.write(f"ul = {ulx, uly}\n")
        md.write(f"lr = {lrx, lry}\n")
        md.write(f"x_res = {xres}, y_res = {yres}\n###")
    print('...complete')


# In[102]:


# Usage: specify the path to your shp folder, either "shp_chunks_folder" or "input_shp". Specify the tree_types either 'ALL', 'F', 'NF'
#tree_species = 'F'
tree_species = 'Red'
#tree_species = 'White'
print('Tree type: ', tree_species)
for i in os.listdir(md_folder):
    #if i.endswith('.shp') and i.startswith('Mask_2022'):
    #if i.endswith('.shp') and i.startswith('Mask'):
    if i.endswith('.shp'):
        vector2raster(input_shp, tree_species)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[17]:


# Usage: specify the path to your shp folder, either "shp_chunks_folder" or "input_shp". Specify the tree_types either 'ALL', 'F', 'NF'
tree_species = 'ALL'
print('Tree type: ', tree_species)
for i in os.listdir(md_folder):
    #if i.endswith('.shp') and i.startswith('Mask_2022'):
    #if i.endswith('.shp') and i.startswith('Mask'):
    if i.endswith('.shp'):
        vector2raster(input_shp, tree_species)

