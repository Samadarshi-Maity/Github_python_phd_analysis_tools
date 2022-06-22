# created by @ Samadarshi ~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~import the essentials 
# import os for norming the path
import os.path
# importnumpy for manipulation
import numpy as np 
# Now call in the pandas 
import pandas as pd  
# import the h5py for reading v7.3 .mat versions of files  
import h5py
# import the file subsystem reading package 
import glob 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# define the function to read all the values of across densities
# important updates that ned to be done
'''
Params:
1. Place all the .mat files into a single folder and pass the folde rpath to this function
2. Keep the sequence of name very consistent to the trend that you want to study
3. This function read the bindata and returns a master array containing the bin data of all the .mat files
'''
def cumulative_bin_data(mainPath, voltage):
    
    # Check what voltages you need 
    if (voltage == 0):
        A = '\*.mat';
    else:
        str1 = r'\*';
        str3 = r'*.mat';
        str2 = str(140);
        A = str1 + str2 + str3;
        
    # Set up the file calling protocols
    file_name_list = glob.glob(mainPath + A); 
    mainPath  = os.path.normpath(mainPath).replace('\\','/')

    #file_name_list = glob.glob(mainPath + '\*140*.mat');   # this should be the code if you want some voltage 
    file_name_list = glob.glob(mainPath + '\*.mat');   

    # convert all the file path into the standard interpretable formats
    File_path_list = [];
    for file_path in file_name_list:
        File_path_list.append(os.path.normpath(file_path).replace('\\','/'))

    # read the data from each .mat file and save it in a dictonary     
    master_array = pd.DataFrame();       # main dataset 
    temporary_data_set = pd.DataFrame(); # read the chunks 

    # specif the name of the headings of the table
    table_names = ['fileID','#_fraction','$\Pi$','V$_0$','$\rho$','centres'];

    serial_number = 0;
    for file_path in File_path_list:

        serial_number += 1; 
        # extract the data from each file
        f = h5py.File(file_path, 'r')
        MATLAB_data = {}
        for k, v in f.items():
            MATLAB_data[k] = np.array(v)
        '''
        MATLAB_data has dat in the following order:
        1. fraction of particle in the bin
        2. Bin averaged polarization
        3. Bin averaged velocity
        4. Bin averaged number density
        5. Bin centres in the radial directions
        '''  
        # set the fist ID to the serial of the fil that your are reading from the folder of he .mat files.
        temporary_data_set[table_names[0]] = serial_number*np.ones(len(MATLAB_data['binData'][0]));

        # fill te other columns with the data from the dats of the other columns of bin data 
        for i in range(len(MATLAB_data['binData'])):
            temporary_data_set[table_names[i+1]] = MATLAB_data['binData'][i]

        # keep adding the read data into the master array 
        master_array = pd.concat([master_array,temporary_data_set]) 

    return master_array


# Define a function to clean the velocity vector
def vortex_data_ETL(matrix_path, v_cutoff):
    # Initialise the dataframes 
    XY_vector = pd.DataFrame();
    
    f = h5py.File(matrix_path, 'r')
    MATLAB_data = {}
    for k, v in f.items():
        MATLAB_data[k] = np.array(v)
    
    #  build the pandas dataframe
    c = 0;
    for i in['X','Y','R','$\theta$','Vx','Vy','V$_0$','V$_r$',r'V$_\varphi$']:
        XY_vector[i] = (MATLAB_data['XY_vector'])[c];
        c +=1;
    
    # apply velocity cutoff
    XY_vector = XY_vector[XY_vector['V$_0$']>v_cutoff];
    return XY_vector



# perform the statistical averzging for the data sets
def Compute_Bin_data(XY_vector, particle):
    
    # denfine the bin edges
    edges = np.linspace(1,600,16);
    
    # create another column with the BIN IDs
    XY_vector['binID'] = np.digitize(XY_vector['R'], edges, right=False)
    
    # Create a new table of bin data with the mean of all th ebin means of all columns in XY_vector
    binData = XY_vector.groupby(by=['binID']).mean()
    
    # define the edges and the elementary area and the central value of R
    R_bins = np.insert((binData['R']).values,0,0)
    dA = 0.5*( R_bins[1:]**2 - R_bins[:-1]**2)  
    
    # define the centre for each bin.
    binData['centre'] = 0.5*(R_bins[1:] + R_bins[:-1])

    # Comopute the mean polarisation in each bin 
    binData[r'$\Pi_{\varphi}$'] = np.sqrt((binData['V$_r$']/binData['V$_0$'])**2 + (binData[r'V$_\varphi$']/binData['V$_0$'])**2)
    
    # compute the density in area fraction within each bin.
    binData['$\rho$'] = XY_vector.groupby(by=['binID']).size()/(dA*42480)*(np.pi*(particle/0.8621)**2)
    
    return binData 