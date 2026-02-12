import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from sklearn.metrics import r2_score, root_mean_squared_error
from matplotlib.cm import ScalarMappable
from scipy import stats
import sys
import os

sys.path.append(os.path.abspath(".."))
from data_tools import my_setup

class PlotOzone:

    def __init__(self):
        self.vmin = 0
        self.vmax = 50
        self.temp_norm = Normalize(vmin=self.vmin, vmax=self.vmax)

    def plot(self, data, sensor_id, period, calibration, color_by='temperature'):
        """
        color_by: 'temperature' (default) or 'date'
        """
        fig, ax = plt.subplots(figsize=(7,6))
        imagefolder = my_setup.local_image_folder("Ozone","")

        if "o3_calibrated" in data.columns:
            self._add_to_plots("o3_calibrated", f"{sensor_id}", ax, data, color_by)
            if color_by == 'date':
                plt.savefig(rf"{imagefolder}{sensor_id}/{period}{calibration}PreVsPostTrainingData.jpg", format='jpg', dpi=300)
            else:
                plt.savefig(rf"{imagefolder}{sensor_id}/{period}{calibration}CalibratedStats.jpg", format='jpg', dpi=300)

        # if(period == "All"):
        #     fig, ax = plt.subplots(figsize=(7,6))
        #     self._add_to_plots("o3","Raw Ozone", ax, data, color_by)
        #     plt.savefig(rf"{imagefolder}{sensor_id}/RawStats.jpg", format='jpg', dpi=300)

    def _add_to_plots(self, model, name, ax, data, color_by='temperature'):
        x = data['reference']
        y = data[model]

        # Determine colors based on color_by parameter
        if color_by == 'date':
            # Date-based coloring
            dates = pd.to_datetime(data.index)  # or pd.to_datetime(data['your_date_column'])
            august_cutoff = pd.Timestamp('2025-08-01')  # Adjust year as needed
            colors = ['red' if date < august_cutoff else 'blue' for date in dates]
            
            ax.scatter(x, y, c=colors, alpha=0.6, s=5)
            
            # Add legend for date colors
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='red', alpha=0.6, label='Pre-Field'),
                Patch(facecolor='blue', alpha=0.6, label='Post-Field')
            ]
            ax.legend(handles=legend_elements, loc='lower right', fontsize=10)
            
        else:  # default to temperature
            # Temperature-based coloring (original)
            ax.scatter(
                x,
                y,
                c=data['temp_C'],
                cmap='RdBu_r',
                norm=self.temp_norm,
                alpha=1,
                s=5
            )
            
            # Colorbar
            sm = ScalarMappable(cmap='RdBu_r', norm=self.temp_norm)
            sm.set_array([])
            ticks = np.arange(self.vmin, self.vmax + 1, 5)
            cbar = plt.colorbar(sm, ax=ax, ticks=ticks)
            cbar.set_ticklabels([str(t) for t in ticks])
            cbar.set_label('Ambient Temp [C]', fontsize=12)

            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            y_fit = slope * x + intercept

            ax.plot(x, y_fit, c='red', label='Best fit')
            ax.text(0.55, 0.03, f'y = {slope:.2f}x + {intercept:.2f}',transform=ax.transAxes, fontsize=13, verticalalignment='bottom')

        # Add 1:1 line
        ax.plot([0, 100], [0, 100], c='black', linestyle='--', label='1:1')

        # Metrics
        r2, rmse, mbe, nmb, nme = self._calculate_metrics(data['reference'], data[model])
        ax.text(0.05, 0.95, f'R\u00b2 = {r2:.2f}', transform=ax.transAxes, fontsize=13, verticalalignment='top')
        ax.text(0.05, 0.87, f'RMSE = {rmse:.2f}', transform=ax.transAxes, fontsize=13, verticalalignment='top')
        ax.text(0.05, 0.80, f'MBE = {mbe:.2f}', transform=ax.transAxes, fontsize=13, verticalalignment='top')
        ax.text(0.05, 0.73, f'NMB = {nmb:.2%}', transform=ax.transAxes, fontsize=13, verticalalignment='top')
        ax.text(0.05, 0.66, f'NME = {nme:.2%}', transform=ax.transAxes, fontsize=13, verticalalignment='top')
        ax.text(0.05, 0.59, f'Data Points = {len(data)}', transform=ax.transAxes, fontsize=13, verticalalignment='top')

        # Titles & labels
        # ax.set_title(f'{name}', fontsize=14)
        ax.set_xlabel('Reference O3 (ppb)', fontsize=14)
        ax.set_ylabel(f'Calibrated O3 (ppb)', fontsize=14)
        ax.set_aspect('equal', adjustable='box')

        ax.set_xlim(0, 90)
        ax.set_ylim(0, 90)


    def _calculate_metrics(self, observed, predicted):
        r2 = r2_score(observed, predicted)
        rmse = root_mean_squared_error(observed, predicted)
        mbe = (predicted - observed).mean()
    
        # Calculate percentage errors, handling division by zero
        nmb = np.nanmean(np.divide(predicted - observed, observed, out=np.zeros_like(predicted - observed), where=observed!=0))
        nme = np.nanmean(np.divide(abs(predicted - observed), observed, out=np.zeros_like(abs(predicted - observed)), where=observed!=0))
        
        return r2, rmse, mbe, nmb, nme
    
    def plot_two_models(self, data, sensor_id, calibration1, calibration2, model1_col, model2_col):
        """
        Plot two calibration models against reference values with different colors.
        
        Parameters:
        - data: DataFrame containing the data
        - sensor_id: sensor identifier
        - calibration1: label for first calibration method
        - calibration2: label for second calibration method
        - model1_col: column name for first calibrated values (e.g., 'o3_calibrated_model1')
        - model2_col: column name for second calibrated values (e.g., 'o3_calibrated_model2')
        """
        fig, ax = plt.subplots(figsize=(7, 6))
        imagefolder = my_setup.local_image_folder("Ozone", "")
        
        # Define colors for each model
        color1 = 'blue'
        color2 = 'red'
        
        # Plot first model
        if model1_col in data.columns:
            x1 = data['reference']
            y1 = data[model1_col]
            ax.scatter(x1, y1, c=color1, alpha=0.6, s=5, label=calibration1)
            
            # Calculate metrics for model 1
            r2_1, rmse_1, mbe_1, nmb_1, nme_1 = self._calculate_metrics(data['reference'], data[model1_col])
        
        # Plot second model
        if model2_col in data.columns:
            x2 = data['reference']
            y2 = data[model2_col]
            ax.scatter(x2, y2, c=color2, alpha=0.6, s=5, label=calibration2)
            
            # Calculate metrics for model 2
            r2_2, rmse_2, mbe_2, nmb_2, nme_2 = self._calculate_metrics(data['reference'], data[model2_col])
        
        # Add 1:1 line
        ax.plot([0, 100], [0, 100], c='black', linestyle='--', label='')
        
        # Display metrics for both models
        r21 = r2_score(data[model1_col], data['reference'])
        r22 = r2_score(data[model2_col], data['reference'])
        rmse1 = root_mean_squared_error(data[model1_col], data['reference'])
        rmse2 = root_mean_squared_error(data[model2_col], data['reference'])
        mbe1 = (data['reference'] - data[model1_col]).mean()
        mbe2 = (data['reference'] - data[model2_col]).mean()
        ax.text(0.03, 0.95, f'R\u00b2 = {r21:.2f},', transform=ax.transAxes, fontsize=10, color=color1, verticalalignment='top')
        ax.text(0.03, 0.9, f'R\u00b2 = {r22:.2f},', transform=ax.transAxes, fontsize=10, color=color2, verticalalignment='top')
        ax.text(0.2, 0.95, f'RMSE = {rmse1:.2f},', transform=ax.transAxes, fontsize=10, color=color1, verticalalignment='top')
        ax.text(0.2, 0.9, f'RMSE = {rmse2:.2f},', transform=ax.transAxes, fontsize=10, color=color2, verticalalignment='top')
        ax.text(0.415, 0.95, f'MBE = {mbe1:.2f}', transform=ax.transAxes, fontsize=10, color=color1, verticalalignment='top')
        ax.text(0.415, 0.9, f'MBE = {mbe2:.2f}', transform=ax.transAxes, fontsize=10, color=color2, verticalalignment='top')
        
        ax.text(0.15, 0.025, f'Data Points = {len(data)}', transform=ax.transAxes, fontsize=13, verticalalignment='bottom')
        
        # Titles & labels
        # ax.set_title(f'{sensor_id} - With and Without Post-Field Calibration', fontsize=14)
        ax.set_xlabel('Reference O3 (ppb)', fontsize=14)
        ax.set_ylabel(f'Calibrated O3 (ppb)', fontsize=14)
        ax.legend(loc='lower right', fontsize=10)
        
        ax.set_xlim(0, 90)
        ax.set_ylim(0, 90)
        ax.set_aspect('equal', adjustable='box')
        
        plt.savefig(rf"{imagefolder}{sensor_id}/WithandWithoutPostField.jpg", 
                    format='jpg', dpi=300)
