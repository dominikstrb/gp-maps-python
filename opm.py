import numpy as np
import matplotlib.pyplot as plt

from scipy.ndimage import filters

def make_opm(size, sigma=4., k=2., alpha=1.):
    """ Generate an orientation preference map (to be used as a fake ground truth). 
     
    
    Args:
        size: dimensionality of the OPM is size x size
        sigma: std of the first gaussian filter
        k: k * sigma is the std of the second gaussian filter
        
    Returns:
        m: complex np.array with shape (size, size)
    """
    
    if isinstance(size, int):
        sx, sy = size, size
    else:
        sx, sy = size
    
    # generate white noise for real and imaginary map
    a = np.random.randn(sx, sy)
    b = np.random.randn(sx, sy)
    
    # apply difference of Gaussians filter to both maps
    a = alpha * filters.gaussian_filter(a, sigma) - alpha * filters.gaussian_filter(a, k * sigma)
    b = alpha * filters.gaussian_filter(b, sigma) - alpha * filters.gaussian_filter(b, k * sigma)
    
    # combine real and imaginary parts
    m = a + 1j * b
    
    return m

def plot_opm(m, cmap='hsv', title='Preferred orientation'):
    """ Plot an orientation preference map m.
    
    Args:
        m: orientation preference map. If complex, it is treated like a complex OPM. 
            If real, it is treated like the argument of a complex OPM (the angle, assumed to be between -pi and pi).
        cmap: a matplotlib color map
        
    Returns:
        f, ax: figure and axes of the plot
    """
    
    if np.iscomplex(m).any():
        # compute the preferred orientation (argument)
        # and scale -> theta [0, 180]
        theta = 0.5 * (np.angle(m) + np.pi)
    else:
        theta = m
    
    f, ax = plt.subplots()

    # plot data and adjust axes
    im = ax.imshow(theta, cmap=cmap)
    im.set_clim(0, np.pi)
    loc = np.linspace(0, np.pi, 5) 
    
    # label axes
    labels = ['0', r'$\pi / 4$', r'$\pi / 2$', r'$3 \pi / 4$', r'$\pi$']
    cb = f.colorbar(im, ax=ax)
    cb.set_ticks(loc)
    cb.set_ticklabels(labels)
    ax.set_xticks([])
    ax.set_yticks([])
    
    ax.set_title(title)

    return f, ax

def plot_amplitude_map(m, cmap='jet', title='Amplitude'):
    """ Plot the amplitude of an orientation preference map m.
    
    Args:
        m: orientation preference map. If complex, it is treated like a complex OPM. 
            If real, it is treated like the absolute value of a complex OPM (the angle, assumed to be between -pi and pi).
        cmap: a matplotlib color map
        
    Returns:
        f, ax: figure and axes of the plot
    
    """
    
    if np.iscomplex(m).any():
        # compute the modulus of the orientation map
        A = np.abs(m)
    else:
        A = m
        
    f, ax = plt.subplots()

    im = ax.imshow(A, cmap=cmap)
    

    cb = f.colorbar(im, ax=ax)

    ax.set_xticks([])
    ax.set_yticks([])
    
    ax.set_title(title)

    return f, ax

def get_indices(size):
    """ Given the size of an OPM, compute the indices of the pixels
    
    Args:
        size: size of the orientation preference map, either scalar (square OPM) or tuple (rectangular OPM)
    
    Returns:
        An npixels x 2 matrix, where the kth row contains the x and y coordinates of the kth pixel
    """
    
    if isinstance(size, int):
        sx, sy = size, size
    else:
        sx, sy = size
        
    X, Y = np.meshgrid(np.arange(sx), np.arange(sy))
    indices = np.vstack((X.flatten(), Y.flatten())).T
    
    return indices

def calculate_map(responses, stimuli, size=None):
    """ Compute OPM components from an experiment (max likelihood solution)
    
    Args:
        responses: N x n array
        stimuli: N x d array
        size: (n_x, n_y) shape of result, defaults to (sqrt(n), sqrt(n))
        
    Returns: estimated map components: d x n_x x n_y array 
    """
    V = stimuli
    d = V.shape[1]
    R = responses
    
    # least squares estimate of real and imaginary components of the map
    M_flat = np.linalg.inv(V.T @ V) @ V.T @ R

    # get size to reshape map, defaults to square map
    if not size:
        size = int(np.round(np.sqrt(R.shape[1])))
        size = (size, size)
        
    # reshape map into three
    M = np.zeros((d, *size))
    for i, a in enumerate(M_flat):
        M[i] = a.reshape(*size)
        
    return M
    