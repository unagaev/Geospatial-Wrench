#!/usr/bin/env python
# coding: utf-8

# In[6]:


import os
import glob
import json
import geopandas as gpd
from osgeo import gdal, ogr, osr


# In[7]:


#Set your working dir, create the folders for output png, tif masks and matched copies of your satellite images.
#Run the cell once! If needed, clean the folders from the files


#md_folder = r'C:\Deepplanet\Projects\Crops\Vineyards\Vineyards_other_australia\Riverine_Vineyards\Riverina_masks_matched_res/'
#md_folder = r'C:\Deepplanet\Projects\Tasks_students_crop\Lavender/'
#md_folder = os.path.normpath(r'C:/Deepplanet/Oregon_Vineyards/Masks_for_Ira/')
#md_folder = os.path.normpath(r'C:\Deepplanet\Projects\Crops\Lavender\Masks/') +'/'
#md_folder = os.path.normpath(r'C:\Deepplanet\Projects\Crops\Almonds\Almonds_CA/Masks/') + '/'
#md_folder = os.path.normpath(r'C:\Deepplanet\Projects\Crops\Almonds\Almonds_CA\Sentinel_Images\Almonds_Kern_Masks\Polygons\sentinel/') + '/'
#md_folder = os.path.normpath(r'C:\Deepplanet\Projects\Crops\Vineyards\Vines/') + '/'
#md_folder = os.path.normpath(r'C:\Deepplanet\Projects\Crops\Barley/') + '/'
#md_folder = os.path.normpath(r'C:\Deepplanet\Projects\Crops\Almonds\Almonds_Morocco_Sentinel\masks/') + '/'
#md_folder = os.path.normpath(r'C:\Deepplanet\Projects\Crops\Lavender\Masks_v2_France/') + '/'
#md_folder = os.path.normpath(r'D:\Dobrich-2019_Sentinel\July_Chunks/') + '/'
#md_folder = os.path.normpath(r'C:\Deepplanet\Projects\!OurPapers\Methodological approaches (paper)\Data\training\satellite_images_for_search\almonds_aus_search/') + '/'
#md_folder = os.path.normpath(r'C:\Deepplanet\Projects\Crops\Vineyards\NY\Polygons_from_Ira\NY_sentinel_img/') + '/'
md_folder = os.path.normpath(r'C:\Deepplanet\Projects\Crops\Vineyards\NY\Polygons_from_Ira\v2\Masks_NY_img_v4/') + '/'
#md_folder = os.path.normpath(r'C:\Deepplanet\!OurPapers\Methodological approaches (paper)\Data') + '/'


tif_folder = md_folder +  'tif/'
if not os.path.exists(tif_folder):
    os.makedirs(tif_folder)
png_folder = md_folder +  'png/'
if not os.path.exists(png_folder):
    os.makedirs(png_folder)


# In[9]:


md_folder


# In[10]:


# Set the path to the folder with the sat images you use for coordinate extraction and read the feature file (.shp, .geojson) to rasterize
img_path = md_folder + '/sentinel/'

shape = glob.glob(md_folder)[0]
#input_shp = ogr.Open(md_folder+"vineyards_australia_grape_Riverina_combined_4326.geojson.shp")
#input_shp = ogr.Open(md_folder+"/Oregon_Vineyards_2023_Shp_2205_R_py.shp")
#input_shp = ogr.Open(md_folder+"/Lavender_France_2020.shp")
#input_shp = ogr.Open(md_folder+"/Vine_Penley_Individual_full.shp")
#input_shp = ogr.Open(md_folder+"/Barley-2019.geojson")
#input_shp = ogr.Open(md_folder+"/Almonds_Morocco.geojson")
#input_shp = ogr.Open(md_folder+"/Almond_California.shp")
#input_shp = ogr.Open(md_folder+"/Lavender_France_2020.shp")
input_shp = ogr.Open(md_folder+"/NY_Vineyards_Branchport&Portland_v2.geojson")
#input_shp = ogr.Open(md_folder+"/Almond_California.shp")
in_layer = input_shp.GetLayer()
in_layer_defn = in_layer.GetLayerDefn()
in_layer.GetFeatureCount()