class PlotPlantower:

    def __init__(self):
        self.vmin = 0
        self.vmax = 50
        self.temp_norm = Normalize(vmin=self.vmin, vmax=self.vmax)

    def plot(self, data, sensor_id,period,calibration):
        # Set up 2x2 grid of subplots
        fig, axs = plt.subplots(2, 2, figsize=(14,12))
        fig.suptitle(f"{period} Data: {sensor_id} Calibration Model Comparison\n", fontsize=18)
        fig.text(0.5, 0.945, f"{calibration} Calibration", ha='center', fontsize=12, fontstyle='italic')
        fig.text(0.5, 0.92, "Unit-Specific Models", ha='center', fontsize=14, fontweight='bold')
        fig.subplots_adjust(hspace=0.3)  # increase vertical space between rows
        fig.text(0.5,0.48,"Universal Models", ha='center', fontsize=14, fontweight='bold' )

        self._add_to_plots(0,0,'pm_calibrated_clarityremake', 'Clarity v2 Variables - PM10', axs, data)
        self._add_to_plots(0,1,'pm_calibrated_twovar', 'RH + PM2.5', axs, data)
        self._add_to_plots(1,1,'pm_calibrated_epa_barkjohn', 'EPA Barkjohn 2021', axs, data)
        self._add_to_plots(1,0,'pm_calibrated_clarity', 'Clarity v2', axs, data)
        imagefolder = my_setup.local_image_folder("PM","Plantower")
        plt.savefig(rf"{imagefolder}{sensor_id}/{period}{calibration}CalibrationStatswEPA.jpg", format='jpg', dpi=300)

        fig, ax = plt.subplots(figsize=(7,6))
        self._add_to_plots(0,0,'m_PM25_CF1', 'Raw Plantower CF1', ax, data)  # pass ax instead of axs grid
        plt.savefig(rf"{imagefolder}{sensor_id}/RawStats.jpg", format='jpg', dpi=300)


    def _add_to_plots(self, i, j, model, name, axs, data):
    # If axs is a 2D array (grid)
        if isinstance(axs, np.ndarray):
            ax = axs[i, j]
        else:
            ax = axs  # single subplot case

        x = data['reference']
        y = data[model]

        ax.scatter(
            x,
            y,
            c=data['temp_C'],
            cmap='RdBu_r',
            norm=self.temp_norm,
            alpha=1,
            s=5
        )

        # Add 1:1 line
        ax.plot([0, 100], [0, 100], c='black', linestyle='--', label='1:1')

        # Line of best fit
        # slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        # y_fit = slope * x + intercept
        # ax.plot(x, y_fit, c = 'red', label = 'Best fit')
        # ax.text(0.55, 0.03, f'y = {slope:.2f}x + {intercept:.2f}',transform=ax.transAxes, fontsize=13, verticalalignment='bottom')

        # Metrics
        r2, rmse, mbe, nmb, nme = self._calculate_metrics(data['reference'], data[model])
        ax.text(0.1, 0.95, f'R\u00b2 = {r2:.2f}', transform=ax.transAxes, fontsize=13, verticalalignment='top')
        ax.text(0.1, 0.87, f'RMSE = {rmse:.2f}', transform=ax.transAxes, fontsize=13, verticalalignment='top')
        ax.text(0.1, 0.80, f'MBE = {mbe:.2f}', transform=ax.transAxes, fontsize=13, verticalalignment='top')
        ax.text(0.1, 0.73, f'NMB = {nmb:.2%}', transform=ax.transAxes, fontsize=13, verticalalignment='top')
        ax.text(0.1, 0.66, f'NME = {nme:.2%}', transform=ax.transAxes, fontsize=13, verticalalignment='top')
        ax.text(0.1, 0.59, f'Data Points = {len(data)}', transform=ax.transAxes, fontsize=13, verticalalignment='top')

        # Colorbar
        sm = ScalarMappable(cmap='RdBu_r', norm=self.temp_norm)
        sm.set_array([])
        ticks = np.arange(self.vmin, self.vmax + 1, 5)
        cbar = plt.colorbar(sm, ax=ax, ticks=ticks)
        cbar.set_ticklabels([str(t) for t in ticks])
        cbar.set_label('Ambient Temp [C]', fontsize=12)

        # Titles & labels
        ax.set_title(f'{name}', fontsize=14)
        ax.set_xlabel('Reference PM (ug/m3)', fontsize=14)
        ax.set_ylabel(f'Calibrated PM (ug/m3)', fontsize=14)

        ax.set_xlim(0, 65)
        ax.set_ylim(0, 65)

    # Function to calculate metrics
    def _calculate_metrics(self, observed, predicted):
        r2 = r2_score(observed, predicted)
        rmse = root_mean_squared_error(observed, predicted)
        mbe = (predicted - observed).mean()
        
        # Calculate percentage errors, handling division by zero
        nmb = np.nanmean(np.divide(predicted - observed, observed, out=np.zeros_like(predicted - observed), where=observed!=0))
        nme = np.nanmean(np.divide(abs(predicted - observed), observed, out=np.zeros_like(abs(predicted - observed)), where=observed!=0))
        
        return r2, rmse, mbe, nmb, nme

