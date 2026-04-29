# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 11:10:47 2026

@author: VSRS-ladm
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# --- Constants ---
NA1 = 0.2       # Numerical Aperture of reference SMA fibre
d1 = 0.2        # Diameter of reference SMA fibre in [mm]
NA2 = 0.22      # Numerical Aperture of one Fibre from the bundle
d2 = 0.113      # Diameter of one fibre from the bundle in [mm]

IT_ref = 9134.688      # Integration time of reference in [ms]
IT_mes = 9134.688      # Integration time of fibre measurements in [ms]

# Ettendue
E = ((d1 * NA1) ** 2) / ((d2 * NA2) ** 2)

# Correction of integration time
IT_div = IT_ref / IT_mes
cor = E * IT_div

# Maximum ADC count for a 16-bit operating system
adc = 65535

# --- Total Link Loss ---
attenuation_632_8 = 10  # dB/km

# Reference setup: SMA fiber
fiber_length_ref = 2 * 10**-3
connector_pairs_ref = 0
connector_loss_ref = 0
number_splices_ref = 0
splice_loss_ref = 0

# Measurement setup: Fiber bundle
fiber_length = 66 * 10**-3
connector_pairs = 1
connector_loss = 0
number_splices = 0
splice_loss = 0.0

# Link loss for reference setup
attenuation_loss_ref = attenuation_632_8 * fiber_length_ref
tll_ref = attenuation_loss_ref + connector_loss_ref + splice_loss_ref

# Link loss for measurement setup
attenuation_loss = attenuation_632_8 * fiber_length
tll = attenuation_loss + connector_loss + splice_loss

# --- Data Loading and Preprocessing ---
def load_data(file_path):
    data = pd.read_csv(
        file_path,
        sep=';',
        skiprows=9,
        names=['Wavelength [nm]', 'Sample [counts]', 'Dark [counts]',
               'Reference [counts]', 'Dark Corrected [counts]']
    )
    data['Corrected Counts'] = data['Dark Corrected [counts]'] * cor
    return data

def preprocess_data(data):
    data['Corrected Counts'] = data['Dark Corrected [counts]'] * cor #*2
    data['Corrected dB'] = 20 * np.log10(data['Corrected Counts'] / adc)
    data['Corrected dB'] += tll
    data['Final Corrected Counts'] = adc * 10**(data['Corrected dB'] / 20)
    return data

# --- Plotting Functions ---
def plot_raw_vs_corrected(start_fiber, end_fiber):
    plt.figure(figsize=(12, 8))
    for fiber_num in range(start_fiber, end_fiber + 1):
        file_path = f'C:\\Users\\VSRS-ladm\\Avantes\\AvaSoft8\\fibre {fiber_num:02d} (OSL2) 260407.txt'
        try:
            data = load_data(file_path)
            plt.plot(
                data['Wavelength [nm]'],
                data['Dark Corrected [counts]'],
                color='blue', alpha=0.3,
                label='Raw' if fiber_num == start_fiber else ""
            )
            plt.plot(
                data['Wavelength [nm]'],
                data['Corrected Counts'],
                label=f'Fiber {fiber_num:02d}'
            )
        except FileNotFoundError:
            print(f"File {file_path} not found. Skipping...")
    plt.xlabel('Wavelength [nm]')
    plt.ylabel('Counts')
    plt.title('Spectrometer Data: Dark Corrected')
    plt.grid(True)
    plt.show()

def plot_final_corrected_counts(start_fiber, end_fiber):
    plt.figure(figsize=(12, 8))
    ref_data = load_data(r'C:\Users\VSRS-ladm\Avantes\AvaSoft8\reference light (OSL2) 260407 SMA.txt')
    ref_data['Corrected dB'] = 20 * np.log10(ref_data['Dark Corrected [counts]'] / adc)
    ref_data['Corrected dB'] += tll_ref
    ref_data['Final Corrected Counts'] = adc * 10**(ref_data['Corrected dB'] / 20)
    plt.plot(
        ref_data['Wavelength [nm]'],
        ref_data['Final Corrected Counts'],
        label='Reference (SMA)', color='red', linewidth=2
    )
    for fiber_num in range(start_fiber, end_fiber + 1):
        file_path = f'C:\\Users\\VSRS-ladm\\Avantes\\AvaSoft8\\fibre {fiber_num:02d} (OSL2) 260407.txt'
        try:
            data = load_data(file_path)
            data['Corrected Counts'] = data['Dark Corrected [counts]'] * cor
            data = preprocess_data(data)
            plt.plot(
                data['Wavelength [nm]'],
                data['Final Corrected Counts'],
                alpha=0.7, label=''
            )
        except FileNotFoundError:
            print(f"File {file_path} not found. Skipping...")
    plt.xlabel('Wavelength [nm]')
    plt.ylabel('Counts (ADC)')
    plt.title('Spectrometer Data: Final Corrected Counts (ADC Range)')
    # plt.legend()
    plt.grid(True)
    plt.show()