# In[11]:


def vector2raster(input_shp, tree):
    """
   The function reads the feature .shp/.geojson file and rasterizes the objects into bit masks with the value 1 burned over the objects places.
    Your shapefile must contain the column "Class_Tree" with the name of the objects' you prepare masks for 
    (e.g Frankincense and Non-frankincense) or create a new column "Type_Tree" if you want to rasterize all objects inside the shapefile with the value 'ALL'
    
    In addition your shapefile must contain the column "Id_Copy" with the value=1 for all objects inside the shapefile you want to burn over the mask.
    The objects with Null values or any another will not be burned.
    
    You'll find the masks in png and tif folders with the names, ending with Red for a red variety and White for a white one.
    You'll find the MD with coordinates of ul and lr corners of the masks created, as a .json in your md_folder 
    """
    d = {}
    counter = 0
    for i in os.listdir(img_path):
        if i.endswith('.tif') or i.endswith('.tiff'):
            
            gdal.UseExceptions()
            img = gdal.Open(img_path+i, gdal.GA_ReadOnly)
            img_arr = img.ReadAsArray()
            img_name = os.path.split(img.GetDescription())[1]
 
            proj = img.GetProjectionRef()
            ext  = img.GetGeoTransform()
    
            ext1  = ext[0], ext[1], ext[2], ext[3], ext[4], ext[5]
        
            img_ncol = img_arr.shape[2]
            img_nrow = img_arr.shape[1]
            shp_name = os.path.split(input_shp.GetDescription())[1]
            print(img_name)
            
            # Let's open the shapefile with masked objects
            in_layer = input_shp.GetLayer()
            in_layer_defn = in_layer.GetLayerDefn()

            if tree != 'ALL':
                in_layer.SetAttributeFilter(f"Class_Tree = '{tree}'") # filter drawn shapefile objects by tree type, e.g. 'F' or 'NF'
            else:
                in_layer.SetAttributeFilter(f"Type_Tree = '{tree}'") # just creates a mask for all trees

            # Set the need pixel extent of your future raster mask, according to the image resolution
            ulx, xres, uly, yres = ext[0], ext[1], ext[3], ext[5]
            
            # Set the upper-left corner coordinates and a resolution of your future raster mask: y with minus sign
            lrx = ulx + (img_ncol * xres)
            lry = uly + (img_nrow * yres)

            bbox = (ulx, uly, lrx, lry)
            print(bbox)
            ext1  = ext[0], ext[1], ext[2], ext[3], ext[4], ext[5]

            # Create the dict to keep your mask coordinates in
            d[f'mask_{img_name[:-4]}_{tree}'] = [(bbox[0], bbox[1]), (bbox[2], bbox[3])]

            # Create the template for the output mask geotif image
            driver = gdal.GetDriverByName('GTiff')
            #out_raster_ds = driver.Create(tif_folder + f'/{tree}/'+ f'mask_{img_name[:-4]}_{tree}.tif', img_ncol, img_nrow, 1, gdal.GDT_Byte)
            out_raster_ds = driver.Create(tif_folder + f'/mask_{img_name[:-4]}_{tree}.tif', img_ncol, img_nrow, 1, gdal.GDT_Byte)

            out_raster_ds.SetProjection(proj)
            out_raster_ds.SetGeoTransform(ext1)
            nodata = out_raster_ds.GetRasterBand(1)
            nodata.Fill(0)
            
            # Rasterise our shapefile. It requires 1 and 0 values in Id_Copy column inside a shapefile's attribute.
            gdal.RasterizeLayer(out_raster_ds, [1], in_layer, None, None, [0], ['ALL_TOUCHED=False', 'ATTRIBUTE=Id_Copy'])
            mask_coords = out_raster_ds.GetGeoTransform()
            mask_raster = out_raster_ds
            out_raster_ds = None
            
            # Convert tif to 1-bit png mask
            options_list = ['-co NBITS=1', '-ot Byte', '-of PNG']
            options_string = " ".join(options_list)
            #mask_png = gdal.Translate(png_folder + f'/{tree}/'+ f'mask_{img_name[:-4]}_{tree}.png', mask_raster, options=options_string)
            mask_png = gdal.Translate(png_folder + f'/mask_{img_name[:-4]}_{tree}.png', mask_raster, options=options_string)
            mask_raster = None
        
            # Write the metadata for the png
            print(f'Image {counter} processing...complete')
            counter += 1
    with open(md_folder+f'MD_{tree}.json', 'a', encoding='utf-8') as md:
        json.dump(d, md, ensure_ascii=False, indent=4)