class PlotSensirion:
    def __init__(self):
        self.vmin = 0
        self.vmax = 60
        self.temp_norm = Normalize(vmin=self.vmin, vmax=self.vmax)

    def plot(self, data, sensor_id,period,calibration):
        # Set up 1x3 grid of subplots
        fig, axs = plt.subplots(1, 3, figsize=(18,6))
        fig.suptitle(f"{period} Data: {sensor_id} Calibration Model Comparison\n", fontsize=16)
        fig.text(0.5, 0.915, f"{calibration} Calibration", ha='center', fontsize=12, fontstyle='italic')
        plt.subplots_adjust(top=0.82)
        fig.subplots_adjust(hspace=0.3)  # increase vertical space between rows
        self._add_to_plots(2,'pm_calibrated_clarityremake', 'Clarity v2 Variables - PM10', axs, data)
        self._add_to_plots(1,'pm_calibrated_twovar', 'RH + PM2.5', axs, data)
        self._add_to_plots(0,'m_PM25_b', 'Raw Data', axs, data)
        imagefolder = my_setup.local_image_folder("PM","Sensirion")
        plt.savefig(rf"{imagefolder}{sensor_id}/{period}{calibration}CalibrationStats.jpg", format='jpg', dpi=300)

    def _add_to_plots(self, i, model, name, axs, data):
    # If axs is a 2D array (grid)
        if isinstance(axs, np.ndarray):
            ax = axs[i]
        else:
            ax = axs  # single subplot case

        x = data['reference']
        y = data[model]

        ax.scatter(
            x,
            y,
            c=data['temp_C'],
            cmap='RdBu_r',
            norm=self.temp_norm,
            alpha=0.8,
            s=5
        )

        # Add 1:1 line
        ax.plot([0, 100], [0, 100], c='black', linestyle='--', label='1:1')

        # Line of best fit
        # slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        # y_fit = slope * x + intercept
        # ax.plot(x, y_fit, c = 'red', label = 'Best fit')
        # ax.text(0.55, 0.03, f'y = {slope:.2f}x + {intercept:.2f}',transform=ax.transAxes, fontsize=11, verticalalignment='bottom')

        # Metrics
        r2, rmse, mbe, nmb, nme = self._calculate_metrics(data['reference'], data[model])
        ax.text(0.1, 0.95, f'R\u00b2 = {r2:.2f}', transform=ax.transAxes, fontsize=11, verticalalignment='top')
        ax.text(0.1, 0.87, f'RMSE = {rmse:.2f}', transform=ax.transAxes, fontsize=11, verticalalignment='top')
        ax.text(0.1, 0.80, f'MBE = {mbe:.2f}', transform=ax.transAxes, fontsize=11, verticalalignment='top')
        ax.text(0.1, 0.73, f'NMB = {nmb:.2%}', transform=ax.transAxes, fontsize=11, verticalalignment='top')
        ax.text(0.1, 0.66, f'NME = {nme:.2%}', transform=ax.transAxes, fontsize=11, verticalalignment='top')
        ax.text(0.1, 0.59, f'Data Points = {len(data)}', transform=ax.transAxes, fontsize=11, verticalalignment='top')

        # Colorbar
        sm = ScalarMappable(cmap='RdBu_r', norm=self.temp_norm)
        sm.set_array([])
        ticks = np.arange(self.vmin, self.vmax + 1, 5)
        cbar = plt.colorbar(sm, ax=ax, ticks=ticks)
        cbar.set_ticklabels([str(t) for t in ticks])
        cbar.set_label('Ambient Temp [C]', fontsize=12)

        # Titles & labels
        ax.set_title(f'{name}', fontsize=14)
        ax.set_xlabel('Reference PM (ug/m3)', fontsize=14)
        ax.set_ylabel(f'Calibrated PM (ug/m3)', fontsize=14)

        ax.set_xlim(0, 80)
        ax.set_ylim(0, 80)

    # Function to calculate metrics
    def _calculate_metrics(self, observed, predicted):
        r2 = r2_score(observed, predicted)
        rmse = root_mean_squared_error(observed, predicted)
        mbe = (predicted - observed).mean()
        
        # Calculate percentage errors, handling division by zero
        nmb = np.nanmean(np.divide(predicted - observed, observed, out=np.zeros_like(predicted - observed), where=observed!=0))
        nme = np.nanmean(np.divide(abs(predicted - observed), observed, out=np.zeros_like(abs(predicted - observed)), where=observed!=0))
        
        return r2, rmse, mbe, nmb, nme
    