def plot_transmission(start_fiber, end_fiber):
    plt.figure(figsize=(20, 16))
    ref_data = load_data(r'C:\Users\VSRS-ladm\\Avantes\\AvaSoft8\\reference light (OSL2) 260407 SMA.txt')
    ref_data['Corrected dB'] = 20 * np.log10(ref_data['Dark Corrected [counts]'] / adc)
    ref_data['Corrected dB'] += tll_ref
    ref_data['Final Corrected Counts'] = adc * 10**(ref_data['Corrected dB'] / 20)
    manufacturer_df = pd.read_excel(
        r'C:\Users\VSRS-ladm\Avantes\AvaSoft8\manufacturer measurment.xlsx',
        engine='openpyxl'
    )
    manufacturer_transmission = {
        500: manufacturer_df.iloc[4:64, 2].fillna(0).values,
        600: manufacturer_df.iloc[4:64, 4].fillna(0).values,
        632.8: manufacturer_df.iloc[4:64, 9].fillna(0).values,
        700: manufacturer_df.iloc[4:64, 6].fillna(0).values,
    }
    wavelengths_of_interest = [500, 600, 632.8, 700]
    for fiber_num in range(start_fiber, end_fiber + 1):
        file_path = f'C:\\Users\\VSRS-ladm\\Avantes\\AvaSoft8\\fibre {fiber_num:02d} (OSL2) 260407.txt'
        try:
            data = load_data(file_path)
            data['Corrected Counts'] = data['Dark Corrected [counts]'] * cor
            data = preprocess_data(data)
            transmission = (data['Final Corrected Counts'] / ref_data['Final Corrected Counts']) * 100 #*2
            transmission_percentage = np.clip(transmission, 0, 120)
            color = plt.cm.viridis((fiber_num - start_fiber) / (end_fiber - start_fiber))
            plt.plot(
                data['Wavelength [nm]'],
                transmission_percentage,
                color=color, alpha=0.7,
                label=f'Fiber {fiber_num:02d}' if fiber_num == start_fiber else ""
            )
            for wl in wavelengths_of_interest:
                if (fiber_num - 1) < len(manufacturer_transmission[wl]):  # Check bounds
                    manufacturer_value = manufacturer_transmission[wl][fiber_num - 1] * 100
                    idx = np.argmin(np.abs(data['Wavelength [nm]'] - wl))
                    plt.scatter(
                        data['Wavelength [nm]'].iloc[idx],
                        manufacturer_value,
                        color='black', marker='x', s=100,
                        label=f'Manufacturer {wl} nm' if wl == 500 and fiber_num == start_fiber else ""
                    )
        except FileNotFoundError:
            print(f"File {file_path} not found. Skipping...")
    plt.xlabel('Wavelength [nm]')
    plt.ylabel('Transmission [%]')
    plt.title('Fiber Transmission Relative to Reference')
    # plt.legend()
    plt.grid(True)
    plt.show()


# --- Save Transmission Data to CSV ---
def save_transmission_data(start_fiber, end_fiber):
    # Use the directory of your data files
    data_dir = r'C:\Users\VSRS-ladm\Avantes\AvaSoft8'

    transmission_data = {}
    ref_data = load_data(os.path.join(data_dir, 'reference light (OSL2) 260407 SMA.txt'))
    ref_data['Corrected dB'] = 20 * np.log10(ref_data['Dark Corrected [counts]'] / adc)
    ref_data['Corrected dB'] += tll_ref
    ref_data['Final Corrected Counts'] = adc * 10**(ref_data['Corrected dB'] / 20)

    for fiber_num in range(start_fiber, end_fiber + 1):
        file_path = os.path.join(data_dir, f'fibre {fiber_num:02d} (OSL2) 260407.txt')
        try:
            data = load_data(file_path)
            data['Corrected Counts'] = data['Dark Corrected [counts]'] * cor
            data = preprocess_data(data)
            transmission = (data['Final Corrected Counts'] / ref_data['Final Corrected Counts']) * 100
            transmission_percentage = np.clip(transmission, 0, 120)
            transmission_data[f'Fiber {fiber_num:02d}'] = transmission_percentage
        except FileNotFoundError:
            print(f"File {file_path} not found. Skipping...")

    # Save to CSV in the same directory
    output_path = os.path.join(data_dir, 'fiber_transmissions.csv')
    pd.DataFrame(transmission_data).to_csv(output_path, index=False)
    print(f"Transmission data saved to: {output_path}")

# --- Main Execution ---
if __name__ == "__main__":
    start_fiber = 1
    end_fiber = 61

    plot_raw_vs_corrected(start_fiber, end_fiber)
    plot_final_corrected_counts(start_fiber, end_fiber)
    plot_transmission(start_fiber, end_fiber)
    save_transmission_data(start_fiber, end_fiber)
    
    
# def plot_corrected_dB(start_fiber, end_fiber):
#     plt.figure(figsize=(12, 8))
#     for fiber_num in range(start_fiber, end_fiber + 1):
#         file_path = f'C:\\Users\\VSRS-ladm\\Avantes\\AvaSoft8\\fibre {fiber_num:02d} (OSL2) 260407.txt'
#         try:
#             data = load_data(file_path)
#             data['Corrected Counts'] = data['Dark Corrected [counts]'] * cor
#             data['Corrected dB'] = 20 * -np.log10(data['Corrected Counts']/adc)
#             data['Corrected dB'] += tll
#             plt.plot(
#                 data['Wavelength [nm]'],
#                 data['Corrected dB'],
#                 label=f'Fiber {fiber_num:02d}'
#             )
#         except FileNotFoundError:
#             print(f"File {file_path} not found. Skipping...")
#     plt.xlabel('Wavelength [nm]')
#     plt.ylabel('Corrected Signal [dB]')
#     plt.title('Spectrometer Data: Corrected Signal in dB')
#     plt.grid(True)
#     # plt.legend()
#     plt.show()

# # Call the function
# plot_corrected_dB(start_fiber, end_fiber)