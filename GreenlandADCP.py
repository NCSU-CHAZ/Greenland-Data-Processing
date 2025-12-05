# load in necessary packages
import pandas as pd
import numpy as np
import datetime
import scipy.io as spio
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# load in data
filepath = r"/Users/KatherineAnardeWheels/PycharmProjects/Greenland-Data-Processing/104505_20230722T124546UTC_Data_15ppt_50percentCorrelation_90depth/104505_20230722T124546UTC.mat"
# filepath = r"/Users/KatherineAnardeWheels/PycharmProjects/Greenland-Data-Processing/104505_20230722T124546UTC_Data_15ppt_50percentCorrelation_100depth/104505_20230722T124546UTC.mat"

##This part was written by AI but converts the subtructures from the .mat file to a python dictionary

def loadmat_recursive(filename):
    """
    Recursively loads a .mat file, converting MATLAB objects to Python dictionaries.
    """

    def _check_keys(d):
        """Checks if entries in dictionary are mat-objects and converts them accordingly."""
        for key in d:
            if isinstance(d[key], spio.matlab.mat_struct):
                d[key] = _todict(d[key])
            elif isinstance(d[key], np.ndarray):
                d[key] = _tolist(d[key])
        return d

    def _todict(matobj):
        """Converts a mat-object to a dictionary."""
        d = {}
        for strg in matobj._fieldnames:
            elem = matobj.__dict__[strg]
            if isinstance(elem, spio.matlab.mat_struct):
                d[strg] = _todict(elem)
            elif isinstance(elem, np.ndarray):
                d[strg] = _tolist(elem)
            else:
                d[strg] = elem
        return d

    def _tolist(ndarray):
        """Converts a numpy array to a list, handling nested mat-objects."""
        elem_list = []
        for elem in ndarray:
            if isinstance(elem, spio.matlab.mat_struct):
                elem_list.append(_todict(elem))
            elif isinstance(elem, np.ndarray):
                elem_list.append(_tolist(elem))
            else:
                elem_list.append(elem)
        return elem_list

    # Use the function by calling it instead of direct spio.loadmat
    data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_keys(data)

# Example usage of the function
data = loadmat_recursive(filepath)
# result = mat_data['main_structure_name']['sub_structure_1']['data_field_name']
# data['A']['Nav']['timestamp']

current = pd.DataFrame(data['A']['Wat']['vMag_ms'])  # .fillna(0)
print(current.shape)
# current = current.iloc[:, :-1]

# depth_nonan = pd.DataFrame(data['A']['Nav']['depth'])  # .fillna(0) # fill NaNs with zeros for plotting
# depthmax = depth_nonan.max().max()  # grab maximum depth for plotting
# print(depthmax)
# print(depth_nonan.shape)

depth = pd.DataFrame(data['A']['Wat']['binDepth'])  # .fillna(0) # fill NaNs with zeros for plotting
ds_depth = pd.DataFrame(data['A']['Nav']['dsDepth'])  # .fillna(0) # fill NaNs with zeros for plotting
# ds_depth = pd.DataFrame(data['A']['Sup']['altimeter_depth'])  # .fillna(0) # fill NaNs with zeros for plotting
ninety_percent_max_depth = depth.max()

print(depth.shape)
depthmin = int(depth.min().min())  # grab maximum depth for plotting
num_bins = int(data['A']['Sup']['bins'][0])
bin_size = int(data['A']['Sup']['binSize_m'][0])
bin_depth = list(range(depthmin, depthmin + num_bins, bin_size))

# Function to convert matlab timestamp to regular datetime in UTC
def dtnum_dttime_adcp(datenum_array):
    dates = []
    for datenum in datenum_array:
        python_datetime = datetime.fromordinal((int(datenum))) + timedelta(days=(datenum) % 1) - timedelta(days=366)
        dates.append(python_datetime)
    return dates

timestamp = dtnum_dttime_adcp(data['A']['Nav']['timestamp'])
# print(timestamp)
# print(type(timestamp))

# window time series
df = pd.DataFrame({
    'value': timestamp
}, index=pd.to_datetime(timestamp))

target_date_start = datetime(2023, 7, 22, 13, 6)
target_date_end = datetime(2023, 7, 22, 13, 22)

# Get the indexer for the nearest datetime
iloc_idx_start = df.index.get_indexer([target_date_start], method='nearest')
iloc_idx_end = df.index.get_indexer([target_date_end], method='nearest')

fig, ax = plt.subplots(figsize=(12, 3))
plt.pcolormesh(
    timestamp[int(iloc_idx_start):int(iloc_idx_end)],
    bin_depth,
    current.iloc[:,int(iloc_idx_start):int(iloc_idx_end)] ,
    cmap='plasma',
    shading='gouraud',
    vmin=0,
    vmax=1.6
)
plt.ylim([2,75])
plt.xlabel("Time (UTC)")
plt.ylabel("Depth (m)")
im1 = plt.colorbar()
im1.ax.set_ylabel("Velocity (m/s)")
plt.gca().invert_yaxis()
ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.show()
plt.plot(timestamp[int(iloc_idx_start):int(iloc_idx_end)], ds_depth[int(iloc_idx_start):int(iloc_idx_end)],
         color='black', linewidth=1, label='Depth')
plt.plot(timestamp[int(iloc_idx_start):int(iloc_idx_end)],
         ninety_percent_max_depth[int(iloc_idx_start):int(iloc_idx_end)], color='black', linestyle='dashed',
         linewidth=1,  label='90% Depth')
plt.legend()

plt.savefig("90_jet.pdf")

# plot 90% depth and full depth
fig, ax = plt.subplots(figsize=(12, 3))
plt.plot()