from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib.dates as mdates
import pandas as pd
import matplotlib as mpl

def timeseries(timeseries, start_date, end_date, variable, sensor=""):

    mpl.rcParams['font.family'] = 'Arial'        # your preferred font
    mpl.rcParams['font.size'] = 12               # default size
    mpl.rcParams['xtick.labelsize'] = 12
    mpl.rcParams['ytick.labelsize'] = 12
    mpl.rcParams['axes.labelsize'] = 14
    fig,ax = plt.subplots(figsize=(12, 6))

    plt.fill_between(
        timeseries.index,
        timeseries['ref_mean']-timeseries['ref_2std'],
        timeseries['ref_mean']+timeseries['ref_2std'],
        color='lightgray',
        alpha=0.65,
        label='3 Standard Deviations',
        zorder=1
    )

    # 25th to 75th percentile (dark gray)
    plt.fill_between(
        timeseries.index,
        timeseries['ref_mean']-timeseries['ref_std'],
        timeseries['ref_mean']+timeseries['ref_std'],
        color='darkgray',
        alpha=0.75,
        label='1 Standard Deviation',
        zorder=2
    )

    # Median as a dashed line
    plt.plot(
        timeseries.index,
        timeseries['ref_mean'],
        color='black',
        linestyle='--',
        linewidth=2,
        label='Mean',
        zorder=3
    )

    # plt.fill_between(
    #     timeseries.index,
    #     timeseries['voz_mean']-timeseries['voz_2std'],
    #     timeseries['voz_mean']+timeseries['voz_2std'],
    #     color="#ff7f0e",
    #     alpha=0.15,
    #     label='3 Standard Deviations',
    #     zorder=4
    # )

    # # 25th to 75th percentile (dark gray)
    # plt.fill_between(
    #     timeseries.index,
    #     timeseries['voz_mean']-timeseries['voz_std'],
    #     timeseries['voz_mean']+timeseries['voz_std'],
    #     color="#ff7f0e",
    #     alpha=0.35,
    #     label='1 Standard Deviation',
    #     zorder=5
    # )

    plt.plot(
        timeseries.index,
        timeseries['voz_mean'],
        color="#ff7f0e",
        linewidth=2,
        label='Mean',
        zorder=6
    )

    mean_line_ref = [Line2D([0], [0], color='black', linestyle='--', label='Mean (CARB)')]
    mean_line_voz = [Line2D([0], [0], color='#ff7f0e', linestyle='-', label='Mean (Voz)')]

    if(variable == "Ozone"):
        ax.axhline(y=70, color='red', linestyle='-', linewidth=2, label='High Ozone',zorder=7)
        ax.text(0.12, 0.925, "EPA Health Standard = 70 ppb", transform=ax.transAxes, ha='center', fontsize=12, color = 'red')
        ax.text(0.5, 1.02, "Max Daily 8-Hour Averages - Smoothed", transform=ax.transAxes, ha='center', fontsize=12)
    else:
        ax.axhline(y=9, color='red', linestyle='-', linewidth=2, label='High PM',zorder=7)
        ax.text(0.12, 1.01, "EPA Health Standard = 9 ug/m3", transform=ax.transAxes, ha='center', fontsize=12, color = 'red')

    # --- Patches for standard deviations ---
    ref_patches = [
        Patch(facecolor='gray', label='1 Std (CARB)'),
        Patch(facecolor='lightgray', label='2 Std (CARB)')
    ]

    # voz_patches = [
    #     Patch(facecolor='#ffb347', label='1 Std (Voz)'),
    #     Patch(facecolor='#ffd8b1', label='2 Std (Voz)')
    # ]

    # --- Combine and plot legend ---
    plt.legend(handles=mean_line_ref + mean_line_voz + ref_patches, #+ voz_patches,
            title='',
            loc='upper right',
            frameon=True,
            ncol=2,
            columnspacing=1.5,
            handlelength=2)

    ax.set_title(f"{variable} Timeseries of Voz Monitors vs. CARB References\n", fontsize=14, fontweight = 'bold')
    plt.tight_layout()
    # --- First day of each month within the plot ---
    month_starts = pd.date_range(start=start_date.replace(day=1), end=end_date, freq='MS')
    first_last = pd.DatetimeIndex([start_date, end_date])
    all_ticks = month_starts.union(first_last)
    ax.set_xticks(all_ticks)
    ax.set_yticks([0,10,20,30,40,50,60,70,80,90])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))  # e.g., 'Jun 15'

    # voz_mda8_daily.to_csv("../reference_files/2025OzoneDataCalibrated/AllMDA8Voz.csv")

    # Optional: rotate labels for readability
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    if(variable == "Ozone"):
        ax.set_ylim(0,90)
        plt.ylabel("Ozone [ppb]", fontweight = 'bold')
    else:
        ax.set_ylim(0,70)
        plt.ylabel("PM2.5 [ug/m3]", fontweight = 'bold')
    ax.set_xlim(start_date,end_date)
    plt.tight_layout()
    plt.xlabel("")
    # plt.savefig(rf"../../PlotsForRubenNov25/{sensor}{variable}Timeseries.jpg", format='jpg', dpi=300)
    # plt.show()