# In[12]:


# Run this cell if you want just to create a mask for all features from the shapefile to be masked (column Type with the value ALL inside the .shp attributes needed)
tree_species = 'ALL'
print('Tree type: ', tree_species)
for i in os.listdir(md_folder):
    if i.endswith('NY_Vineyards_Branchport&Portland_v2.geojson'):
    #if i.endswith('.geojson') or i.endswith('.shp'):
        vector2raster(input_shp, tree_species)


# In[42]:


tree_species = 'Vines' # 'White'
print('Tree type: ', tree_species)
vector2raster(input_shp, tree_species)


# In[6]:


#The function for rasterizing masks for red/white grapes' vineyard blocks
#Run firstly with the tree species='Red'; after that, change it to 'White'!
tree_species = 'White'
print('Tree type: ', tree_species)
vector2raster(input_shp, tree_species)


tree_species = 'Red'
print('Tree type: ', tree_species)
vector2raster(input_shp, tree_species)


# In[ ]:


del 


# In[ ]:





# In[ ]:





# In[42]:


# Function to check the extent of your shapefile
import os
import glob
import json
from osgeo import gdal, ogr, osr


d = {}
for i in os.listdir(md_folder):
    if i.endswith('.geojson') or i.endswith('.shp'):
        
        input_shp = ogr.Open(md_folder + i)
        in_layer = input_shp.GetLayer()
        ext = [(in_layer.GetExtent()[1], in_layer.GetExtent()[3]), (in_layer.GetExtent()[0], in_layer.GetExtent()[2])]
        d[os.path.split(input_shp.GetDescription())[1]] = ext


# In[43]:


d


# In[34]:


# Code to check the spatial extent of your shapefile and write it into a json
import os
import json
from osgeo import ogr

"""
Set the path to the folder with your vector files
"""
md_folder = r'C:\Deepplanet\Projects\Crops\Vineyards\Vineyards_other_australia\Riverine_Vineyards\Riverina_new_masks/shp/'
d = {}
for i in os.listdir(md_folder):
    if i.endswith('.geojson') or i.endswith('.shp'):
        
        input_shp = ogr.Open(md_folder + i)
        in_layer = input_shp.GetLayer()
        in_layer.GetExtent()
        ext = [(in_layer.GetExtent()[0], in_layer.GetExtent()[3]), (in_layer.GetExtent()[1], in_layer.GetExtent()[2])]
        d[os.path.split(input_shp.GetDescription())[1]] = ext

with open(md_folder+f'MD_AOI.json', 'w', encoding='utf-8') as md:
    json.dump(d, md, ensure_ascii=False, indent=4)
    
f = open(md_folder+f'MD_AOI.json')
d = json.load(f)


# In[38]:


d


# In[12]:


f = open('C:/Users/rost8/Downloads' + '/Dalwhinnie.json', encoding="utf8")
d = json.load(f)


# In[15]:


f = open('C:/Deepplanet/Oregon_Vineyards/Masks_for_Ira/MD_ALL.json', encoding="utf8")
d = json.load(f)


# In[16]:


d['mask_OR_230_2021-07-05_18-51-46_ALL']


# In[18]:


d['layers'][1]['paths']


# In[19]:


d['layers'][2]['paths']


# In[20]:


d['layers'][3]['paths']


# In[ ]:




