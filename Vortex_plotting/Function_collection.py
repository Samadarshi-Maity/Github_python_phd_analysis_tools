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